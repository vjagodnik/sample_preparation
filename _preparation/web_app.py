#%%
import streamlit as st
import pandas as pd
import numpy as np

st.title("📦 Priprema uzorka za laboratorij")

# Funkcija za izračun
def preparation_volume(shape="cylinder", diam=5, height=10, soil_type="SK00", density=0.5):
    if shape == "cylinder":
        Vt = (diam**2 * np.pi / 4) * height
    elif shape == "rectangle":
        Vt = diam**2 * height
    else:
        raise ValueError("Nepoznat oblik!")

    # Podaci o materijalima
    GsS = 2.7
    GsK = 2.6
    data = {
        "Soil_type": ["SK00", "SK10", "SK15", "SK20"],
        "emin": [0.641, 0.47947069, 0.399169312, 0.319174427],
        "emax": [0.911, 0.725064375, 0.632629838, 0.540548105],
        "MsK_perc": [0.00, 0.10, 0.15, 0.20],
        "MsS_perc": [1.00, 0.90, 0.85, 0.80],
        "GsMix": [GsS, 2.69, 2.67, 2.67]
    }
    df = pd.DataFrame(data)

    df["VsK_perc"] = GsS * df["MsK_perc"] / (df["MsS_perc"] * GsK + df["MsK_perc"] * GsS)
    df["VsS_perc"] = GsK * df["MsS_perc"] / (df["MsK_perc"] * GsS + df["MsS_perc"] * GsK)

    df["e0"] = df["emax"] - density * (df["emax"] - df["emin"])
    df["Vsolid"] = Vt / (df["e0"] + 1)
    df["Ms_mix"] = df["Vsolid"] * df["GsMix"]
    df["MsK_mix"] = df["Ms_mix"] * df["MsK_perc"]
    df["MsS_mix"] = df["Ms_mix"] * df["MsS_perc"]
    df["V_voids"] = df["Vsolid"] * df["e0"]
    df["Msat_mix"] = df["Ms_mix"] + df["V_voids"]

    row = df[df["Soil_type"] == soil_type].iloc[0]
    return row["MsK_mix"], row["MsS_mix"],row["Ms_mix"] ,row["Msat_mix"], df

# --- UI kontrole ---

col1, col2 = st.columns(2)
with col1:
    shape = st.radio("Oblik uzorka:", ["cylinder", "rectangle"])
with col2:
    soil_type = st.selectbox("Odaberi materijal:", ["SK00", "SK10", "SK15", "SK20"])

diam = st.number_input("Unesi promjer ili širinu [cm]:", value=5.0, min_value=1.0)
height = st.number_input("Unesi visinu [cm]:", value=10.0, min_value=1.0)
moisture = st.number_input("Unesi vlažnost [%]:", value=7.0, min_value=0.0, max_value=100.0)

# Tabovi za zbijenost
tabs = st.tabs(["Zbijenost 0.3", "Zbijenost 0.5", "Zbijenost 0.8"])
zbijenosti = [0.3, 0.5, 0.8]

for i, tab in enumerate(tabs):
    with tab:
        dens = zbijenosti[i]
        MsK, MsS, MsMx ,Msat, df = preparation_volume(
            shape=shape, diam=diam, height=height,
            soil_type=soil_type, density=dens
        )
# 
        st.markdown(f"### 📊 Rezultati za zbijenost {dens}")
        st.write(f"**Masa MsK (g):** {MsK:.2f}")
        st.write(f"**Masa MsS (g):** {MsS:.2f}")
        st.write(f"**Masa MsK + MsS (g):** {MsMx:.2f}")
        st.write(f"**Masa vlažnog uzorka (g):** {MsMx*(1+moisture/100):.2f}")
        st.write(f"**Zasićena masa (g):** {Msat:.2f}")

        with st.expander("🔍 Pogledaj sve izračune"):
            st.dataframe(df.style.format({col: "{:.3f}" for col in df.select_dtypes(include=[float, int]).columns}))


# %%
