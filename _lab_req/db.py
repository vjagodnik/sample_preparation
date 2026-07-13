"""Zajednicko spajanje na Supabase + verzija aplikacije."""
import streamlit as st
import psycopg2

# ---------------------------------------------------------------
#  VERZIJA APLIKACIJE
#  Format: glavna.manja.zakrpa
#    zakrpa (1.0.X) -> popravak sitnice
#    manja  (1.X.0) -> nova funkcija / stranica
#    glavna (X.0.0) -> veca promjena strukture baze
# ---------------------------------------------------------------
VERZIJA = "1.1.0"
DATUM_VERZIJE = "2026-07-13"


def prikazi_verziju():
    """Verzija u bocnoj traci — pozvati na svakoj stranici."""
    st.sidebar.caption(f"Laboratorij · v{VERZIJA} · {DATUM_VERZIJE}")


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


def execute(query, params=None, returning=False):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            val = cur.fetchone()[0] if returning else None
        conn.commit()
        return val
    finally:
        conn.close()


def provjeri_vezu():
    """Vrati (True, '') ili (False, poruka)."""
    try:
        fetch("SELECT 1;")
        return True, ""
    except Exception as e:
        return False, str(e)
