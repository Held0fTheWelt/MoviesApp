import html
import os

import requests

from API_KEY import OMDB_APY_KEY


def _escape(s):
    """Escape string for safe use in HTML."""
    return html.escape(str(s), quote=True)


_FLAG_CACHE: dict[str, str] = {}
_COUNTRY_CACHE: dict[str, tuple[str, str]] = {}


def _get_flag_for_country(country: str) -> str:
    """Return a flag image URL for the given country name using RestCountries."""
    name = (country or "").strip()
    if not name:
        return ""

    key = name.lower()
    if key in _FLAG_CACHE:
        return _FLAG_CACHE[key]

    try:
        resp = requests.get(
            f"https://restcountries.com/v3.1/name/{name}",
            params={"fields": "flags"},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data and isinstance(data[0], dict):
            flags = data[0].get("flags") or {}
            url = flags.get("png") or flags.get("svg") or ""
            _FLAG_CACHE[key] = url
            return url
    except requests.RequestException:
        pass

    _FLAG_CACHE[key] = ""
    return ""


def _get_country_and_flag(title: str, imdb_id: str) -> tuple[str, str]:
    """Fetch country and flag-image-URL using OMDb (country) + RestCountries (flag)."""
    cache_key = (imdb_id or "").strip().lower() or title.lower()
    if cache_key in _COUNTRY_CACHE:
        return _COUNTRY_CACHE[cache_key]

    params = {"apikey": OMDB_APY_KEY}
    if imdb_id:
        params["i"] = imdb_id
    else:
        params["t"] = title

    country = ""
    flag_url = ""
    try:
        resp = requests.get("http://www.omdbapi.com/", params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        if data.get("Response") == "True":
            country_raw = data.get("Country") or ""
            if country_raw:
                country = country_raw.split(",")[0].strip()
                flag_url = _get_flag_for_country(country)
    except requests.RequestException:
        pass

    _COUNTRY_CACHE[cache_key] = (country, flag_url)
    return country, flag_url


def _build_movie_grid(movies):
    """Build the HTML for the movie grid from the movies dictionary.
    Each item: li > div.movie > poster wrapper (img + note overlay), title, country-flag image, year, rating.
    Note is shown on hover over the poster.
    """
    lines = []
    for title, data in movies.items():
        year = data.get("year", "")
        rating = data.get("rating", "")
        poster_url = data.get("poster_url", "") or ""
        note = data.get("note", "") or ""
        imdb_id = (data.get("imdb_id") or "").strip()

        # Country & flag via secondary API (not persisted in DB)
        country, flag_url = _get_country_and_flag(title, imdb_id)

        title_esc = _escape(title)
        year_esc = _escape(year)
        rating_esc = _escape(str(rating)) if rating != "" else ""
        poster_esc = _escape(poster_url)
        note_esc = _escape(note)
        imdb_id_esc = _escape(imdb_id)
        country_esc = _escape(country)
        flag_url_esc = _escape(flag_url)

        note_content = f'<div class="movie-note">{note_esc}</div>' if note_esc else ""
        rating_node = f'<div class="movie-rating">★ {rating_esc}</div>' if rating_esc else ""
        country_node = ""
        if flag_url_esc:
            country_node = (
                f'<div class="movie-country">'
                f'<img class="movie-flag" src="{flag_url_esc}" alt="{country_esc} flag" loading="lazy">'
                f"</div>"
            )

        imdb_url = f"https://www.imdb.com/title/{imdb_id_esc}/" if imdb_id_esc else ""
        if imdb_url:
            poster_block = (
                f'<a class="movie-poster-link" href="{imdb_url}" target="_blank" rel="noopener noreferrer">\n'
                '                <div class="movie-poster-wrap">\n'
                f'                <img class="movie-poster" src="{poster_esc}" alt="{title_esc}">\n'
                f"                {note_content}\n"
                "                </div>\n"
                "                </a>"
            )
        else:
            poster_block = (
                '                <div class="movie-poster-wrap">\n'
                f'                <img class="movie-poster" src="{poster_esc}" alt="{title_esc}">\n'
                f"                {note_content}\n"
                "                </div>"
            )

        lines.append(
            "        <li>\n"
            '            <div class="movie">\n'
            f"                {poster_block}\n"
            f'                <div class="movie-title">{title_esc}</div>\n'
            f"                {country_node}\n"
            f'                <div class="movie-year">{year_esc}</div>\n'
            f"                {rating_node}\n"
            "            </div>\n"
            "        </li>"
        )
    return "\n\n        ".join(lines)


def generate_website(movies, title="My Movie App", output_filename=None):
    """
    Generate HTML from the template and the current movies.
    Template and output are in project root's _static (same directory as style.css).
    If output_filename is given (e.g. "John.html"), the file is saved under that name.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, "_static")
    template_path = os.path.join(static_dir, "index_template.html")
    if output_filename:
        safe_name = os.path.basename(output_filename).replace("\\", "").replace("/", "")
        if not safe_name.endswith(".html"):
            safe_name += ".html"
        output_path = os.path.join(static_dir, safe_name)
    else:
        output_path = os.path.join(static_dir, "index.html")

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("__TEMPLATE_TITLE__", _escape(title))
    content = content.replace("__TEMPLATE_MOVIE_GRID__", _build_movie_grid(movies))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Website was generated successfully.")


def create_rating_histogram(movies):
    pass
