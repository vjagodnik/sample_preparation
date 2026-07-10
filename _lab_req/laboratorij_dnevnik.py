"""
Zahtjev za koristenje opreme — Streamlit forma spojena na Supabase.

Tok:
  1) Podnositelj ispuni i klikne "Posalji zahtjev" -> redak ide u koristenje_opreme (status='na_cekanju').
  2) Zaseban gumb "Posalji e-mail" -> obavijest voditelju i laborantu s Excel + .ics privitkom.
  3) Voditelj/laborant u NocoDB-u promijene status u 'odobreno' / 'odbijeno'.

Postavljanje: Streamlit Secrets (vidi secrets_TEMPLATE.toml) — [supabase] i [email].
"""
#%%
import os
import tempfile
from datetime import datetime

import streamlit as st
import psycopg2
from openpyxl import Workbook

st.set_page_config(page_title="Zahtjev za koristenje opreme", page_icon="🔬")


# ----------------------- BAZA (Supabase) -----------------------
def get_conn():
    s = st.secrets["supabase"]
    return psycopg2.connect(
        host=s["host"], port=s["port"], dbname=s["dbname"],
        user=s["user"], password=s["password"],
        sslmode="require", connect_timeout=10,
    )


def fetch(query, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()


@st.cache_data(ttl=300)
def ucitaj_opremu():
    # (id, inv, naziv, odgovorna_osoba)
    return fetch(
        """
        SELECT o.id, o.interna_oznaka, o.naziv, s.ime_prezime
        FROM oprema o
        LEFT JOIN osoblje s ON s.id = o.odgovorna_osoba
        WHERE o.status = 'u_uporabi' OR o.status IS NULL
        ORDER BY o.naziv;
        """
    )


@st.cache_data(ttl=300)
def ucitaj_osoblje():
    return [r[0] for r in fetch(
        "SELECT ime_prezime FROM osoblje WHERE aktivan = TRUE ORDER BY ime_prezime;"
    )]


def spremi_zahtjev(oprema_id, vrijeme_od, vrijeme_do, materijal,
                   potreba, opis, podnositelj, sati):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO koristenje_opreme
                    (oprema_id, vrijeme_od, vrijeme_do, materijal,
                     potrebe_ispitivanja, opis, podnositelj,
                     sati_koristenja, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'na_cekanju');
                """,
                (oprema_id, vrijeme_od, vrijeme_do, materijal,
                 potreba, opis, podnositelj, sati),
            )
        conn.commit()
    finally:
        conn.close()


# ----------------------- PRIVITCI -----------------------
def napravi_excel(zapis):
    path = os.path.join(tempfile.gettempdir(), "zahtjev_zapis.xlsx")
    wb = Workbook()
    ws = wb.active
    ws.title = "Zahtjev"
    ws.append(list(zapis.keys()))
    ws.append(list(zapis.values()))
    wb.save(path)
    return path


def napravi_ics(zapis, vrijeme_od, vrijeme_do):
    path = os.path.join(tempfile.gettempdir(), "zahtjev.ics")
    ics = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "PRODID:-//Laboratorij Geotehnika//Zahtjev//HR\n"
        "BEGIN:VEVENT\n"
        f"UID:{datetime.now().strftime('%Y%m%d%H%M%S')}@lab.geotehnika.hr\n"
        f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%S')}\n"
        f"DTSTART:{vrijeme_od.strftime('%Y%m%dT%H%M%S')}\n"
        f"DTEND:{vrijeme_do.strftime('%Y%m%dT%H%M%S')}\n"
        f"SUMMARY:{zapis['Oprema']} - {zapis['Podnositelj']}\n"
        "LOCATION:Laboratorij za geotehniku, Rijeka\n"
        f"DESCRIPTION:Materijal: {zapis['Materijal']}\\nPotreba: {zapis['Potreba']}"
        f"\\nOpis: {zapis['Opis']}\n"
        "BEGIN:VALARM\nTRIGGER:-PT30M\nACTION:DISPLAY\n"
        "DESCRIPTION:Podsjetnik - koristenje opreme\nEND:VALARM\n"
        "END:VEVENT\nEND:VCALENDAR\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(ics)
    return path


# ---------------------------- SUCELJE ----------------------------
st.title("🔬 Zahtjev za koristenje opreme")
st.caption("Ispuni zahtjev. Nakon slanja ceka odobrenje voditelja ili laboranta.")

try:
    oprema_rows = ucitaj_opremu()
    osobe = ucitaj_osoblje()
except Exception as e:
    st.error("Ne mogu se spojiti na bazu. Provjeri Secrets ([supabase]).")
    st.caption(f"Detalj: {e}")
    st.stop()

if not oprema_rows:
    st.warning("U bazi nema opreme za odabir.")
    st.stop()

labele = [f"{naziv}  ·  inv. {inv or '—'}" for (_id, inv, naziv, _odg) in oprema_rows]
i = st.selectbox("Oprema", range(len(labele)), format_func=lambda i: labele[i])
_id, inv_br, naziv_opreme, odg_osoba = oprema_rows[i]

materijal = st.selectbox("Vrsta materijala",
                         ["Glina", "Prah", "Pijesak", "Sljunak", "Stijena", "Ostalo"])
potreba = st.selectbox("Za koje potrebe se provodi ispitivanje",
                       ["Nastava", "Zavrsni rad", "Diplomski rad", "Doktorski rad",
                        "Znanstveni rad", "Struka", "Ostalo"])

st.subheader("⏱️ Vrijeme")
c1, c2 = st.columns(2)
with c1:
    d_od = st.date_input("Datum pocetka")
    t_od = st.time_input("Vrijeme pocetka")
with c2:
    d_do = st.date_input("Datum zavrsetka")
    t_do = st.time_input("Vrijeme zavrsetka")

opis = st.text_area("Kratki opis ispitivanja")

podnositelj = st.selectbox("Podnositelj", osobe + ["Ostalo (upisi)"])
if podnositelj == "Ostalo (upisi)":
    podnositelj = st.text_input("Ime podnositelja")

vrijeme_od = datetime.combine(d_od, t_od)
vrijeme_do = datetime.combine(d_do, t_do)
sati = round(max((vrijeme_do - vrijeme_od).total_seconds() / 3600, 0), 2)
st.info(f"Trajanje: **{sati} h**")

st.divider()

# 1) SPREMI ZAHTJEV U BAZU
if st.button("📨 Posalji zahtjev", type="primary"):
    if vrijeme_do <= vrijeme_od:
        st.error("Vrijeme zavrsetka mora biti nakon pocetka.")
    elif not podnositelj:
        st.error("Upisi podnositelja.")
    else:
        try:
            spremi_zahtjev(_id, vrijeme_od, vrijeme_do, materijal,
                           potreba, opis, podnositelj, sati)
            zapis = {
                "Inv. br.": inv_br or "",
                "Oprema": naziv_opreme,
                "Odgovorna osoba": odg_osoba or "",
                "Materijal": materijal,
                "Potreba": potreba,
                "Datum od": vrijeme_od.strftime("%Y-%m-%d %H:%M"),
                "Datum do": vrijeme_do.strftime("%Y-%m-%d %H:%M"),
                "Sati": sati,
                "Opis": opis,
                "Podnositelj": podnositelj,
                "Status": "na_cekanju",
            }
            st.session_state["zapis"] = zapis
            st.session_state["vrijeme_od"] = vrijeme_od
            st.session_state["vrijeme_do"] = vrijeme_do
            st.success("✅ Zahtjev je poslan u bazu i ceka odobrenje.")
            st.dataframe([zapis], use_container_width=True)
        except Exception as e:
            st.error(f"Greska pri spremanju u bazu: {e}")

# 2) ZASEBAN GUMB — E-MAIL VODITELJU I LABORANTU
st.divider()
st.subheader("📧 Obavijest e-mailom")

if "email" not in st.secrets:
    st.info("E-mail nije konfiguriran (dodaj [email] u Secrets).")
elif "zapis" not in st.session_state:
    st.caption("Prvo posalji zahtjev, pa mozes poslati obavijest.")
else:
    if st.button("📧 Posalji e-mail voditelju i laborantu"):
        try:
            import yagmail

            zapis = st.session_state["zapis"]
            xlsx = napravi_excel(zapis)
            ics = napravi_ics(zapis, st.session_state["vrijeme_od"],
                              st.session_state["vrijeme_do"])

            sender = st.secrets["email"]["sender"]
            app_password = st.secrets["email"]["app_password"]
            recipients = st.secrets["email"]["recipients"]

            yag = yagmail.SMTP(sender, app_password)
            yag.send(
                to=list(recipients),
                subject=f"Novi zahtjev (na cekanju): {zapis['Oprema']}",
                contents=(
                    "Pozdrav,\n\nStigao je novi zahtjev za koristenje opreme "
                    "(status: na cekanju odobrenja).\n\n"
                    f"Podnositelj: {zapis['Podnositelj']}\n"
                    f"Oprema: {zapis['Oprema']} (inv. {zapis['Inv. br.']})\n"
                    f"Materijal: {zapis['Materijal']}\n"
                    f"Potreba: {zapis['Potreba']}\n"
                    f"Vrijeme: {zapis['Datum od']} - {zapis['Datum do']} "
                    f"({zapis['Sati']} h)\n"
                    f"Opis: {zapis['Opis']}\n\n"
                    "Zahtjev odobrite/odbijte u NocoDB-u (polje status).\n\n"
                    "— Automatska obavijest"
                ),
                attachments=[xlsx, ics],
            )
            st.success(f"📤 E-mail poslan na: {', '.join(recipients)}")
        except Exception as e:
            st.error(f"Greska pri slanju e-maila: {e}")
# %%
