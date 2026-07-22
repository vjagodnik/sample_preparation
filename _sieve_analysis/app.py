from __future__ import annotations

import os

# PyArrow 25 + Python 3.14 under Rosetta can segfault in its bundled Mimalloc
# allocator.  Streamlit uses Arrow internally, so force the macOS system
# allocator before importing Streamlit, Pandas or PyArrow.
os.environ["ARROW_DEFAULT_MEMORY_POOL"] = "system"

from datetime import timedelta
from io import BytesIO

import matplotlib

matplotlib.use("Agg")  # web-safe backend; prevents macOS GUI crashes
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import pyarrow as pa
import streamlit as st

pa.set_memory_pool(pa.system_memory_pool())

from granulometry import (
    HydrometerParameters,
    combined_export,
    hydrometer_analysis,
    parse_hydrometer_file,
    parse_sieve_file,
    passing_at,
    sieve_analysis,
)

st.set_page_config(page_title="Granulometrijska analiza", page_icon="🪨", layout="wide")
st.title("Granulometrijska analiza")
st.caption("Mehaničko prosijavanje, areometriranje i objedinjena granulometrijska krivulja")

with st.expander("Kako pripremiti ulazne podatke", expanded=True):
    st.markdown(
        """
        Aplikacija prihvaća **TXT, TSV, CSV i Excel** datoteke. Decimalni
        separator može biti točka ili zarez. Za tekstualne datoteke preporučuje
        se razdvajanje stupaca tabulatorom.

        #### Mehaničko prosijavanje

        Potrebna su dva stupca:

        1. otvor sita u **mm**
        2. masa zadržana na tom situ u **g**

        Prvi red sadrži zaglavlja. Ukupna masa uzorka unosi se u kućicu
        **„Masa materijala za prosijavanje [g]”** i ne upisuje se kao zaseban
        red u datoteci. Svaki broj u drugom stupcu aplikacija smatra masom
        zadržanom na odgovarajućem situ.
        """
    )
    st.code(
        """Uzorak\tBA_L_1
4\t0.00
2\t0.04
1.18\t0.05
0.8\t0.08
0.6\t0.13
0.425\t0.13
0.2\t0.45
0.15\t2.64
0.1\t37.51
0.063\t42.21""",
        language="text",
    )
    st.markdown(
        """
        Naziv drugog stupca (`BA_L_1` u primjeru) koristi se kao naziv uzorka.
        Otvori sita moraju biti pozitivni. Zbroj zadržanih masa ne smije biti
        veći od unesene ukupne mase uzorka.

        #### Areometriranje

        Potrebna su točno tri stupca:

        - `eltime` — datum i vrijeme očitanja
        - `temp` — temperatura u °C
        - `reading` — očitanje areometra
        """
    )
    st.code(
        """eltime\ttemp\treading
2023-11-08 09:00:00\t19.8\t34
2023-11-08 09:00:30\t19.8\t34
2023-11-08 09:01:00\t19.8\t33
2023-11-08 09:02:00\t19.8\t32.5""",
        language="text",
    )
    st.markdown(
        """
        Preporučeni format vremena je `GGGG-MM-DD HH:MM:SS`. Nakon učitavanja
        treba provjeriti specifičnu gustoću čestica, masu uzorka za
        areometriranje i početak pokusa.

        Kod **pune granulometrijske krivulje** rezultati areometriranja
        automatski se korigiraju prolazom na najfinijem situ iz mehaničkog
        prosijavanja. Kod zasebnog prikaza areometriranje ostaje na vlastitoj
        skali 0–100 %.
        """
    )


def show_preview(data: pd.DataFrame, rows: int = 20) -> None:
    # Avoid st.dataframe/PyArrow: some macOS Python builds can crash in its
    # binary serialization immediately after a file upload.
    st.code(data.head(rows).to_csv(index=False, float_format="%.5g"), language="text")


def plot_curve(series):
    fig, ax = plt.subplots(figsize=(10, 6))
    for x, y, label, marker in series:
        ax.plot(x, y, marker=marker, linewidth=1.8, markersize=5, label=label)
    ax.set_xscale("log")
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 10))
    ax.grid(True, which="both", alpha=0.35)
    ax.set_xlabel("Otvor sita [mm]")
    ax.set_ylabel("Postotak prolaza kroz sito [%]")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:g}"))
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def fig_bytes(fig, fmt: str) -> bytes:
    buffer = BytesIO()
    fig.savefig(buffer, format=fmt, dpi=300, bbox_inches="tight")
    return buffer.getvalue()


tab_sieve, tab_hydro, tab_results = st.tabs(
    ["Mehaničko prosijavanje", "Areometriranje", "Rezultati i izvoz"]
)
sieve_result = hydro_raw = hydro_standalone = None
sample_name = "uzorak"

with tab_sieve:
    left, right = st.columns([2, 1])
    sieve_file = left.file_uploader(
        "Rezultati mehaničkog prosijavanja",
        type=["txt", "csv", "tsv", "xlsx", "xls"],
        key="sieve_file",
    )
    sieve_mass = right.number_input(
        "Masa materijala za prosijavanje [g]", min_value=0.01, value=100.0, step=1.0
    )
    if sieve_file is not None:
        try:
            sample_name, sieve_raw = parse_sieve_file(sieve_file, sieve_file.name)
            sieve_result = sieve_analysis(sieve_raw, sieve_mass)
            st.success(f"Učitan uzorak: {sample_name}")
            if sieve_result["retained_g"].sum() > sieve_mass * 1.005:
                st.warning("Zbroj masa ostataka veći je od unesene mase uzorka. Provjerite podatke.")
            with st.expander("Pregled obrađenih podataka", expanded=True):
                show_preview(sieve_result)
        except Exception as exc:
            st.error(f"Prosijavanje nije obrađeno: {exc}")

with tab_hydro:
    hydro_file = st.file_uploader(
        "Rezultati sedimentacijske analize",
        type=["txt", "csv", "tsv", "xlsx", "xls"],
        key="hydro_file",
    )
    if hydro_file is not None:
        try:
            hydro_raw = parse_hydrometer_file(hydro_file, hydro_file.name)
            default_start = hydro_raw["eltime"].iloc[0] - timedelta(seconds=30)
            with st.expander("Pregled učitanih mjerenja"):
                show_preview(hydro_raw)
            c1, c2, c3 = st.columns(3)
            gs = c1.number_input(
                "Specifična gustoća čestica, Gs", min_value=2.50, max_value=2.85,
                value=2.65, step=0.01,
            )
            hydro_mass = c2.number_input(
                "Masa uzorka za areometriranje [g]", min_value=0.01, value=50.0, step=1.0
            )
            start_text = c3.text_input(
                "Početak pokusa", value=default_start.strftime("%Y-%m-%d %H:%M:%S")
            )
            with st.expander("Korekcije areometra"):
                c4, c5 = st.columns(2)
                meniscus = c4.number_input("Korekcija meniska", value=0.5, step=0.1)
                dispersant = c5.number_input("Korekcija disperzivnog sredstva", value=3.0, step=0.1)
            params = HydrometerParameters(
                gs, hydro_mass, pd.Timestamp(start_text), meniscus, dispersant
            )
            hydro_standalone = hydrometer_analysis(hydro_raw, params, 100.0)
            st.caption("Za skupni prikaz korekcija finom frakcijom primjenjuje se automatski.")
        except Exception as exc:
            st.error(f"Areometriranje nije obrađeno: {exc}")

with tab_results:
    available = []
    if sieve_result is not None:
        available.append("Mehaničko prosijavanje")
    if hydro_standalone is not None:
        available.append("Areometriranje")
    if sieve_result is not None and hydro_standalone is not None:
        available.insert(0, "Puna granulometrijska krivulja")

    if not available:
        st.info("Učitajte barem jednu datoteku kako bi se prikazali rezultati.")
    else:
        mode = st.radio("Prikaz", available, horizontal=True)
        series, export_hydro = [], None
        if mode in {"Mehaničko prosijavanje", "Puna granulometrijska krivulja"}:
            series.append(
                (sieve_result["sieve_mm"], sieve_result["passing_pct"],
                 "Mehaničko prosijavanje", "o")
            )
        if mode == "Areometriranje":
            export_hydro = hydro_standalone
            series.append(
                (export_hydro["diameter_mm"], export_hydro["hydrometer_passing_pct"],
                 "Areometriranje", "s")
            )
        elif mode == "Puna granulometrijska krivulja":
            fine_fraction = float(sieve_result.iloc[-1]["passing_pct"])
            params = HydrometerParameters(
                gs, hydro_mass, pd.Timestamp(start_text), meniscus, dispersant
            )
            export_hydro = hydrometer_analysis(hydro_raw, params, fine_fraction)
            series.append(
                (export_hydro["diameter_mm"], export_hydro["corrected_passing_pct"],
                 f"Areometriranje (korigirano × {fine_fraction / 100:.3f})", "s")
            )
            st.metric("Prolaz na najfinijem situ", f"{fine_fraction:.2f} %")

        fig = plot_curve(series)
        st.pyplot(fig, use_container_width=True)
        if export_hydro is not None:
            clay_col = (
                "corrected_passing_pct"
                if mode == "Puna granulometrijska krivulja"
                else "hydrometer_passing_pct"
            )
            clay = passing_at(export_hydro, 0.002, clay_col)
            if clay is not None:
                st.metric("Sadržaj čestica < 0,002 mm", f"{clay:.2f} %")

        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in sample_name)
        png_data, pdf_data = fig_bytes(fig, "png"), fig_bytes(fig, "pdf")
        export_sieve = sieve_result if mode != "Areometriranje" else None
        export_h = export_hydro if mode != "Mehaničko prosijavanje" else None
        csv_data = combined_export(export_sieve, export_h).to_csv(index=False).encode("utf-8-sig")
        d1, d2, d3 = st.columns(3)
        d1.download_button("Preuzmi graf (PNG)", png_data, f"granulometrija_{safe_name}.png", "image/png")
        d2.download_button("Preuzmi graf (PDF)", pdf_data, f"granulometrija_{safe_name}.pdf", "application/pdf")
        d3.download_button("Preuzmi sve podatke (CSV)", csv_data, f"granulometrija_{safe_name}.csv", "text/csv")
        plt.close(fig)
