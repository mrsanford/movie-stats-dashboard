from src.downloading.downloading import download_kaggle_dataset
from src.downloading.webscraping import webscrape_budgets
from src.processing.cleaning import clean_tmdb_to_csv, clean_genres_to_csv, clean_budgets_to_csv
from src.processing.merging import cleaning_and_merging
from src.utils.logging import clear_logs
from src.utils.helpers import TMDB_RAW_PATH, GENRES_RAW_PATH, BUDGET_RAW_FILE, KAGGLE_TMDB, KAGGLE_IMDB
from src.database.database import MovieDB
from src.dash.dashboard import run_app


def run_full_pipeline(tmdb_path: str = TMDB_RAW_PATH,
    genres_path: str = GENRES_RAW_PATH, budget_path: str = BUDGET_RAW_FILE):
    clear_logs()

    def download_all_data(budget_path: str = budget_path) -> None:
        """
        Downloads the used data from Kaggle and webscrapes The-Numbers.com data
        """
        download_kaggle_dataset(kaggle_id=KAGGLE_IMDB, output_dir=genres_path,
        target_filename=None, logger_name="genres_logger", log_filepath="genres_download")
        download_kaggle_dataset(kaggle_id=KAGGLE_TMDB, output_dir=tmdb_path,
        target_filename=None, logger_name="tmdb_logger", log_filepath="tmdb_download")
        webscrape_budgets(budget_path=budget_path, max_pages=1)
        return None

    def clean_all_datasets() -> None:
        clean_tmdb_to_csv()
        clean_genres_to_csv()
        clean_budgets_to_csv()
        return None
    
    def prep_create_db() -> None:
        movies_df, budgets_df, genre_table, movie_genre_links = cleaning_and_merging(export=False)
        db = MovieDB(create=True)
        db.load_from_dataframes(movies_df=movies_df, budgets_df=budgets_df,
                genre_table=genre_table, movie_genre_links=movie_genre_links)
        return None


run_app()

