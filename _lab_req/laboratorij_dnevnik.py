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
    ["4547", "Bender elementi za triaxialni uređaj 1", "Martina Vivoda Prodan"],
    ["4548", "Bender elementi za triaxialni uređaj 2", "Martina Vivoda Prodan"],
    ["4560", "Veliki uređaj za smicanje Large Shear", "Vedran Jagodnik"],
    ["4538", "GDS uređaj za direktno smicanje", "Vedran Jagodnik"],
    ["4538a", "GDS bender elementi", "Vedran Jagodnik"],
    ["4539", "Automatski edometar ACE", "Vedran Jagodnik"],
    ["4556", "Uređaj za dinamičko troosno ispitivanje", "Vedran Jagodnik"],
    ["4540", "Uređaj za troosno ispitivanje 1", "Vedran Jagodnik"],
    ["4558", "Hidraulični edometar Hydrocon", "Vedran Jagodnik"],
    ["4557", "Uređaj za konstantnu konsolidaciju CRS", "Martina Vivoda Prodan"],
    ["4559", "Resonant column", "Vedran Jagodnik"],
    ["4550", "Garnitura pretvornika - on sample, Controls", "Vedran Jagodnik"],
    ["4554", "Triaksijalna ćelija za nesaturirana tla, Controls", "Vedran Jagodnik"],
    ["4555", "Set za ispitivanje vodopropusnosti", "Vedran Jagodnik"],
    ["4549", "Osciloskop i generator signala", "Martina Vivoda Prodan"],
    ["4986", "Univerzalna preša za ispitivanje stijena", "Josip Peranić"],
    ["4987", "Mjerni sustav na uzorku kod aksijalnog ispitivanja", "Josip Peranić"],
    ["4988", "Troosna ćelija i sustav za postizanje i održavanje ćelijskog tlaka", "Josip Peranić"],
    ["4989", "Oprema za mjerenje deformacija uzorka u troosnoj ćeliji", "Josip Peranić"],
    ["4990", "Oprema za ultrazvučno ispitivanje", "Josip Peranić"],
    ["4993", "Bušilica za stijene HILTI", "Josip Peranić"],
    ["4994", "Pila za rezanje jezgre stijene iz bušotine", "Josip Peranić"],
    ["4995", "Brusilica za stijenovite uzorke", "Josip Peranić"],
    ["4996", "Oprema za kontrolu postignute točnosti obrade uzorka", "Josip Peranić"],
    ["4997", "Oprema za određivanje 'slake durability' indeksa", "Josip Peranić"],
    ["4998", "Čeljusti za ispitivanje vlačne čvrstoće", "Josip Peranić"],
    ["4272", "Istiskivač uzoraka, Controls", "Vedran Jagodnik"],
    ["4273", "Trimer za obradu ispitivanih uzoraka tla, Controls", "Vedran Jagodnik"],
    ["4274", "Vakuum sustav, Controls", "Vedran Jagodnik"],
    ["4275", "Peć za žarenje", "Vedran Jagodnik"],
    ["4276", "Sušionik 250l, Controls", "Vedran Jagodnik"],
    ["4277", "Drobilica, Controls", "Vedran Jagodnik"],
    ["4279", "UV System - ultraljubičasta lampa", "Petra Đomlija"],
    ["4280", "Geološki čekić, Controls x2", "Petra Đomlija"],
    ["4281", "Geološki kompas Brunton", "Petra Đomlija"],
    ["4282", "Geološki kompas Freiberg Krantz", "Petra Đomlija"],
    ["4283", "Skala tvrdoće, Controls", "Petra Đomlija"],
    ["4284", "Nagibni ispitni uređaj za kut trenja, Controls", "Petra Đomlija"],
    ["4285", "Garmin Oregon 650", "Petra Đomlija"],
    ["4286", "Mikroskop trinokularni, Sole-Mark", "Petra Đomlija"],
    ["4287", "Dinamička ploča", "Sanja Dugonjić Jovančević"],
    ["4288", "Terenska oprema za uzimanje suhih uzoraka tla", "Sanja Dugonjić Jovančević"],
    ["4289", "Terenska oprema za uzimanje mokrih uzoraka tla", "Sanja Dugonjić Jovančević"],
    ["999", "Casagrandeov uređaj, ručni", "Juraj Stella"],
    ["1000", "Digitalni penetrometar za određivanje granice tečenja", "Juraj Stella"],
    ["1001", "Kalup za linearno skupljanje BS 1377", "Juraj Stella"],
    ["1002", "Piknometar za pijesak i fini šljunak", "Juraj Stella"],
    ["1003", "Gay-Lussac posuda za određivanje specifične gustoće A", "Juraj Stella"],
    ["1004", "Gay-Lussac posuda za određivanje specifične gustoće B", "Juraj Stella"],
    ["1005", "Gay-Lussac posuda za određivanje specifične gustoće C", "Juraj Stella"],
    ["1006", "Električni sterilizator", "Juraj Stella"],
    ["1007", "Prijenosni uređaj za izravni posmik", "Juraj Stella"],
    ["1008", "Čekić za klasifikaciju stijena - Sklerometar", "Juraj Stella"],
    ["1009", "ASTM postolje za sklerometar", "Juraj Stella"],
    ["1010", "PLT - Digitalni aparat za određivanje indeksa čvrstoće stijene", "Juraj Stella"],
    ["1011", "Dinamička konusna penetracijska sonda", "Juraj Stella"],
    ["1012", "Inklinometar", "Juraj Stella"],
    ["1013", "Uređaj za prstenasto smicanje", "Martina Vivoda Prodan"],
    ["1014", "End-over shaker", "Juraj Stella"],
    ["1015", "Hydrometer", "Juraj Stella"],
    ["1016", "Krilna sonda sa penetrometrom", "Juraj Stella"],
    ["1017", "Menzura od 1 L", "Juraj Stella"],
    ["1018", "Chatelierova tikvica", "Juraj Stella"],
    ["1019", "Mikser", "Juraj Stella"],
    ["1020", "Gay-Lussac posuda za određivanje specifične gustoće D", "Juraj Stella"],
]

df = pd.DataFrame(data, columns=["Inv no", "Oprema", "Odgovorna osoba"])

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

if st.button("Generiraj zapis"):
    zapis_dict = {
        "Inv no": inv_no,
        "Oprema": oprema,
        "Odgovorna osoba": odg_osoba,
        "Materijal": materijal,
        "Potreba": potreba,
        "Datum od": datum_od.strftime("%Y-%m-%d"),
        "Datum do": datum_do.strftime("%Y-%m-%d"),
        "Sati korištenja": round(sati_koristenja, 2),
        "Opis": opis,
        "Podnositelj": podnositelj,
    }

    st.success("✅ Zapis generiran:")
    st.write(pd.DataFrame([zapis_dict]))

    csv_file = "lab_dnevnik.csv"
    if os.path.exists(csv_file):
        df_existing = pd.read_csv(csv_file)
        df_new = pd.concat([df_existing, pd.DataFrame([zapis_dict])], ignore_index=True)
    else:
        df_new = pd.DataFrame([zapis_dict])
    df_new.to_csv(csv_file, index=False, encoding="utf-8-sig")

    st.download_button(
        label="⬇️ Preuzmi CSV (TSV format)",
        data=df_new.to_csv(index=False, sep="\t").encode("utf-8-sig"),
        file_name="lab_dnevnik.tsv",
        mime="text/tab-separated-values"
    )
# === Slanje e-maila (ako su tajne postavljene) ===
if "email" in st.secrets:
    if st.button("📧 Pošalji e-mail laboratoriju"):
        try:
            import yagmail

            recipient = st.secrets["email"]["recipient"]
            sender = st.secrets["email"]["sender"]
            app_password = st.secrets["email"]["app_password"]

            yag = yagmail.SMTP(sender, app_password)
            yag.send(
                to=recipient,
                subject="Novi laboratorijski zapis",
                contents="Pozdrav,\n\nU privitku se nalazi najnoviji laboratorijski zapis.\n\nLP,\nStreamlit aplikacija",
                attachments="lab_dnevnik.csv",
            )
            st.success(f"📤 E-mail uspješno poslan na {recipient}")
        except Exception as e:
            st.error(f"⚠️ Greška pri slanju e-maila: {e}")
else:
    st.info("ℹ️ E-mail nije konfiguriran. Dodaj podatke u Streamlit Secrets.")
