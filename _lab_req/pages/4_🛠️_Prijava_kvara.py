"""
Prijava kvara opreme — Streamlit forma spojena na Supabase.

Brza prijava: koji uredaj, sto ne radi, tko prijavljuje, hitnost.
Upisuje u kvarovi_opreme; po zelji stavlja uredaj 'u_servisu' (pa se vise
ne nudi u zahtjev-formi). Opcionalno salje mail voditelju i laborantu.

Secrets: [supabase] (obavezno), [email] (opcionalno).
"""

from datetime import datetime

import streamlit as st

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import fetch, get_conn, prikazi_verziju

st.set_page_config(page_title="Prijava kvara opreme", page_icon="🛠️")
prikazi_verziju()


@st.cache_data(ttl=120)
def ucitaj_opremu():
    return fetch(
        "SELECT id, interna_oznaka, naziv, status FROM oprema ORDER BY naziv;"
    )


@st.cache_data(ttl=120)
def ucitaj_osoblje():
    return [r[0] for r in fetch(
        "SELECT ime_prezime FROM osoblje WHERE aktivan = TRUE ORDER BY ime_prezime;"
    )]


def prijavi_kvar(oprema_id, opis, hitnost, prijavio, van_uporabe):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO kvarovi_opreme
                   (oprema_id, opis_kvara, hitnost, prijavio, stavljen_van_uporabe)
                   VALUES (%s,%s,%s,%s,%s);""",
                (oprema_id, opis, hitnost, prijavio, van_uporabe),
            )
            if van_uporabe:
                cur.execute(
                    "UPDATE oprema SET status = 'u_servisu' WHERE id = %s;",
                    (oprema_id,),
                )
        conn.commit()
    finally:
        conn.close()


# ---------------------------- SUCELJE ----------------------------
st.title("🛠️ Prijava kvara opreme")
st.caption("Brza prijava kvara. Po zelji stavlja uredaj u servis.")

try:
    oprema_rows = ucitaj_opremu()
    osobe = ucitaj_osoblje()
except Exception as e:
    st.error("Ne mogu se spojiti na bazu. Provjeri Secrets ([supabase]).")
    st.caption(f"Detalj: {e}")
    st.stop()

if not oprema_rows:
    st.warning("U bazi nema opreme.")
    st.stop()

labele = [f"{naziv}  ·  inv. {inv or '—'}  ·  {status or ''}"
          for (_id, inv, naziv, status) in oprema_rows]
i = st.selectbox("Uredaj u kvaru", range(len(labele)), format_func=lambda i: labele[i])
_id, inv_br, naziv_opreme, trenutni_status = oprema_rows[i]

opis = st.text_area("Opis kvara *", placeholder="Sto tocno ne radi / sto se dogodilo?")
hitnost = st.selectbox("Hitnost", ["niska", "srednja", "visoka"], index=1)

prijavio = st.selectbox("Prijavljuje", osobe + ["Ostalo (upisi)"])
if prijavio == "Ostalo (upisi)":
    prijavio = st.text_input("Ime")

van_uporabe = st.checkbox("Odmah staviti uredaj VAN UPOTREBE (u servis)", value=True,
                          help="Ako je oznaceno, uredaj se vise nece nuditi za koristenje "
                               "dok se kvar ne rijesi.")

st.divider()
if st.button("🛠️ Prijavi kvar", type="primary"):
    if not opis.strip():
        st.error("Upisi opis kvara.")
    elif not prijavio:
        st.error("Upisi tko prijavljuje.")
    else:
        try:
            prijavi_kvar(_id, opis.strip(), hitnost, prijavio, van_uporabe)
            st.session_state["kvar"] = {
                "Oprema": naziv_opreme, "Inv": inv_br or "",
                "Opis": opis.strip(), "Hitnost": hitnost,
                "Prijavio": prijavio,
                "Van upotrebe": "DA" if van_uporabe else "NE",
                "Datum": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.success("✅ Kvar je prijavljen.")
            if van_uporabe:
                st.warning(f"Uredaj '{naziv_opreme}' je stavljen u servis "
                           f"(vise se ne nudi za koristenje).")
            st.balloons()
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Greska pri spremanju: {e}")

# --- Opcionalna e-mail obavijest ---
st.divider()
st.subheader("📧 Obavijest e-mailom")
if "email" not in st.secrets:
    st.info("E-mail nije konfiguriran (dodaj [email] u Secrets).")
elif "kvar" not in st.session_state:
    st.caption("Prvo prijavi kvar, pa mozes poslati obavijest.")
else:
    if st.button("📧 Posalji obavijest voditelju i laborantu"):
        try:
            import yagmail
            k = st.session_state["kvar"]
            sender = st.secrets["email"]["sender"]
            app_password = st.secrets["email"]["app_password"]
            recipients = list(st.secrets["email"]["recipients"])
            yag = yagmail.SMTP(sender, app_password)
            yag.send(
                to=recipients,
                subject=f"KVAR opreme ({k['Hitnost']}): {k['Oprema']}",
                contents=(
                    "Pozdrav,\n\nPrijavljen je kvar opreme.\n\n"
                    f"Uredaj: {k['Oprema']} (inv. {k['Inv']})\n"
                    f"Hitnost: {k['Hitnost']}\n"
                    f"Stavljen van upotrebe: {k['Van upotrebe']}\n"
                    f"Prijavio: {k['Prijavio']} ({k['Datum']})\n\n"
                    f"Opis: {k['Opis']}\n\n"
                    "Status pratite u NocoDB-u (tablica kvarovi_opreme).\n\n"
                    "— Automatska obavijest"
                ),
            )
            st.success(f"📤 Obavijest poslana na: {', '.join(recipients)}")
        except Exception as e:
            st.error(f"Greska pri slanju e-maila: {e}")
