import streamlit as st
import pandas as pd
from datetime import datetime
import os


@st.cache_data
def load_equipment():
    df = pd.read_excel("equipment.xlsx")
    # Uskladi nazive stupaca ako Excel ima višak praznih redaka ili drugačije zaglavlje
    df.columns = [col.strip() for col in df.columns]
    # Očisti redove bez inventarnog broja ili naziva opreme
    df = df.dropna(subset=["Inv no"])
    return df

df = load_equipment()

st.title("📘 Laboratorijski dnevnik - unos podataka")


oprema = st.selectbox("Odaberi opremu", df["LG 1"].fillna("").tolist() + df["LG 2"].fillna("").tolist() +
                      df["LG 3"].fillna("").tolist() + df["LG 4"].fillna("").tolist() +
                      df["LG 5"].fillna("").tolist() + df["GF Ri"].fillna("").tolist())

# pronađi inventarni broj i odgovornu osobu iz bilo kojeg stupca
inv_no, odg_osoba = None, None
for lab in ["LG 1", "LG 2", "LG 3", "LG 4", "LG 5", "GF Ri"]:
    mask = df[lab] == oprema
    if mask.any():
        inv_no = df.loc[mask, "Inv no"].values[0]
        odg_osoba = df.loc[mask, "Odg osoba"].values[0]
        break


materijal = st.selectbox("Vrsta materijala", ["Glina", "Prah", "Pijesak", "Šljunak", "Stijena", "Ostalo"])


potreba = st.selectbox(
    "Za koje potrebe se provodi ispitivanje",
    ["Nastava", "Završni rad", "Znanstveni rad", "Diplomski rad", "Doktorski rad", "Struka", "Ostalo"]
)


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

if datum_do < datum_od:
    st.warning("⚠️ Datum završetka ne može biti prije početka.")
    sati_koristenja = 0
else:
    trajanje = datum_do - datum_od
    sati_koristenja = round(trajanje.total_seconds() / 3600, 2)

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
        "Sati korištenja": sati_koristenja,
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

    st.success(f"💾 Zapis spremljen u {csv_file}")
    st.download_button(
        label="⬇️ Preuzmi CSV",
        data=df_new.to_csv(index=False, sep="\t").encode("utf-8-sig"),
        file_name="lab_dnevnik.tsv",
        mime="text/tab-separated-values"
    )
