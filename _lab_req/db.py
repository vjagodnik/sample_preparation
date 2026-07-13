"""Zajednicko spajanje na Supabase — koriste ga sve stranice."""
import streamlit as st
import psycopg2


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
