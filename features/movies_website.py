import html
import os


def _escape(s):
    """Escape string for safe use in HTML."""
    return html.escape(str(s), quote=True)


def _build_movie_grid(movies):
    """Build the HTML for the movie grid from the movies dictionary.
    Each item: li > div.movie > img.movie-poster, div.movie-title, div.movie-year.
    """
    lines = []
    for title, data in movies.items():
        year = data.get("year", "")
        poster_url = data.get("poster_url", "") or ""
        title_esc = _escape(title)
        year_esc = _escape(year)
        poster_esc = _escape(poster_url)
        lines.append(
            "        <li>\n"
            "            <div class=\"movie\">\n"
            f"                <img class=\"movie-poster\" src=\"{poster_esc}\" title=\"\">\n"
            f"                <div class=\"movie-title\">{title_esc}</div>\n"
            f"                <div class=\"movie-year\">{year_esc}</div>\n"
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
