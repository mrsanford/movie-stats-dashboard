import os

# Root Paths
PATH_DATA = "data"
PROCESSED_DATA = "processed"
RAW_DATA = "raw"

RAW_PATH = os.path.join(PATH_DATA, RAW_DATA)
# DATA/RAW/* Paths
GENRES_RAW_PATH = os.path.join(RAW_PATH, "genres")
TMDB_RAW_PATH = os.path.join(RAW_PATH, "tmdb_movies")

PROCESSED_PATH = os.path.join(PATH_DATA, PROCESSED_DATA)
# DATA/PROCESSED/* Paths
BUDGET_OUTPUT_PATH = os.path.join(PROCESSED_PATH, "budgets.csv")
GENRES_OUTPUT_PATH = os.path.join(PROCESSED_PATH, "all_genres.csv")
TMDB_OUTPUT_PATH = os.path.join(PROCESSED_PATH, "tmdb.csv")
