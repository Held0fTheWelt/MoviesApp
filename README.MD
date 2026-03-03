# My Movies Database

Kleine Konsolen-Anwendung zur Verwaltung einer Filmdatenbank. Filme werden per **OMDb API** gesucht und mit Titel, Jahr, Bewertung und Poster-URL gespeichert.

## Voraussetzungen

- Python 3
- OMDb API-Key (kostenlos auf [omdbapi.com](http://www.omdbapi.com/apikey.aspx))

## Installation

```bash
pip install -r requirements.txt
```

In `API_KEY.py` den eigenen OMDb-Key eintragen:

```python
OMDB_APY_KEY = 'dein-api-key'
```

## Start

```bash
python movies.py
```

## Funktionen

- **Filme auflisten** – alle gespeicherten Filme anzeigen
- **Film hinzufügen** – nur Filmtitel eingeben, Rest kommt von OMDb
- **Film löschen**
- **Film aktualisieren** (Bewertung)
- **Statistiken** – Durchschnitt, Median, bester/schlechtester Film
- **Zufallsfilm**, **Suchen**, **Filtern**, **Sortieren**
- **Rating-Histogramm** (Konsole oder PNG)
- **Website generieren** – erzeugt `_static/index.html` aus den Filmdaten

Die Daten werden in einer SQLite-Datenbank (`movies.db`) gespeichert.
