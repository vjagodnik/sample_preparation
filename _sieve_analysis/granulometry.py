from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import numpy as np
import pandas as pd


SIEVE_ALIASES = {
    "sieve": "sieve_mm", "sieve_mm": "sieve_mm", "opening": "sieve_mm",
    "otvor": "sieve_mm", "otvor sita": "sieve_mm", "mm": "sieve_mm",
    "retained": "retained_g", "retained_g": "retained_g", "mass": "retained_g",
    "masa": "retained_g", "ostatak": "retained_g", "ostatak_g": "retained_g",
}


@dataclass(frozen=True)
class HydrometerParameters:
    specific_gravity: float
    sample_mass_g: float
    start_time: pd.Timestamp
    meniscus_correction: float = 0.5
    dispersant_correction: float = 3.0


def _read_table(source: BinaryIO | BytesIO | str | Path, filename: str = "") -> pd.DataFrame:
    name = filename or str(getattr(source, "name", source))
    suffix = Path(name).suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(source)
    # sep=None handles tabs, commas and semicolons; decimal comma is normalized below.
    return pd.read_csv(source, sep=None, engine="python", dtype=str)


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.strip().str.replace(",", ".", regex=False), errors="coerce")


def parse_sieve_file(source: BinaryIO | BytesIO | str | Path, filename: str = "") -> tuple[str, pd.DataFrame]:
    raw = _read_table(source, filename)
    if raw.shape[1] < 2:
        raise ValueError("Datoteka prosijavanja mora imati najmanje dva stupca.")

    columns = [str(c).strip() for c in raw.columns]
    normalized = [SIEVE_ALIASES.get(c.lower(), c) for c in columns]
    raw.columns = normalized
    sample_name = columns[1]

    if "sieve_mm" in raw.columns and "retained_g" in raw.columns:
        sieve, retained = raw["sieve_mm"], raw["retained_g"]
    else:
        # Format used by Butoniga: first header is "Uzorak", second is sample ID.
        sieve, retained = raw.iloc[:, 0], raw.iloc[:, 1]

    data = pd.DataFrame({"sieve_mm": _numeric(sieve), "retained_g": _numeric(retained)}).dropna()
    data = data[data["sieve_mm"] > 0].sort_values("sieve_mm", ascending=False).reset_index(drop=True)
    if data.empty:
        raise ValueError("Nisu pronađeni valjani otvori sita i mase ostatka.")
    if (data["retained_g"] < 0).any():
        raise ValueError("Masa ostatka na situ ne može biti negativna.")
    return sample_name, data


def sieve_analysis(data: pd.DataFrame, total_mass_g: float) -> pd.DataFrame:
    if total_mass_g <= 0:
        raise ValueError("Ukupna masa uzorka mora biti veća od nule.")
    out = data.copy()
    out["retained_pct"] = out["retained_g"] / total_mass_g * 100
    out["cumulative_retained_pct"] = out["retained_pct"].cumsum()
    out["passing_pct"] = (100 - out["cumulative_retained_pct"]).clip(lower=0, upper=100)
    return out


def parse_hydrometer_file(source: BinaryIO | BytesIO | str | Path, filename: str = "") -> pd.DataFrame:
    raw = _read_table(source, filename)
    raw.columns = [str(c).strip().lower() for c in raw.columns]
    aliases = {"vrijeme": "eltime", "time": "eltime", "temperatura": "temp",
               "temperature": "temp", "očitanje": "reading", "ocitanje": "reading"}
    raw = raw.rename(columns=aliases)
    missing = {"eltime", "temp", "reading"} - set(raw.columns)
    if missing:
        raise ValueError("Nedostaju stupci za areometriranje: " + ", ".join(sorted(missing)))
    data = pd.DataFrame({
        "eltime": pd.to_datetime(raw["eltime"], errors="coerce"),
        "temp_c": _numeric(raw["temp"]),
        "reading": _numeric(raw["reading"]),
    }).dropna()
    if data.empty:
        raise ValueError("Datoteka nema valjana mjerenja areometrom.")
    return data.sort_values("eltime").reset_index(drop=True)


def hydro_bulb(reading: np.ndarray) -> np.ndarray:
    return 20.761 - 0.3958 * reading


def temperature_correction(temperature: np.ndarray) -> np.ndarray:
    return 0.004 * temperature**2 + 0.0253 * temperature - 1.9878


def k_value(temperature: np.ndarray, density: float) -> np.ndarray:
    temperatures = np.arange(16, 31, dtype=float)
    densities = np.arange(2.50, 2.86, 0.05)
    values = np.array([
        [0.0151,0.0148,0.0146,0.0144,0.0141,0.0139,0.0137,0.0136],
        [0.0149,0.0146,0.0144,0.0142,0.0140,0.0138,0.0136,0.0134],
        [0.0148,0.0144,0.0142,0.0140,0.0138,0.0136,0.0134,0.0132],
        [0.0145,0.0143,0.0140,0.0138,0.0136,0.0134,0.0132,0.0131],
        [0.0143,0.0141,0.0139,0.0137,0.0134,0.0133,0.0131,0.0129],
        [0.0141,0.0139,0.0137,0.0135,0.0133,0.0131,0.0129,0.0127],
        [0.0140,0.0137,0.0135,0.0133,0.0131,0.0129,0.0127,0.0126],
        [0.0138,0.0136,0.0134,0.0132,0.0130,0.0128,0.0126,0.0124],
        [0.0137,0.0134,0.0132,0.0130,0.0128,0.0126,0.0125,0.0123],
        [0.0135,0.0133,0.0131,0.0129,0.0127,0.0125,0.0123,0.0122],
        [0.0133,0.0131,0.0129,0.0127,0.0125,0.0124,0.0122,0.0120],
        [0.0132,0.0130,0.0128,0.0126,0.0124,0.0122,0.0120,0.0119],
        [0.0130,0.0128,0.0126,0.0124,0.0123,0.0121,0.0119,0.0117],
        [0.0129,0.0127,0.0125,0.0123,0.0121,0.0120,0.0118,0.0116],
        [0.0128,0.0126,0.0124,0.0122,0.0120,0.0118,0.0117,0.0115],
    ])
    if not 2.5 <= density <= 2.85 or np.any((temperature < 16) | (temperature > 30)):
        raise ValueError("K-vrijednost podržava temperaturu 16–30 °C i gustoću 2,50–2,85.")
    # Bilinear interpolation without a SciPy dependency.
    by_temp = np.array([np.interp(density, densities, row) for row in values])
    return np.array([np.interp(t, temperatures, by_temp) for t in temperature])


def hydrometer_analysis(data: pd.DataFrame, params: HydrometerParameters,
                        fine_fraction_pct: float = 100.0) -> pd.DataFrame:
    if params.sample_mass_g <= 0 or not 1 < params.specific_gravity:
        raise ValueError("Masa mora biti pozitivna, a specifična gustoća veća od 1.")
    elapsed_min = (data["eltime"] - params.start_time).dt.total_seconds().to_numpy() / 60
    if np.any(elapsed_min <= 0):
        raise ValueError("Sva vremena mjerenja moraju biti nakon početnog vremena pokusa.")
    temp = data["temp_c"].to_numpy(float)
    reading = data["reading"].to_numpy(float)
    corrected_meniscus = reading + params.meniscus_correction
    depth_cm = hydro_bulb(corrected_meniscus)
    if np.any(depth_cm <= 0):
        raise ValueError("Izračunata efektivna dubina nije pozitivna; provjerite očitanja.")
    diameter = k_value(temp, params.specific_gravity) * np.sqrt(depth_cm / elapsed_min)
    corrected_reading = corrected_meniscus + temperature_correction(temp) - params.dispersant_correction
    hydrometer_passing = (100 / params.sample_mass_g) * (
        params.specific_gravity / (params.specific_gravity - 1)
    ) * corrected_reading
    out = data.copy()
    out["elapsed_min"] = elapsed_min
    out["effective_depth_cm"] = depth_cm
    out["diameter_mm"] = diameter
    out["hydrometer_passing_pct"] = hydrometer_passing.clip(0, 100)
    out["corrected_passing_pct"] = (out["hydrometer_passing_pct"] * fine_fraction_pct / 100).clip(0, 100)
    return out.sort_values("diameter_mm", ascending=False).reset_index(drop=True)


def passing_at(data: pd.DataFrame, diameter_mm: float, passing_column: str) -> float | None:
    valid = data[["diameter_mm", passing_column]].dropna().sort_values("diameter_mm")
    if valid.empty or not valid["diameter_mm"].min() <= diameter_mm <= valid["diameter_mm"].max():
        return None
    return float(np.interp(np.log10(diameter_mm), np.log10(valid["diameter_mm"]), valid[passing_column]))


def combined_export(sieve: pd.DataFrame | None, hydrometer: pd.DataFrame | None) -> pd.DataFrame:
    frames = []
    if sieve is not None:
        s = sieve.copy()
        s.insert(0, "method", "mechanical_sieving")
        s["diameter_mm"] = s["sieve_mm"]
        s["curve_passing_pct"] = s["passing_pct"]
        frames.append(s)
    if hydrometer is not None:
        h = hydrometer.copy()
        h.insert(0, "method", "hydrometer")
        h["curve_passing_pct"] = h["corrected_passing_pct"]
        frames.append(h)
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()
