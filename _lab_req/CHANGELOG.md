# Dnevnik verzija — Laboratorij za geotehniku

Verzija se postavlja u `db.py` (`VERZIJA`, `DATUM_VERZIJE`)
i prikazuje se u bočnoj traci na svakoj stranici.

Format: `glavna.manja.zakrpa`
- **zakrpa** (1.0.**X**) — popravak sitnice
- **manja** (1.**X**.0) — nova funkcija ili stranica
- **glavna** (**X**.0.0) — veća promjena strukture baze

---

## 1.1.0 — 2026-07-13
- Sve forme spojene u **jednu aplikaciju** s izbornikom (jedan link)
- Nova stranica **✅ Odobravanje** — odobri/odbij zahtjev, bilježi tko i kada
- Nova stranica **🔧 Rješavanje kvarova** — zatvori kvar, vrati uređaj u upotrebu
- Početna stranica s pregledom stanja (zahtjevi, kvarovi, oprema, uzorci)
- Prikaz verzije u bočnoj traci

## 1.0.0 — 2026-07-10
- Zahtjev za korištenje opreme (upis u bazu, e-mail, status `na_cekanju`)
- Prijem uzorka (projekt i klijent po potrebi "u letu", atomarni upis)
- Prijava kvara (uređaj automatski ide `u_servisu`)
- Unos opreme (auto `id`, status iz izbornika, provjera duplikata inv. broja)
- Baza: Supabase (PostgreSQL) — sljedivost, audit trag, pravilo četiri oka
