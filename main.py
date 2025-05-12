from src.downloading.downloading import download_kaggle_dataset
from src.downloading.webscraping import webscrape_budgets
from src.processing.cleaning import (
    clean_tmdb_to_csv,
    clean_genres_to_csv,
    clean_budgets_to_csv,
)
from src.database.database import MovieDB
from src.dash.dashboard import run_app
from src.processing.merging import cleaning_and_merging
from src.utils.logging import clear_logs, logs_exist
from src.utils.helpers import (
    TMDB_RAW_PATH,
    GENRES_RAW_PATH,
    BUDGET_RAW_FILE,
    KAGGLE_TMDB,
    KAGGLE_IMDB,
    MOVIE_DB_PATH,
)
import os


def run_full_pipeline(
    tmdb_path: str = TMDB_RAW_PATH,
    genres_path: str = GENRES_RAW_PATH,
    budget_path: str = BUDGET_RAW_FILE,
):
    print("Welcome to MoVIZ!\n")

    def download_all_data():
        print("Starting download step...")
        download_kaggle_dataset(
            kaggle_id=KAGGLE_IMDB,
            output_dir=genres_path,
            target_filename=None,
            logger_name="genres_logger",
            log_filepath="genres_download",
        )
        download_kaggle_dataset(
            kaggle_id=KAGGLE_TMDB,
            output_dir=tmdb_path,
            target_filename=None,
            logger_name="tmdb_logger",
            log_filepath="tmdb_download",
        )
        webscrape_budgets(budget_path=budget_path, max_pages=1)

        # verify downloads
        genre_files = os.listdir(genres_path)
        tmdb_files = os.listdir(tmdb_path)
        if not genre_files or not tmdb_files or not os.path.exists(budget_path):
            raise RuntimeError("Download step failed: one or more files missing.")
        print("Download step verified.")

    def clean_all_datasets():
        print("Cleaning datasets...")
        clean_tmdb_to_csv()
        clean_genres_to_csv()
        clean_budgets_to_csv()

        # verify clean outputs
        clean_paths = [
            "data/processed/tmdb_movies_cleaned.csv",
            "data/processed/genres_cleaned.csv",
            "data/processed/budgets_cleaned.csv",
        ]
        for path in clean_paths:
            if not os.path.exists(path):
                raise RuntimeError(f"Cleaning step failed: {path} missing.")
        print("Cleaning step verified.")

    def prep_create_db():
        print("Merging and building database...")
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

        # verify DB
        try:
            db_check = MovieDB()
            db_check.run_query("SELECT COUNT(*) FROM tMovie;")
        except Exception as e:
            raise RuntimeError(f"Database build failed: {e}")
        print("Database build verified.")

    # step 1: checking if the logs exist
    logs_present = logs_exist()
    print(f"Logs present? {'Yes' if logs_present else 'No'}")

    # step 2: checking to see if the DB is properly populated
    db_exists = os.path.exists(MOVIE_DB_PATH)
    db_queryable = False
    if db_exists:
        try:
            test_db = MovieDB()
            test_db.run_query("SELECT 1;")
            db_queryable = True
        except Exception as e:
            print("Database exists but is not queryable:", e)

    # step 3: decision logic
    if not db_queryable:
        proceed = (
            input("Database is missing or corrupted. Rebuild from scratch? (y/n): ")
            .strip()
            .lower()
        )
        if proceed == "y":
            clear_logs()
            download_all_data()
            clean_all_datasets()
            prep_create_db()
        else:
            print("Aborting rebuild. Exiting.")
            return
    else:
        if input("Re-download datasets anyway? (y/n): ").strip().lower() == "y":
            download_all_data()
        if input("Re-clean datasets anyway? (y/n): ").strip().lower() == "y":
            clean_all_datasets()
        if (
            input("Rebuild the database from cleaned CSVs? (y/n): ").strip().lower()
            == "y"
        ):
            prep_create_db()

    # step 4: launch app
    if input("Launch the MoVIZ dashboard? (y/n): ").strip().lower() == "y":
        run_app()
    else:
        print("Dashboard not launched. Run `run_app()` manually later.")


if __name__ == "__main__":
    # run_full_pipeline()
    run_app()
