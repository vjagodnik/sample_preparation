import streamlit as st
import pandas as pd
from datetime import datetime
import os
import yagmail

# === Popis opreme (pretvoren iz equipment.xlsx) ===
data = [
    ["4294", "Uređaj za direktno smicanje A", "Martina Vivoda Prodan"],
    ["4295", "Uređaj za direktno smicanje B", "Martina Vivoda Prodan"],
    ["4296", "Uređaj za direktno smicanje C", "Martina Vivoda Prodan"],
    ["4290", "Casagrandeov uređaj A", "Martina Vivoda Prodan"],
    ["4291", "Casagrandeov uređaj B", "Martina Vivoda Prodan"],
    ["4100", "Desikator", "Juraj Stella"],
    ["4101", "Termometar", "Juraj Stella"],
    ["4102", "Digitalna kupelj", "Juraj Stella"],
    ["4293", "Treskalica sita", "Martina Vivoda Prodan"],
    ["4298", "Uređaj za ispitivanje stišljivosti Edometar 1", "Martina Vivoda Prodan"],
    ["4299", "Uređaj za ispitivanje stišljivosti Edometar 2", "Martina Vivoda Prodan"],
    ["4300", "Uređaj za ispitivanje stišljivosti Edometar 3", "Martina Vivoda Prodan"],
    ["4302", "Uređaj za zbijanje Proctor", "Martina Vivoda Prodan"],
    ["4103", "Ručni izvlakač uzorka", "Juraj Stella"],
    ["0", "Oprema za određivanje gustoće čestica, Controls", "Vedran Jagodnik"],
    ["4104", "Džepni penetrometar, Controls", "Juraj Stella"],
    ["4105", "Kartice za tlo Munsell, Controls", "Juraj Stella"],
    ["4106", "Kartice za stijene Munsell, Controls", "Juraj Stella"],
    ["4303", "Multispeed preša - CBR, Controls", "Vedran Jagodnik"],
    # (ostatak popisa kao što već imaš)
]

df = pd.DataFrame(data, columns=["Inv no", "Oprema", "Odgovorna osoba"])

# === Funkcija za kreiranje Google Calendar (.ics) datoteke ===
def create_ics_file(zapis_dict):
    try:
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Ispitivanje - {zapis_dict['Oprema']}
DTSTART:{datetime.strptime(zapis_dict['Datum od'], "%Y-%m-%d").strftime('%Y%m%dT090000')}
DTEND:{datetime.strptime(zapis_dict['Datum do'], "%Y-%m-%d").strftime('%Y%m%dT170000')}
DESCRIPTION:Podnositelj: {zapis_dict['Podnositelj']}\\nMaterijal: {zapis_dict['Materijal']}\\nPotreba: {zapis_dict['Potreba']}\\nOpis: {zapis_dict['Opis']}
END:VEVENT
END:VCALENDAR
"""
        with open("lab_dnevnik.ics", "w", encoding="utf-8") as f:
            f.write(ics_content)
    except Exception as e:
        st.error(f"⚠️ Greška pri kreiranju .ics datoteke: {e}")

# === Streamlit sučelje ===
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

# === Generiranje zapisa ===
# === Generiranje zapisa ===
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

    # === Spremi CSV s akumuliranim zapisima ===
    csv_file = "lab_dnevnik.csv"
    if os.path.exists(csv_file):
        df_existing = pd.read_csv(csv_file)
        df_new = pd.concat([df_existing, pd.DataFrame([zapis_dict])], ignore_index=True)
    else:
        df_new = pd.DataFrame([zapis_dict])
    df_new.to_csv(csv_file, index=False, encoding="utf-8-sig")

    # === Spremi TSV i ICS samo za zadnji zapis ===
    df_last = pd.DataFrame([zapis_dict])
    tsv_file = "lab_dnevnik_posljednji.tsv"
    df_last.to_csv(tsv_file, index=False, sep="\t", encoding="utf-8-sig")

    ics_file = "lab_dnevnik.ics"
    create_ics_file(zapis_dict)

    # Spremi imena datoteka u session_state da ih kasnije može koristiti e-mail dio
    st.session_state["tsv_file"] = tsv_file
    st.session_state["ics_file"] = ics_file
    st.session_state["zapis_dict"] = zapis_dict

    # Gumb za preuzimanje TSV datoteke
    st.download_button(
        label="⬇️ Preuzmi TSV datoteku (zadnji zapis)",
        data=open(tsv_file, "rb").read(),
        file_name=tsv_file,
        mime="text/tab-separated-values"
    )
# === Slanje e-maila (ako su tajne postavljene) ===
if "email" in st.secrets:
    if st.button("📧 Pošalji e-mail laboratoriju"):
        if "tsv_file" not in st.session_state or "ics_file" not in st.session_state:
            st.error("⚠️ Nema generiranog zapisa za slanje. Prvo klikni 'Generiraj zapis'.")
        else:
            try:
                import os
                import tempfile
                recipient = st.secrets["email"]["recipient"]
                sender = st.secrets["email"]["sender"]
                app_password = st.secrets["email"]["app_password"]

                yag = yagmail.SMTP(sender, app_password)

                zapis = st.session_state["zapis_dict"]
                tsv_path = os.path.abspath(st.session_state["tsv_file"])
                ics_path = os.path.abspath(st.session_state["ics_file"])

                # 🔹 napravi privremenu kopiju TSV-a da Gmail ga sigurno prepozna
                with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv") as tmp_tsv:
                    tmp_tsv.write(open(tsv_path, "rb").read())
                    tmp_tsv_path = tmp_tsv.name

                # 🔹 napravi listu privitaka s apsolutnim putanjama
                attachments = [tmp_tsv_path, ics_path]

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
                st.info(f"📎 Poslani privitci:\n- {os.path.basename(tmp_tsv_path)}\n- {os.path.basename(ics_path)}")

            except Exception as e:
                st.error(f"⚠️ Greška pri slanju e-maila: {e}")
else:
    st.info("ℹ️ E-mail nije konfiguriran. Dodaj podatke u Streamlit Secrets.")
