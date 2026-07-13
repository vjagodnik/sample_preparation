"""
Laboratorij za geotehniku — glavna aplikacija.
Sve forme na jednom mjestu; izbornik je lijevo.
"""
import streamlit as st
from db import fetch, provjeri_vezu

st.set_page_config(page_title="Laboratorij — geotehnika", page_icon="🧪", layout="wide")

st.title("🧪 Laboratorij za geotehniku")
st.caption("Odaberi radnju u izborniku lijevo.")

ok, poruka = provjeri_vezu()
if not ok:
    st.error("Nema veze s bazom. Provjeri Secrets ([supabase]).")
    st.caption(f"Detalj: {poruka}")
    st.stop()

st.success("Veza s bazom je uspostavljena.")

# --- Kratki pregled stanja ---
st.subheader("Pregled")
try:
    c1, c2, c3, c4 = st.columns(4)

    na_cekanju = fetch(
        "SELECT count(*) FROM koristenje_opreme WHERE status = 'na_cekanju';"
    )[0][0]
    c1.metric("Zahtjevi na cekanju", na_cekanju)

    u_servisu = fetch("SELECT count(*) FROM oprema WHERE status = 'u_servisu';")[0][0]
    c2.metric("Oprema u servisu", u_servisu)

    ukupno_opreme = fetch("SELECT count(*) FROM oprema;")[0][0]
    c3.metric("Ukupno opreme", ukupno_opreme)

    uzoraka = fetch("SELECT count(*) FROM uzorci;")[0][0]
    c4.metric("Uzoraka u bazi", uzoraka)

    if na_cekanju:
        st.warning(f"⏳ {na_cekanju} zahtjev(a) ceka odobrenje "
                   f"— vidi stranicu **Odobravanje**.")
except Exception as e:
    st.info("Pregled trenutno nije dostupan.")
    st.caption(f"Detalj: {e}")

st.divider()
st.markdown(
    """
**Stranice (izbornik lijevo):**

| Stranica | Cemu sluzi |
|---|---|
| 📨 Zahtjev za opremu | podnosenje zahtjeva za koristenje uredaja |
| ✅ Odobravanje | voditelj/laborant odobrava ili odbija zahtjeve |
| 📥 Prijem uzorka | zaprimanje uzorka (projekt/klijent po potrebi u letu) |
| 🛠️ Prijava kvara | brza prijava kvara, uredaj ide u servis |
| ➕ Unos opreme | dodavanje novog uredaja u inventar |
"""
)
