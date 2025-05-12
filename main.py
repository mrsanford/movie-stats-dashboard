import os
from src.utils.logging import logs_exist, clear_logs
from src.database.database import MovieDB
from src.processing.merging import cleaning_and_merging
from src.downloading.downloading import download_kaggle_dataset
from src.downloading.webscraping import webscrape_budgets
from src.processing.cleaning import (
    clean_tmdb_to_csv,
    clean_genres_to_csv,
    clean_budgets_to_csv,
)
from src.utils.helpers import (
    TMDB_RAW_PATH,
    GENRES_RAW_PATH,
    BUDGET_RAW_FILE,
    KAGGLE_TMDB,
    KAGGLE_IMDB,
    MOVIE_DB_PATH,
)
from src.dash.dashboard import run_app


def check_data_ready():
    print("Checking existing data status...")
    # checking if logs exist
    if not logs_exist():
        print("Logs are missing. Data may be outdated.")
        return False
    # checking if the database exists and is queryable
    if not os.path.exists(MOVIE_DB_PATH):
        print("Database file is missing.")
        return False
    try:
        db = MovieDB()
        db.run_query("SELECT 1;")
        print("Database is present and queryable.")
        return True
    except Exception as e:
        print(f"Database exists but is not queryable: {e}")
        return False


def run_data_pipeline(max_pages=63):
    print("Running data pipeline: download, clean, merge, database build...")

    # download datasets
    print("Downloading datasets...")
    download_kaggle_dataset(
        kaggle_id=KAGGLE_IMDB,
        output_dir=GENRES_RAW_PATH,
        target_filename=None,
        logger_name="genres_logger",
        log_filepath="genres_download",
    )
    download_kaggle_dataset(
        kaggle_id=KAGGLE_TMDB,
        output_dir=TMDB_RAW_PATH,
        target_filename=None,
        logger_name="tmdb_logger",
        log_filepath="tmdb_download",
    )
    webscrape_budgets(budget_path=BUDGET_RAW_FILE, max_pages=max_pages)
    print("Dataset download completed.")
    print("Cleaning datasets...")
    clean_tmdb_to_csv()
    clean_genres_to_csv()
    clean_budgets_to_csv()
    print("Dataset cleaning completed.")

    # merges datasets and builds database
    print("Merging datasets and building database...")
    movies_df, budgets_df, genre_table, movie_genre_links = cleaning_and_merging(
        export=False
    )
    db = MovieDB(create=True)
    db.load_from_dataframes(
        movies_df=movies_df,
        budgets_df=budgets_df,
        genre_table=genre_table,
        movie_genre_links=movie_genre_links,
    )
    print("Database build completed.")


if __name__ == "__main__":
    if check_data_ready():
        print("Data is ready. Launching dashboard...")
        run_app()
    else:
        proceed = (
            input("Data is missing or invalid. Run data pipeline to rebuild? (y/n): ")
            .strip()
            .lower()
        )
        if proceed == "y":
            clear_logs()
            run_data_pipeline()
            print("Pipeline completed. Launching dashboard...")
            run_app()
        else:
            print("Exiting without launching dashboard.")
