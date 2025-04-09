import os
import glob
import pandas as pd
from src.helpers import (
    GENRES_RAW_PATH,
    TMDB_RAW_PATH,
    GENRES_OUTPUT_PATH,
    TMDB_OUTPUT_PATH,
)


def clean_genre_data(
    genres_path: str = GENRES_RAW_PATH, output_path: str = GENRES_OUTPUT_PATH
) -> None:
    """
    Cleans and consolidates multiple genre csvs outputted from download_genre_data()
    into single output file
    ---
    Args:
        genres_path (str) is the path to the genres folder with the raw genres csvs
        output_path (str) is the path to the single clean genre data csv
    Returns: None
    """
    # Loads in all CSV files from genre directory
    csv_files = glob.glob(os.path.join(genres_path, "*.csv"))
    # Reading reach CSV file into a DataFrame and stores in list
    dfs = [pd.read_csv(f) for f in csv_files]
    # Combines all DataFrame via stacking rows
    combined = pd.concat(dfs, ignore_index=True)

    # Removing any duplicate rows based on 'movie_id'
    combined = combined.drop_duplicates(subset="movie_id")

    # Drops columns unnecessary to the analysis
    cols_to_drop = [
        "backdrop_path",
        "homepage",
        "poster_path",
        "director_id",
        "star_id",
    ]
    # Only dropping columns if exists in datasets
    combined = combined.drop(
        columns=[col for col in cols_to_drop if col in combined.columns]
    )

    # sorting dataframe alphabetically by movie_name
    if "movie_name" in combined.columns:
        combined = combined.sort_values("movie_name")
    # resetting the index
    combined = combined.reset_index(drop=True)
    # outputting results to csv
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    combined.to_csv(output_path, index=False)
    return None


def clean_tmdb_data(
    tmdb_path: str = TMDB_RAW_PATH, output_path: str = TMDB_OUTPUT_PATH
) -> None:
    """
    Cleans and consolidates TMDB csv and has additional functionality if >1 TMDB csv
    Note: there should only be a single csv; however, adjustments have been included if the kaggle data's
    storage conventions change in the future
    ---
    Args:
        tmdb_path (str) is the path to the folder containing raw TMDB csv file(s)
        output_path (str) is the path to the cleaned TMDB data csv
    Returns: None
    """
    # Loads CSV files from TMDB directory
    csv_files = glob.glob(os.path.join(tmdb_path, "*.csv"))
    # Reads each CSV file and stores in a list of DataFrames
    dfs = [pd.read_csv(f) for f in csv_files]
    # Combines all dataframes into one via stacking rows, or uses single file if only 1
    data = dfs[0] if len(dfs) == 1 else pd.concat(dfs, ignore_index=True)

    # Converting 'id' to string and avoiding type errors when dropping duplicates
    data["id"] = data["id"].astype(str)
    data = data.drop_duplicates(subset="id")

    # Removing rows where title is missing or empty
    data = data[data["title"].notna() & (data["title"].str.strip() != "")]
    # Dropping rows where all of runtime, revenue, and budget are NaN or 0
    data = data[
        ~(
            (data["runtime"].fillna(0) == 0)
            & (data["revenue"].fillna(0) == 0)
            & (data["budget"].fillna(0) == 0)
        )
    ]
    # Filtering results for only released movies
    data = data[data["status"] == "Released"]
    # Dropping unused image/path columns
    data = data.drop(
        ["backdrop_path", "homepage", "poster_path"], axis=1, errors="ignore"
    )

    # Sorting dataframe alphabetically by movie title
    data = data.sort_values(by="title", ascending=True)
    # Resetting the index
    data.reset_index(drop=True, inplace=True)
    # Saving the cleaned dataset
    data.to_csv(output_path, index=False)
    return


def clean_kaggle_data() -> None:
    clean_genre_data()
    clean_kaggle_data
    return None
