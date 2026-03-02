from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///movies.db"

# Create the engine
# echo=True prints all SQL statements SQLAlchemy runs (useful for debugging)
#engine = create_engine(DB_URL, echo=True) # Development
engine = create_engine(DB_URL, echo=False) # Runtime


def _init_db():
    """Create the movies table if it does not exist. Migrates old schema (no poster_url) by recreating the table."""
    with engine.connect() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT UNIQUE NOT NULL,
                    year INTEGER NOT NULL,
                    rating REAL NOT NULL,
                    poster_url TEXT
                )
                """
            )
        )
        connection.commit()

        # Migration: if table existed without poster_url, it has no such column
        result = connection.execute(text("PRAGMA table_info(movies)"))
        columns = [row[1] for row in result.fetchall()]
        if "poster_url" not in columns:
            connection.execute(text("DROP TABLE IF EXISTS movies"))
            connection.commit()
            connection.execute(
                text(
                    """
                    CREATE TABLE movies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT UNIQUE NOT NULL,
                        year INTEGER NOT NULL,
                        rating REAL NOT NULL,
                        poster_url TEXT
                    )
                    """
                )
            )
            connection.commit()


_init_db()


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating, poster_url FROM movies")
        )
        rows = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
            "poster_url": row[3] or "",
        }
        for row in rows
    }


def add_movie(title, year, rating, poster_url=None):
    """Add a new movie to the database."""
    poster_url = poster_url if poster_url is not None else ""
    with engine.connect() as connection:
        try:
            connection.execute(
                text(
                    "INSERT INTO movies (title, year, rating, poster_url) "
                    "VALUES (:title, :year, :rating, :poster_url)"
                ),
                {
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster_url": poster_url,
                },
            )
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except Exception as e:
            print(f"Error: {e}")


def delete_movie(title):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text("DELETE FROM movies WHERE title = :title"),
                {"title": title},
            )
            connection.commit()

            if result.rowcount == 0:
                print(f"Movie '{title}' not found.")
            else:
                print(f"Movie '{title}' deleted successfully.")
        except Exception as e:
            print(f"Error: {e}")


def update_movie(title, rating):
    """Update a movie's rating in the database."""
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text("UPDATE movies SET rating = :rating WHERE title = :title"),
                {"title": title, "rating": rating},
            )
            connection.commit()

            if result.rowcount == 0:
                print(f"Movie '{title}' not found.")
            else:
                print(f"Movie '{title}' updated successfully.")
        except Exception as e:
            print(f"Error: {e}")
