# Laboratorij za geotehniku — aplikacija

Streamlit aplikacija povezana sa Supabase (PostgreSQL) bazom.

## Stranice
| Stranica | Čemu služi |
|---|---|
| 📨 Zahtjev za opremu | podnošenje zahtjeva za korištenje uređaja |
| ✅ Odobravanje | voditelj/laborant odobrava ili odbija zahtjeve |
| 📥 Prijem uzorka | zaprimanje uzorka (projekt/klijent po potrebi u letu) |
| 🛠️ Prijava kvara | brza prijava kvara — uređaj ide `u_servisu` |
| ➕ Unos opreme | dodavanje novog uređaja u inventar |
| 🔧 Rješavanje kvarova | zatvaranje kvara — uređaj se vraća `u_uporabi` |

## Pokretanje (Streamlit Cloud)
1. Sadržaj ove mape stavi u **korijen** GitHub repozitorija.
2. share.streamlit.io → New app → glavna datoteka: **`Pocetna.py`**
3. Settings → Secrets:

```toml
[supabase]
host = "aws-1-eu-west-2.pooler.supabase.com"
port = "5432"
dbname = "postgres"
user = "postgres.xxxxxxxx"
password = "LOZINKA"

[email]                       # nije obavezno
sender = "posiljatelj@gmail.com"
app_password = "GOOGLE-APP-PASSWORD"
recipients = ["voditelj@...", "laborant@..."]
```

## Verzija
Postavlja se u `db.py` (`VERZIJA`). Vidi `CHANGELOG.md`.
