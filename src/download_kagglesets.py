## DOWNLOADS THE DATASETS FROM KAGGLE VIA KAGGLEHUB ##
import os
import shutil
import kagglehub
from src.helpers import GENRES_RAW_PATH, TMDB_RAW_PATH


def download_tmdb_data(tmdb_path: str = TMDB_RAW_PATH) -> None:
    """
    Downloads the TMDB dataset from Kaggle and names the raw file 'tmdb.csv'
    """
    print(f"Downloading TMDB Movies Dataset to {tmdb_path}")

    # downloading dataset via kagglehub
    download_path = kagglehub.dataset_download(
        "asaniczka/tmdb-movies-dataset-2023-930k-movies"
    )
    print(f"Download complete. Raw files located at: {tmdb_path}")
    # ensuring the output directory exists
    os.makedirs(tmdb_path, exist_ok=True)
    # coping only .csv files into directed folder
    csv_files = [file for file in os.listdir(download_path) if file.endswith(".csv")]
    print(f"Found {len(csv_files)} CSV files in download.")
    for i, file in enumerate(csv_files):
        src = os.path.join(download_path, file)
        dst = os.path.join(tmdb_path, "tmdb.csv" if i == 0 else file)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            print(f"Copied: {file} → {dst}")
        else:
            print(f"Skipped (already exists): {file}")


def download_genre_data(genres_path: str = GENRES_RAW_PATH) -> None:
    """
    Downloads the genres data
    """
    # downloading dataset via kagglehub
    print(f"Downloading dataset from KaggleHub to {genres_path}")
    download_path = kagglehub.dataset_download(
        "rajugc/imdb-movies-dataset-based-on-genre"
    )
    print(f"Download complete. Raw files located at: {genres_path}")

    # ensuring the output directory exists
    os.makedirs(genres_path, exist_ok=True)
    # copying CSVs to genre folder
    csv_files = [file for file in os.listdir(download_path) if file.endswith(".csv")]
    print(f"Found {len(csv_files)} CSV files in download.")
    for file in csv_files:
        src = os.path.join(download_path, file)
        dst = os.path.join(genres_path, file)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            print(f"Copied: {file} → {dst}")
        else:
            print(f"Skipped (already exists): {file}")
    return
