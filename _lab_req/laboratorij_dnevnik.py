import streamlit as st
import pandas as pd
from datetime import datetime
import os
import yagmail

# === FUNKCIJA ZA GENERIRANJE .ICS FAJLA ===
def create_ics_file(zapis):
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Laboratorij Geotehnika//Dnevnik//HR
BEGIN:VEVENT
UID:{zapis['Inv no']}@lab.geotehnika.hr
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%S')}
DTSTART:{datetime.strptime(zapis['Datum od'], '%Y-%m-%d').strftime('%Y%m%dT090000')}
DTEND:{datetime.strptime(zapis['Datum do'], '%Y-%m-%d').strftime('%Y%m%dT170000')}
SUMMARY:{zapis['Oprema']} - {zapis['Podnositelj']}
LOCATION:Laboratorij za geotehniku, Rijeka
DESCRIPTION:Materijal: {zapis['Materijal']}\\nPotreba: {zapis['Potreba']}\\nOpis: {zapis['Opis']}
BEGIN:VALARM
TRIGGER:-PT30M
ACTION:DISPLAY
DESCRIPTION:Podsjetnik - Ispitivanje {zapis['Oprema']}
END:VALARM
END:VEVENT
END:VCALENDAR
"""
    with open("lab_dnevnik.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)


# === POPIS OPREME (kraćena verzija za primjer) ===
data = [
    ["4294", "Uređaj za direktno smicanje A", "Martina Vivoda Prodan"],
    ["4295", "Uređaj za direktno smicanje B", "Martina Vivoda Prodan"],
    ["4302", "Uređaj za zbijanje Proctor", "Martina Vivoda Prodan"],
    ["4556", "Uređaj za dinamičko troosno ispitivanje", "Vedran Jagodnik"],
    ["4986", "Univerzalna preša za ispitivanje stijena", "Josip Peranić"],
]
df = pd.DataFrame(data, columns=["Inv no", "Oprema", "Odgovorna osoba"])

# === APLIKACIJA ===
st.title("📘 Laboratorijski dnevnik - unos podataka")

oprema = st.selectbox("Odaberi opremu", df["Oprema"])
inv_no = df.loc[df["Oprema"] == oprema, "Inv no"].values[0]
odg_osoba = df.loc[df["Oprema"] == oprema, "Odgovorna osoba"].values[0]

materijal = st.selectbox("Vrsta materijala", ["Glina", "Prah", "Pijesak", "Šljunak", "Stijena", "Ostalo"])
potreba = st.selectbox("Za koje potrebe se provodi ispitivanje",
                       ["Nastava", "Završni rad", "Znanstveni rad", "Diplomski rad", "Doktorski rad", "Struka", "Ostalo"])

st.subheader("⏱️ Vrijeme ispitivanja")
col1, col2 = st.columns(2)
with col1:
    datum_pocetak = st.date_input("Datum početka")
    vrijeme_pocetak = st.time_input("Vrijeme početka")
with col2:
    datum_kraj = st.date_input("Datum završetka")
    vrijeme_kraj = st.time_input("Vrijeme završetka")

datum_od = datetime.combine(datum_pocetak, vrijeme_pocetak)
datum_do = datetime.combine(datum_kraj, vrijeme_kraj)
sati_koristenja = max((datum_do - datum_od).total_seconds() / 3600, 0)

opis = st.text_area("Kratki opis ispitivanja")
podnositelj = st.text_input("Podnositelj")

# === GENERIRAJ ZAPIS ===
if st.button("Generiraj zapis"):
    zapis_dict = {
        "Inv no": inv_no,
        "Oprema": oprema,
        "Materijal": materijal,
        "Potreba": potreba,
        "Datum od": datum_od.strftime("%Y-%m-%d"),
        "Datum do": datum_do.strftime("%Y-%m-%d"),
        "Sati korištenja": round(sati_koristenja, 2),
        "Opis": opis,
        "Podnositelj": podnositelj,
        "Komentar": " ",
        "Odgovorna osoba": odg_osoba,
    }

    st.success("✅ Zapis generiran:")
    st.write(pd.DataFrame([zapis_dict]))

    # === Spremi CSV (tab-delimited, ali s .csv ekstenzijom) ===
    df_last = pd.DataFrame([zapis_dict])
    csv_named_path = os.path.abspath("lab_dnevnik_zapis.csv")
    df_last.to_csv(csv_named_path, index=False, sep="\t", encoding="utf-8-sig")

    # === Generiraj .ics ===
    create_ics_file(zapis_dict)
    ics_path = os.path.abspath("lab_dnevnik.ics")

    # Spremi putanje i podatke u session_state
    st.session_state["csv_file"] = csv_named_path
    st.session_state["ics_file"] = ics_path
    st.session_state["zapis_dict"] = zapis_dict

    # Gumb za preuzimanje CSV-a
    st.download_button(
        label="⬇️ Preuzmi CSV datoteku (zadnji zapis)",
        data=open(csv_named_path, "rb").read(),
        file_name="lab_dnevnik_zapis.csv",
        mime="text/csv"
    )

# === SLANJE E-MAILA ===
if "email" in st.secrets:
    if st.button("📧 Pošalji e-mail laboratoriju"):
        if "csv_file" not in st.session_state or "ics_file" not in st.session_state:
            st.error("⚠️ Nema generiranog zapisa za slanje. Prvo klikni 'Generiraj zapis'.")
        else:
            try:
                recipient = st.secrets["email"]["recipient"]
                sender = st.secrets["email"]["sender"]
                app_password = st.secrets["email"]["app_password"]

                yag = yagmail.SMTP(sender, app_password)
                zapis = st.session_state["zapis_dict"]

                # === Privitci: CSV (tab-delimited) i ICS ===
                attachments = [
                    os.path.abspath(st.session_state["csv_file"]),
                    os.path.abspath(st.session_state["ics_file"]),
                ]

                yag.send(
                    to=recipient,
                    subject=f"Laboratorijski zapis - {zapis['Oprema']}",
                    contents=f"""Pozdrav,

U privitku se nalazi zadnji laboratorijski zahtjev i događaj za Google Calendar.

Podnositelj: {zapis['Podnositelj']}
Oprema: {zapis['Oprema']}
Materijal: {zapis['Materijal']}
Potreba: {zapis['Potreba']}
Vrijeme: {zapis['Datum od']} - {zapis['Datum do']}

LP,
Streamlit aplikacija""",
                    attachments=attachments,
                )

                st.success(f"📤 E-mail uspješno poslan na {recipient}")
                st.info("📎 Poslani privitci:\n- lab_dnevnik_zapis.csv\n- lab_dnevnik.ics")

            except Exception as e:
                st.error(f"⚠️ Greška pri slanju e-maila: {e}")
else:
    st.info("ℹ️ E-mail nije konfiguriran. Dodaj podatke u Streamlit Secrets.")
