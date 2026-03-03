# My Movies Database

Kleine Konsolen-App zur persönlichen Filmdatenbank. Jeder Nutzer hat eine eigene Sammlung; Filme werden per **OMDb API** geladen (Titel, Jahr, Bewertung, Poster). Zu jedem Film kann eine **Notiz** gespeichert werden.

## Voraussetzungen

- Python 3
- OMDb API-Key (kostenlos auf [omdbapi.com](http://www.omdbapi.com/apikey.aspx))

## Installation

```bash
pip install -r requirements.txt
```

In `API_KEY.py` den eigenen Key eintragen:

```python
OMDB_APY_KEY = 'dein-api-key'
```

## Start

```bash
python movies.py
```

Beim Start wählst du einen **Nutzer** (oder legst einen neuen an). Alle Filme und Notizen gehören zu diesem Nutzer.

## Funktionen

- **Filme auflisten** – nur die Filme des aktuellen Nutzers
- **Film hinzufügen** – Filmtitel eingeben → OMDb liefert Daten → Notiz optional eingeben
- **Film löschen**
- **Film aktualisieren** – Notiz zu einem Film setzen oder ändern
- **Nutzer wechseln** – zu einem anderen Profil wechseln
- **Statistiken**, **Zufallsfilm**, **Suchen**, **Filtern**, **Sortieren**
- **Rating-Histogramm** (Konsole oder PNG)
- **Website generieren** – erzeugt z. B. `_static/John.html` mit der Sammlung des Nutzers; Notizen erscheinen beim Hover über das Poster

## Projektstruktur

- **`data/`** – SQLite-Datenbank (`movies.db`), wird beim ersten Start angelegt
- **`storage/`** – Speicherlogik (Nutzer, Filme, Notizen)
- **`features/`** – Website-Generierung, Plots
- **`_static/`** – HTML-Vorlage und generierte Webseiten
