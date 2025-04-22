from src.dataframe_cleaning import (
    clean_tmdb_to_csv,
    clean_genres_to_csv,
    clean_budgets_to_csv,
)
from src.download_kagglesets import (
    download_tmdb_data,
    download_genre_data,
)
from src.helpers import TMDB_RAW_PATH, GENRES_RAW_PATH, BUDGET_RAW_FILE
from src.budget_webscraping import webscrape_budgets


def download_all_data(
    tmdb_path: str = TMDB_RAW_PATH,
    genres_path: str = GENRES_RAW_PATH,
    budget_path: str = BUDGET_RAW_FILE,
) -> None:
    """
    Downloads the used data from Kaggle and webscrapes The-Numbers.com data
    """
    download_tmdb_data(tmdb_path=tmdb_path)
    download_genre_data(genres_path=genres_path)
    webscrape_budgets(budget_path=budget_path, max_pages=1)
    return None


def clean_all_data():
    clean_tmdb_to_csv()
    clean_genres_to_csv()
    clean_budgets_to_csv()
    return None


download_all_data()
