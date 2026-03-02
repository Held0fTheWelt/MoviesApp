import random
import time
from difflib import get_close_matches
from statistics import median

import matplotlib.pyplot
import plotext

import movie_storage as storage
import movies_plots
import movies_website

ABORT_MESSAGE = "Abort"


def movies_database_is_not_empty(movies):
    """ Checks if the database is empty"""
    if len(movies) == 0:
        print("No movies found.")
        return False
    return True


def get_movie_year(option=0):
    """Gets a movie release year from input.

    option:
      0 -> required year (adding a movie)
      1 -> optional start year (filter; blank = None)
      2 -> optional end year (filter; blank = None)
    """
    while True:
        prompt = "Enter year of release: "
        if option == 1:
            prompt = "Enter start year of releases (leave blank for no start year): "
        elif option == 2:
            prompt = "Enter end year of release (leave blank for no end year): "

        year_input = input(prompt).strip()

        if year_input.lower() == ABORT_MESSAGE.lower():
            print("\033[0;33mOperation aborted. Returning to menu...\033[0;0m")
            time.sleep(1)
            return None

        if option in (1, 2) and year_input == "":
            return None

        try:
            year = int(year_input)
        except ValueError:
            print("\033[0;31mInvalid input: Please enter a numeric year.\033[0;0m")
            continue

        if 1920 < year <= 2026:
            return year

        print("\033[0;31mError: Year of release has to be between "
              "1921 and 2026 inclusive.\033[0;0m")


def get_movie_title(second_option=False):
    """ Gets a movies title for a new movie from input"""
    title = ""
    while True:
        print('\nEnter "Abort" to cancel this operation')
        if second_option is True:
            title = input("Enter part of movie name: ").strip()
        else:
            title = input("Enter movie name: ").strip()

        if title.lower() == ABORT_MESSAGE.lower():
            print("\033[0;33mOperation aborted. Returning to menu...\033[0;0m")
            time.sleep(1)
            title = None
            break

        if title == "":
            if second_option is True:
                print("\033[0;31mError: Part of movie title cannot be empty. \033[0;0m")
            else:
                print("\033[0;31mError: Movie title cannot be empty.\033[0;0m")
        else:
            break
    return title


def get_movie_rating(option=0):
    """Gets a rating from input.

    option:
      0 -> required rating (add/update)
      1 -> optional minimum rating (filter; blank = None)
    """
    while True:
        prompt = "Enter Movie rating (1.0 - 10.0): "
        if option == 1:
            prompt = "Enter Minimum Movie rating (1.0 - 10.0) (leave blank for no minimum rating): "

        rating_input = input(prompt).strip()

        if rating_input.lower() == ABORT_MESSAGE.lower():
            print("\033[0;33mOperation aborted. Returning to menu...\033[0;0m")
            time.sleep(1)
            return None

        if option == 1 and rating_input == "":
            return None

        try:
            rating = float(rating_input)
        except ValueError:
            print("\033[0;31mInvalid input: Please enter a numeric value for the rating.\033[0;0m")
            continue

        if 1.0 < rating <= 10.0:
            return rating

        print("\033[0;31mError: Rating must be greater than 1.0 and no greater than 10.\033[0;0m")


def add_movie(movies):
    """ Adds a movie to the movies database"""
    title = get_movie_title()
    rating = get_movie_rating()
    year = get_movie_year()

    if title is None or rating is None or year is None:
        return

    if title not in movies:
        storage.add_movie(title, year, rating)
        movies[title] = {"rating": rating, "year": year}
        print(f"\033[0;32mSuccess: '{title}' added (year {year}) with a "
              f"rating of {rating}.\033[0;0m")
    else:
        print(f"Movie '{title}' is already present in the list of movies.")


def remove_movie(movies):
    """ Removes a movie from the movies database"""
    title = get_movie_title()

    if title is None:
        return

    if title in movies.keys():
        print(f"Deleting movie {title} from database.")
        storage.delete_movie(title)
        print(f"\033[0;32mSuccess: '{title}' deleted from dictionary.\033[0;0m")
        time.sleep(0.25)
        print("Returning to menu")
        time.sleep(0.2)
        print()
    else:
        print("\033[0;33mMovie does not exist in movie database. Returning to menu\033[0;0m")
        print()


def update_movie(movies):
    """ Updates a movie in the movies database"""
    title = get_movie_title()

    if title is None:
        return

    if title in movies.keys():
        print(f"Updating movie {title} from database.")
        rating = get_movie_rating()
        storage.update_movie(title, rating)
        print(f"\033[0;32mSuccess: '{title}' updated with a "
              f"rating of {rating}.\033[0;0m")
    else:
        print(f"movie {title} not in database. Trying improved fuzzy research")
        improved_fuzzy_search(movies, title)


def filter_movies(movies):
    """ filter a list of movies based on specific criteria"""
    if movies_database_is_not_empty(movies):
        minimum_rating = get_movie_rating(1)
        start_year = get_movie_year(1)
        end_year = get_movie_year(2)

        print("Filtered Movies:")
        filtered = {}
        for title, values in movies.items():
            rating = values["rating"]
            year = values["year"]

            if minimum_rating is not None and rating < minimum_rating:
                continue
            if start_year is not None and year < start_year:
                continue
            if end_year is not None and year > end_year:
                continue

            filtered[title] = values

        if filtered:
            print("\nFiltered Movies:")
            for title, values in filtered.items():
                print(f"{title} ({values['year']}): {values['rating']}")
        else:
            print("\nNo movies match your criteria.")
        print()
        print()


def random_movie(movies):
    """ Prints out a random movie of the movies database"""
    if movies_database_is_not_empty(movies):
        title, values = random.choice(list(movies.items()))
        print(f"Your new random movie is {title} was released in the year {values['year']}"
              f" and it has a rating of {values['rating']}.")
        print()
        print()


def improved_fuzzy_search(movies, search_term):
    """ Uses fuzzy search logic on a search term, if a search was unsuccessful
        to assist wrong input"""
    if movies_database_is_not_empty(movies):
        movie_titles = list(movies.keys())

        matches = get_close_matches(search_term, movie_titles, n=5, cutoff=0.4)

        if matches:
            print(f'\033[0;33mMovies with {search_term} do not exist. Did you mean:\033[0;0m')
            for title in matches:
                print(f"  {title}")
        else:
            print(f'\033[0;33mMovies with {search_term} do not exist\033[0;0m"')
        print()


def search_movies(movies):
    """Searches for movies by (partial) title. Falls back to fuzzy suggestions."""
    if not movies_database_is_not_empty(movies):
        return

    search_term = get_movie_title(True)
    if search_term is None:
        return

    found = False
    for title, values in movies.items():
        if search_term.lower() in title.lower():
            print(
                f'{search_term} is in the name "{title}" and it has a rating of '
                f'{values["rating"]} and is from the year {values["year"]}.'
            )
            found = True

    if not found:
        improved_fuzzy_search(movies, search_term)

    print("")

    time.sleep(2)


def get_average_rating(movies):
    """ Calculates the average rating in the movies database """
    if movies_database_is_not_empty(movies):
        average = 0
        for movie in movies:
            average = average + movies[movie]["rating"]
        return average / len(movies)
    return None


def get_median_rating(movies):
    """ Returns median of the movies database """
    ratings = [movie["rating"] for movie in movies.values()]
    return median(ratings)


def get_best_movie(movies):
    """ Gets the best movie from the list of movies """
    best_value = max(movie["rating"] for movie in movies.values())
    return {title: data for title, data in movies.items() if data["rating"] == best_value}


def get_worst_movie(movies):
    """ Gets the worst movie from the list of movies """
    worst_value = min(movie["rating"] for movie in movies.values())
    return {title: data for title, data in movies.items() if data["rating"] == worst_value}


def print_movies_information(movies, best=True):
    """ Prints out information about the movies """
    if len(movies.items()) > 1:
        rating = 0
        if best:
            if len(movies.items()) > 1:
                for title, values in movies.items():
                    print(f"One of the best movies is {title} from the year {values['year']}")
                    rating = values['rating']
                print(f"They all have a rating of: {rating}")
            else:
                title, values = list(movies.items())[0]
                print(f"Best movie is {title} from the year {values['year']} "
                      f"with a rating of: {values['rating']}")
        else:
            if len(movies.items()) > 1:
                rating = 0
                for movie, values in movies.items():
                    print(f"One of the worst movies is {movie} from the year {values['year']}")
                    rating = values['rating']
                print(f"They all have a rating of: {rating}")
            else:
                title, values = list(movies.items())[0]
                print(f"Worst movie is {title} from the year {values['year']} "
                      f"with a rating of: {values['rating']}")


def stats(movies):
    """Prints stats about the movie database."""
    if not movies_database_is_not_empty(movies):
        return

    avg = get_average_rating(movies)
    if avg is None:
        return

    print(f"Average movie rating is {avg:.1f}")
    print(f"Median movie rating is {get_median_rating(movies):.1f}")
    print_movies_information(get_best_movie(movies))
    print_movies_information(get_worst_movie(movies))
    print()


def print_all_movies_data(movies):
    """ Prints all movies data """
    if len(movies) > 1:
        print(f"{len(movies)} movies in total")
    else:
        print(f"{len(movies)} movie in total")

    for title, values in movies:
        print(f"Title: {title}: -- Rating: {values['rating']} -- Year of Release: {values['year']}")
    print("")


def get_sort_option():
    """ Asks for sort option "rating" or "year" """
    option = ""
    while True:
        option = input("Enter sort option (rating or year): ").strip()
        if option.lower() == "rating" or option.lower() == "year":
            break
        print('Only "rating" or "year" as input allowed')
    return option.lower() == "rating"


def sorted_movies(movies):
    """ sorts movie by rating or year based on chosen option"""
    option = get_sort_option()
    movies_sorted = {}
    if option:
        movies_sorted = sorted(movies.items(), key=lambda item: item[1]["rating"], reverse=True)
    else:
        movies_sorted = sorted(movies.items(), key=lambda item: item[1]["year"])
    print_all_movies_data(movies_sorted)


def sorted_by_name(movies):
    """ Sorts movies by name ascending """
    movies_sorted = sorted(movies.items())
    print_all_movies_data(movies_sorted)


def create_plotext_histogram(ratings):
    """ Creates a histogram in the console"""
    plotext.hist(ratings, bins=10)
    plotext.title("Movie Rating Histogram")
    plotext.xlabel("Rating")
    plotext.ylabel("Movie Count")
    plotext.show()


def create_matplotlib_histogram(ratings):
    """ creates a histogram and saves it to png"""
    filename = input("name of file (i.e. histogram.png): ")

    matplotlib.pyplot.figure(figsize=(10, 6))
    matplotlib.pyplot.hist(ratings, bins=10, edgecolor='black', color='steelblue')
    matplotlib.pyplot.xlabel('Rating')
    matplotlib.pyplot.ylabel('Movie Count')
    matplotlib.pyplot.title('Movie Rating Histogram')

    matplotlib.pyplot.savefig(filename)
    matplotlib.pyplot.close()

    print(f"Histogram saved as: {filename}")


def create_rating_histogram(movies):
    """Asks for option of console or png histogram, then calls function"""
    option = ""
    while True:
        option = input("Enter histogram option (console or png): ").strip()
        if option.lower() == "console" or option.lower() == "png":
            break
        print('Only "console" or "png" as input allowed')
    ratings = [movie["rating"] for movie in movies.values()]
    if option == "console":
        create_plotext_histogram(ratings)
    elif option == "png":
        create_matplotlib_histogram(ratings)
    print()
    print()


def run_choice(choice, movies):
    """ Runs the chosen functionality by accessing corresponding function """
    if choice == 1:
        sorted_by_name(movies)
    elif choice == 2:
        add_movie(movies)
    elif choice == 3:
        remove_movie(movies)
    elif choice == 4:
        update_movie(movies)
    elif choice == 5:
        stats(movies)
    elif choice == 6:
        random_movie(movies)
    elif choice == 7:
        search_movies(movies)
    elif choice == 8:
        sorted_movies(movies)
    elif choice == 9:
        create_rating_histogram(movies)
    elif choice == 10:
        filter_movies(movies)
    elif choice == 11:
        create_rating_histogram(movies)


def get_choice():
    """ Asks for user input to choose movies system functionality """
    choice = 0
    while choice == 0 or choice > 12:
        choiceinput = input("Enter choice (1-12): ")
        try:
            choice = int(choiceinput)
            if choice < 1 or choice > 12:
                print("\033[0;31mError: Please enter a number between 1 and 12.\033[0;0m")
        except ValueError:
            print("\033[0;31mInvalid input. Please enter a whole number.\033[0;0m")
            choice = 0  # Reset choice to stay in the loop
    print("")
    return choice


def show_menu():
    """ Prints the menu to screen"""
    print("*" * 10 + "My Movies Database" + "*" * 10)
    print("")
    print("Menu:")
    print("1. List movies")
    print("2. Add movie")
    print("3. Delete movie")
    print("4. Update movie")
    print("5. Stats")
    print("6. Random movie")
    print("7. Search movie")
    print("8. Movies sorted by rating or year")
    print("9. Create Rating Histogram")
    print("10. Filter Movies")
    print("11. Generate Website")
    print("12. Exit")
    print("")


def main():
    """ Main function of the movies data system"""
    movies = storage.get_movies()  # Load from JSON

    # if JSON is empty
    if not movies:
        # Dictionary to store the movies and the rating
        movies = {
            "The Shawshank Redemption": {"rating": 4.5, "year": 1994},
            "Pulp Fiction": {"rating": 4.8, "year": 1994},
            "The Room": {"rating": 3.6, "year": 2003},
            "The Godfather": {"rating": 9.2, "year": 1972},
            "The Godfather: Part II": {"rating": 3.0, "year": 1974},
            "The Dark Knight": {"rating": 2.0, "year": 2008},
            "The Dark": {"rating": 2.0, "year": 2008},
            "12 Angry Men": {"rating": 6.9, "year": 1957},
            "Everything Everywhere All At Once": {"rating": 8.9, "year": 2022},
            "Forrest Gump": {"rating": 8.8, "year": 1994},
            "Star Wars: Episode V": {"rating": 8.7, "year": 1980}
        }
        storage.save_movies(movies)

    while True:
        show_menu()
        choice = get_choice()
        if choice == 12:
            break
        run_choice(choice, movies)
        time.sleep(1)


if __name__ == "__main__":
    main()
