# 🏥 FHIR Semestrální Projekt

Tento projekt je webová aplikace postavená na **Flasku**, která pracuje s **elektronickými zdravotními záznamy (EHR)**.  
Umožňuje správu pacientů, validaci dat a interakci s databází SQLite.

## 🚀 Funkce aplikace
- 📄 REST API pro správu pacientů  
- 🏥 Databázové operace (SQLite - `ehr.db`)  
- 🛠 Validace vstupních dat pomocí **Pydantic**  
- 🌐 Webové rozhraní s použitím **Flask Jinja Templates**  

## 📦 Instalace

Nejprve si naklonuj repozitář:

```bash
git clone https://github.com/KoliaUS/FHIR_Semestralni.git
cd FHIR_Semestralni
```

Nainstaluj potřebné závislosti (doporučeno použít **virtuální prostředí**):

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## ▶️ Spuštění aplikace

```bash
python app.py
```

Aplikace poběží na **http://127.0.0.1:5000/**.

## 🛠 API Endpointy

| Metoda  | Endpoint           | Popis               |
|---------|--------------------|---------------------|
| `GET`   | `/patients`        | Získá seznam pacientů |
| `POST`  | `/patients`        | Přidá nového pacienta |
| `GET`   | `/patients/<id>`   | Získá informace o pacientovi |
| `PUT`   | `/patients/<id>`   | Aktualizuje pacienta |
| `DELETE`| `/patients/<id>`   | Smaže pacienta |

## 🗃 Struktura databáze (SQLite)
Aplikace používá **SQLite databázi (`ehr.db`)**. Při prvním spuštění vytvoří potřebné tabulky.

Tabulka **patients**:
| id  | first_name | last_name | date_of_birth | gender |
|-----|-----------|-----------|---------------|--------|
| 1   | Jan       | Novák     | 1990-05-15    | M      |

## 📜 Licence
Tento projekt je open-source a dostupný pod licencí **MIT**.

---
