import os

# Root Paths
PATH_DATA = "data"
LOGS_DATA = "logs"
PROCESSED_DATA = "processed"
RAW_DATA = "raw"

RAW_PATH = os.path.join(PATH_DATA, RAW_DATA)
# DATA/RAW/* Paths
GENRES_RAW_PATH = os.path.join(RAW_PATH, "genres")
TMDB_RAW_PATH = os.path.join(RAW_PATH, "tmdb_movies")
BUDGET_RAW_PATH = os.path.join(RAW_PATH, "budgets")
## DATA/RAW/FILE
BUDGET_RAW_FILE = os.path.join(BUDGET_RAW_PATH, "budgets.csv")

PROCESSED_PATH = os.path.join(PATH_DATA, PROCESSED_DATA)
# DATA/PROCESSED/* Paths
GENRES_OUTPUT_PATH = os.path.join(PROCESSED_PATH, "genres.csv")
TMDB_OUTPUT_PATH = os.path.join(PROCESSED_PATH, "tmdb.csv")
BUDGET_OUTPUT_PATH = os.path.join(PROCESSED_PATH, "budgets.csv")

# Kaggle IDs (username/dataset)
KAGGLE_TMDB = "asaniczka/tmdb-movies-dataset-2023-930k-movies"
KAGGLE_IMDB = "rajugc/imdb-movies-dataset-based-on-genre"

# Columns to Drop
GENRE_COLS_TO_DROP = [
    "backdrop_path",
    "homepage",
    "poster_path",
    "director_id",
    "star_id",
]
TMDB_COLS_TO_DROP = ["backdrop_path", "homepage", "poster_path"]

# Target Column Mapping and Declaring the Order
COLUMN_MAPPING = {
    "tmdb": {
        "id": "id",
        "imdb_id": "movie_id",
        "title": "title",
        "normalized_title": "normalized_title",
        "release_date": "release_date",
        "year": "year",
        "vote_average": "rating",
        "vote_count": "votes",
        "popularity": "popularity",
        "genres": "genre",
        "status": "status",
        "runtime": "runtime",
        "adult": "adult",
        "budget": "budget",
        "revenue": "worldwide_gross",
        "overview": "description",
        "tagline": "tagline",
        "keywords": "keywords",
        "original_title": "original_title",
        "original_language": "language",
        "spoken_languages": "spoken_languages",
        "production_companies": "production_companies",
        "production_countries": "production_countries",
    },
    "genres": {
        "movie_id": "movie_id",
        "movie_name": "title",
        "normalized_movie_name": "normalized_title",
        "year": "year",
        "certificate": "certificate",
        "runtime": "runtime",
        "genre": "genre",
        "description": "description",
        "rating": "rating",
        "votes": "votes",
        "director": "director",
        "star": "star",
        "total_gross": "total_gross",
    },
    "budget": {
        "Index": "index",
        "Movie": "title",
        "normalized_title": "normalized_title",
        "normalized_title_year" : "normalized_title_year",
        "Release Date": "release_date",
        "year": "year",
        "Production Budget": "production_budget",
        "Domestic Gross": "domestic_gross",
        "Worldwide Gross": "worldwide_gross",
    },
    "shared": {"decade": "decade"},
}

# Pruned Analysis Columns
PRUNED_TMDB_COLS = ['movie_id', 'title', 'normalized_title', 'normalized_title_year',
                    'release_date', 'year', 'decade', 'rating', 'votes', 'runtime',
                    'genre', 'budget', 'worldwide_gross', 'description', 'production_countries']

PRUNED_GENRE_COLS = ['movie_id', 'title', 'normalized_title', 'normalized_title_year', 'certificate',
                     'year', 'decade', 'rating', 'votes', 'runtime', 'genre', 'description']

PRUNED_BUDGET_COLS = ['title', 'normalized_title', 'normalized_title_year',
                      'release_date', 'year', 'decade', 'production_budget',
                      'domestic_gross', 'worldwide_gross']

# Critical Columns (for Merge)
TMDB_CRIT_COLS = ['movie_id', 'title', 'normalized_title', 'year','decade']
GENRES_CRIT_COLS = ['movie_id', 'title', 'normalized_title', 'year','decade']
BUDGET_CRIT_COLS = ['title', 'normalized_title', 'year', 'decade']

# Ratings Mapping
RATING_MAP = {
    # Rated G
    "G": "G",
    "TV-G": "G",
    "U": "G",
    "E": "G",
    "E10+": "G",
    "TV-Y": "G",
    # Rated PG
    "PG": "PG",
    "TV-PG": "PG",
    "TV-Y7": "PG",
    "M": "PG",
    "UA": "PG",
    "M/PG": "PG",
    "Open": "PG",
    "UA 7+": "PG",
    "GP": "PG",
    "TV-Y7-FV": "PG",
    # Rated PG-13
    "PG-13": "PG-13",
    "TV-14": "PG-13",
    "13+": "PG-13",
    "TV-13": "PG-13",
    "UA 13+": "PG-13",
    "13": "PG-13",
    # Rated R
    "R": "R",
    "TV-MA": "R",
    "16": "R",
    "16+": "R",
    "18": "R",
    "18+": "R",
    "UA 16+": "R",
    "MA-13": "R",
    "MA-17": "R",
    # Rated NC-17
    "NC-17": "NC-17",
    "X": "NC-17",
    "AO": "NC-17",
    # Others
    "Approved": "Approved",
    "Passed": "Passed",
    "Unrated": "Unrated",
    "Not Rated": "NR",
}
