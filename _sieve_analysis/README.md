# Granulometrijska analiza

Streamlit aplikacija za obradu mehaničkog prosijavanja i areometriranja, prikaz zasebnih ili pune granulometrijske krivulje te izvoz grafa i obrađenih podataka.

## Pokretanje

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Ulazni podaci

- Prosijavanje: prva dva stupca predstavljaju otvor sita u mm i masu ostatka u g. Podržan je format `Uzorak<TAB>Naziv uzorka` iz dostavljenog primjera.
- Areometriranje: stupci `eltime`, `temp` i `reading`.

Kod pune krivulje prolaz iz areometriranja množi se udjelom prolaza na najfinijem situ iz mehaničke analize. Kod zasebnog prikaza areometriranje se prikazuje na vlastitoj skali.
