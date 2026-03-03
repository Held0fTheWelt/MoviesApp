import os

from sqlalchemy import create_engine, text

# Database in project's data/ directory
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "data")
os.makedirs(_DATA_DIR, exist_ok=True)
_DB_PATH = os.path.join(_DATA_DIR, "movies.db")
DB_URL = "sqlite:///" + _DB_PATH.replace("\\", "/")

# echo=True prints all SQL statements (useful for debugging)
# engine = create_engine(DB_URL, echo=True)
engine = create_engine(DB_URL, echo=False)


def _init_db():
    """Create users and movies tables. Migrate old schema (no user_id) if needed."""
    with engine.connect() as connection:
        # Users table
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
                """
            )
        )
        connection.commit()

        # Movies table (with user_id)
        result = connection.execute(text("PRAGMA table_info(movies)"))
        rows = result.fetchall()
        columns = [row[1] for row in rows]

        if not columns:
            # No movies table: create with user_id from the start
            connection.execute(
                text(
                    """
                    CREATE TABLE movies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        year INTEGER NOT NULL,
                        rating REAL NOT NULL,
                        poster_url TEXT,
                        UNIQUE(user_id, title),
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                    """
                )
            )
            connection.commit()
        elif "user_id" not in columns:
            # Migrate: add user_id, one default user, move existing movies to that user
            connection.execute(text("INSERT OR IGNORE INTO users (id, name) VALUES (1, 'Default')"))
            connection.commit()
            connection.execute(text("ALTER TABLE movies ADD COLUMN user_id INTEGER"))
            connection.execute(text("UPDATE movies SET user_id = 1 WHERE user_id IS NULL"))
            connection.commit()
            # Recreate with proper UNIQUE(user_id, title) - SQLite can't add composite UNIQUE via ALTER
            connection.execute(text("CREATE TABLE movies_new (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, title TEXT NOT NULL, year INTEGER NOT NULL, rating REAL NOT NULL, poster_url TEXT, UNIQUE(user_id, title))"))
            connection.execute(text("INSERT INTO movies_new (user_id, title, year, rating, poster_url) SELECT COALESCE(user_id, 1), title, year, rating, COALESCE(poster_url, '') FROM movies"))
            connection.commit()
            connection.execute(text("DROP TABLE movies"))
            connection.execute(text("ALTER TABLE movies_new RENAME TO movies"))
            connection.commit()
        else:
            # Ensure poster_url exists (older migration)
            if "poster_url" not in columns:
                try:
                    connection.execute(text("ALTER TABLE movies ADD COLUMN poster_url TEXT"))
                    connection.commit()
                except Exception:
                    pass
        connection.commit()


def list_users():
    """Return list of (id, name) for all users."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, name FROM users ORDER BY name"))
        return result.fetchall()


def add_user(name):
    """Create a new user. Returns user id or None on error."""
    with engine.connect() as connection:
        try:
            connection.execute(text("INSERT INTO users (name) VALUES (:name)"), {"name": name.strip()})
            connection.commit()
            result = connection.execute(text("SELECT last_insert_rowid()"))
            return result.scalar()
        except Exception as e:
            print(f"Error: {e}")
            return None


def get_user_by_id(user_id):
    """Return (id, name) for user or None."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, name FROM users WHERE id = :id"), {"id": user_id})
        row = result.fetchone()
        return row


def list_movies(user_id):
    """Retrieve all movies for the given user."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating, poster_url FROM movies WHERE user_id = :user_id"),
            {"user_id": user_id},
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


def add_movie(user_id, title, year, rating, poster_url=None):
    """Add a new movie for the given user."""
    poster_url = poster_url if poster_url is not None else ""
    with engine.connect() as connection:
        try:
            connection.execute(
                text(
                    "INSERT INTO movies (user_id, title, year, rating, poster_url) "
                    "VALUES (:user_id, :title, :year, :rating, :poster_url)"
                ),
                {
                    "user_id": user_id,
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


def delete_movie(user_id, title):
    """Delete a movie for the given user."""
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text("DELETE FROM movies WHERE user_id = :user_id AND title = :title"),
                {"user_id": user_id, "title": title},
            )
            connection.commit()

            if result.rowcount == 0:
                print(f"Movie '{title}' not found.")
            else:
                print(f"Movie '{title}' deleted successfully.")
        except Exception as e:
            print(f"Error: {e}")


def update_movie(user_id, title, rating):
    """Update a movie's rating for the given user."""
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text("UPDATE movies SET rating = :rating WHERE user_id = :user_id AND title = :title"),
                {"user_id": user_id, "title": title, "rating": rating},
            )
            connection.commit()

            if result.rowcount == 0:
                print(f"Movie '{title}' not found.")
            else:
                print(f"Movie '{title}' updated successfully.")
        except Exception as e:
            print(f"Error: {e}")


# Run init after function defs so list_movies etc. exist when _init_db is called
_init_db()
