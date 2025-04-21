import os

# Root Paths
PATH_DATA = "data"
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

# Columns to Drop
GENRE_COLS_TO_DROP = [
    "backdrop_path",
    "homepage",
    "poster_path",
    "director_id",
    "star_id",
]
TMDB_COLS_TO_DROP = ["backdrop_path", "homepage", "poster_path"]

# Target Column Order
COLUMN_MAPPING = {
    "tmdb": {
        "id": "id",
        "imdb_id": "movie_id",
        "title": "title",
        "normalized_title": "normalized_title",
        "year": "year",
        "release_date": "release_date",
        "vote_average": "rating",
        "vote_count": "votes",
        "popularity": "popularity",
        "runtime": "runtime",
        "budget": "budget",
        "revenue": "worldwide_gross",
        "overview": "description",
        "genres": "genre",
        "original_language": "language",
        "production_companies": "production_companies",
        "tagline": "tagline",
        "keywords": "keywords",
        "status": "status",
        "adult": "adult",
        "original_title": "original_title",
        "production_countries": "production_countries",
        "spoken_languages": "spoken_languages",
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
        "Release Date": "release_date",
        "year": "year",
        "Production Budget": "production_budget",
        "Domestic Gross": "domestic_gross",
        "Worldwide Gross": "worldwide_gross",
    },
    "shared": {"decade": "decade"},
}

TMDB_COL_ORDER = ["id", "movie_id", "title", "normalized_title",
    "release_date", "year", "decade", "rating", "votes",
    "status",  "runtime", "adult", "budget", "revenue",
    "overview", "popularity", "tagline", "genres",
    "original_language", "original_title",
    "production_companies", "production_countries",
    "spoken_languages", "keywords"]

GENRE_COL_ORDER = ["movie_id", "title", "normalized_title",
    "year", "decade", "certificate", "runtime", "genre", "description", "rating",
    "votes", "director", "star", "total_gross"]

BUDGET_COL_ORDER = ["index", "title", "normalized_title", "release_date", "year", "decade",
    "production_budget", "domestic_gross", "worldwide_gross"]
