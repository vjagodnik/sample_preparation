import streamlit as st
import pandas as pd
from datetime import datetime
import os
import yagmail
from openpyxl import Workbook

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
    ["4294.0", "Uređaj za direktno smicanje A", "Martina Vivoda Prodan"],
    ["4295.0", "Uređaj za direktno smicanje B", "Martina Vivoda Prodan"],
    ["4296.0", "Uređaj za direktno smicanje C", "Martina Vivoda Prodan"],
    ["4290.0", "Casagrandeov uređaj A", "Martina Vivoda Prodan"],
    ["4291.0", "Casagrandeov uređaj B", "Martina Vivoda Prodan"],
    ["4100.0", "Desikator", "Juraj Stella"],
    ["4101.0", "Termometar", "Juraj Stella"],
    ["4102.0", "Digitalna kupelj", "Juraj Stella"],
    ["4293.0", "Treskalica sita", "Martina Vivoda Prodan"],
    ["4298.0", "Uređaj za ispitivanje stišljivosti Edometar 1", "Martina Vivoda Prodan"],
    ["4299.0", "Uređaj za ispitivanje stišljivosti Edometar 2", "Martina Vivoda Prodan"],
    ["4300.0", "Uređaj za ispitivanje stišljivosti Edometar 3", "Martina Vivoda Prodan"],
    ["4302.0", "Uređaj za zbijanje Proctor", "Martina Vivoda Prodan"],
    ["4103.0", "Ručni izvlakač uzorka", "Juraj Stella"],
    ["0.0", "Oprema za određivanje gustoće čestica, Controls", "Vedran Jagodnik"],
    ["4104.0", "Džepni penetrometar, Controls", "Juraj Stella"],
    ["4105.0", "Kartice za tlo Munsell, Controls", "Juraj Stella"],
    ["4106.0", "Kartice za stijene Munsell, Controls", "Juraj Stella"],
    ["4303.0", "Multispeed preša - CBR, Controls", "Vedran Jagodnik"],
    ["4294.0", "Bender elementi za triaxalni uređaj 1", "Martina Vivoda Prodan"],
    ["4295.0", "Bender elementi za triaxalni uređaj 2", "Martina Vivoda Prodan"],
    ["4296.0", "Veliki uređaj za smicanje Large Shear", "Martina Vivoda Prodan"],
    ["4290.0", "GDS uređaj za direktno smicanje", "Martina Vivoda Prodan"],
    ["4291.0", "GDS bender elementi", "Martina Vivoda Prodan"],
    ["4100.0", "Automatski edometar ACE", "Juraj Stella"],
    ["4101.0", "Uređaj za dinamičko troosno ispitivanje", "Juraj Stella"],
    ["4102.0", "Uređaj za troosno ispitivanje 1", "Juraj Stella"],
    ["4293.0", "Uređaj za troosno ispitivanje 2", "Martina Vivoda Prodan"],
    ["4298.0", "Uređaj za troosno ispitivanje 3", "Martina Vivoda Prodan"],
    ["4299.0", "Hidraulični edometar Hydrocon", "Martina Vivoda Prodan"],
    ["4300.0", "Uređaj za konstantnu konsolidaciju CRS", "Martina Vivoda Prodan"],
    ["4302.0", "Resonant column", "Martina Vivoda Prodan"],
    ["4103.0", "Garnitura pretvornika - on sample, Controls", "Juraj Stella"],
    ["0.0", "Triaksijalna ćelija za nesaturirana tla, Controls", "Vedran Jagodnik"],
    ["4104.0", "Set za ispitivanje vodopropusnosti", "Juraj Stella"],
    ["4105.0", "Osciloskop i generator signala", "Juraj Stella"],
    ["4294.0", "Univerzalna preša za ispitivanje stijena", "Martina Vivoda Prodan"],
    ["4295.0", "Mjerni sustav na uzorku kod aksijalnog ispitivanja", "Martina Vivoda Prodan"],
    ["4296.0", "Troosna ćelija i sustav za postizanje i održavanje ćelijskog tlaka", "Martina Vivoda Prodan"],
    ["4290.0", "Oprema za mjerenje deformacija uzorka u troosnoj ćeliji", "Martina Vivoda Prodan"],
    ["4291.0", "Oprema za ultrazvučno ispitivanje", "Martina Vivoda Prodan"],
    ["4100.0", "Bušilica za stijene HILTI", "Juraj Stella"],
    ["4101.0", "Pila za rezanje jezgre stijene iz bušotine", "Juraj Stella"],
    ["4102.0", "Brusilica za stijenovite uzorke", "Juraj Stella"],
    ["4293.0", "Oprema za kontrolu postignute točnosti obrade uzorka", "Martina Vivoda Prodan"],
    ["4298.0", "Oprema za određivanje slake durability indeksa", "Martina Vivoda Prodan"],
    ["4299.0", "Čeljusti za ispitivanje vlačne čvrstoće", "Martina Vivoda Prodan"],
    ["4294.0", "Istiskivač uzoraka, Controls", "Martina Vivoda Prodan"],
    ["4295.0", "Trimer za obradu ispitivanih uzoraka tla, Controls", "Martina Vivoda Prodan"],
    ["4296.0", "Vakuum sustav, Controls", "Martina Vivoda Prodan"],
    ["4290.0", "Peć za žarenje", "Martina Vivoda Prodan"],
    ["4291.0", "Sušionik 250l, Controls", "Martina Vivoda Prodan"],
    ["4100.0", "Drobilica, Controls", "Juraj Stella"],
    ["4101.0", "UV System -  ultraljubičasta lampa", "Juraj Stella"],
    ["4102.0", "Geološki čekić, Controls x2", "Juraj Stella"],
    ["4293.0", "Geološki kompas Brunton", "Martina Vivoda Prodan"],
    ["4298.0", "Geološki kompas Freiberg Krantz", "Martina Vivoda Prodan"],
    ["4299.0", "Skala tvrdoće, Controls", "Martina Vivoda Prodan"],
    ["4300.0", "Nagibni ispitni uređaj za kut trenja, Controls", "Martina Vivoda Prodan"],
    ["4302.0", "Garmin Oregon 650", "Martina Vivoda Prodan"],
    ["4103.0", "Mikroskop trinokularni, Sole-Mark", "Juraj Stella"],
    ["4294.0", "Dinamička ploča", "Martina Vivoda Prodan"],
    ["4295.0", "Terenska oprema za uzimanje suhih uzoraka tla", "Martina Vivoda Prodan"],
    ["4296.0", "Terenska oprema za uzimanje mokrih uzoraka tla", "Martina Vivoda Prodan"],
    ["4294.0", "Casagrandeov uređaj, ručni", "Martina Vivoda Prodan"],
    ["4295.0", "Digitalni penetrometar za određivanje granice tečenja sa mikrometarskim vertikalnim podešavanjem", "Martina Vivoda Prodan"],
    ["4296.0", "Kalup za linearno skupljanje BS 1377", "Martina Vivoda Prodan"],
    ["4290.0", "Piknometar za pijesak i fini šljunak", "Martina Vivoda Prodan"],
    ["4291.0", "Gay-lussac-ova posuda za određivanje specifične gustoće A", "Martina Vivoda Prodan"],
    ["4100.0", "Gay-lussac-ova posuda za određivanje specifične gustoće B", "Juraj Stella"],
    ["4101.0", "Gay-lussac-ova posuda za određivanje specifične gustoće C", "Juraj Stella"],
    ["4102.0", "Električni sterilizator", "Juraj Stella"],
    ["4293.0", "Prijenosni uređaj za izravni posmik", "Martina Vivoda Prodan"],
    ["4298.0", "Čekić za klasifikaciju stijena - Sklerometar", "Martina Vivoda Prodan"],
    ["4299.0", "ASTM postolje za sklerometar", "Martina Vivoda Prodan"],
    ["4300.0", "PLT - Digitalni aparat za određivanje indeksa čvrtoće stijene", "Martina Vivoda Prodan"],
    ["4302.0", "Dinamička konusna penetracijska sonda", "Martina Vivoda Prodan"],
    ["4103.0", "Inklinometar", "Juraj Stella"],
    ["0.0", "Uređaj za prstenasto smicanje", "Vedran Jagodnik"],
    ["4104.0", "End - over shaker", "Juraj Stella"],
    ["4105.0", "Hydrometer", "Juraj Stella"],
    ["4106.0", "Krilna sonda sa penetrometrom", "Juraj Stella"],
    ["4303.0", "Menzura od 1 l", "Vedran Jagodnik"],
    ["", "Chatelierova tikvica", ""],
    ["", "Mikser", ""],
    ["", "Gay-lussac-ova posuda za određivanje specifične gustoće D", ""],
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

    # === Spremi i kao tab-delimited CSV (za čitanje)
    csv_named_path = os.path.abspath("lab_dnevnik_zapis.csv")
    df_last = pd.DataFrame([zapis_dict])
    df_last.to_csv(csv_named_path, index=False, sep="\t", encoding="utf-8-sig")

    # === Kreiraj i Excel (.xlsx) fajl s istim podacima ===
    xlsx_path = os.path.abspath("lab_dnevnik_zapis.xlsx")
    wb = Workbook()
    ws = wb.active
    ws.title = "Zapis"

    # zaglavlja
    ws.append(list(df_last.columns))
    # podaci
    for _, row in df_last.iterrows():
        ws.append(list(row.values))

    wb.save(xlsx_path)

    # === Generiraj .ics ===
    create_ics_file(zapis_dict)
    ics_path = os.path.abspath("lab_dnevnik.ics")

    # Pohrani u session_state
    st.session_state["xlsx_file"] = xlsx_path
    st.session_state["ics_file"] = ics_path
    st.session_state["zapis_dict"] = zapis_dict

    # Gumb za preuzimanje Excel datoteke
    st.download_button(
        label="⬇️ Preuzmi Excel datoteku (zadnji zapis)",
        data=open(xlsx_path, "rb").read(),
        file_name="lab_dnevnik_zapis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# === SLANJE E-MAILA ===
if "email" in st.secrets:
    if st.button("📧 Pošalji e-mail laboratoriju"):
        if "xlsx_file" not in st.session_state or "ics_file" not in st.session_state:
            st.error("⚠️ Nema generiranog zapisa za slanje. Prvo klikni 'Generiraj zapis'.")
        else:
            try:
                import os

                recipient = st.secrets["email"]["recipient"]
                sender = st.secrets["email"]["sender"]
                app_password = st.secrets["email"]["app_password"]

                yag = yagmail.SMTP(sender, app_password)
                zapis = st.session_state["zapis_dict"]

                xlsx_path = os.path.abspath(st.session_state["xlsx_file"])
                ics_path = os.path.abspath(st.session_state["ics_file"])

                attachments = [xlsx_path, ics_path]

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
                st.info("📎 Poslani privitci:\n- lab_dnevnik_zapis.xlsx\n- lab_dnevnik.ics")

            except Exception as e:
                st.error(f"⚠️ Greška pri slanju e-maila: {e}")
else:
    st.info("ℹ️ E-mail nije konfiguriran. Dodaj podatke u Streamlit Secrets.")
