import pandas as pd
import ast
from typing import List
from src.utils.logging import setup_logger
from src.utils.helpers import TMDB_CRIT_COLS, GENRES_CRIT_COLS, BUDGET_CRIT_COLS
from src.processing.cleaning import (
    clean_tmdb_to_csv,
    clean_genres_to_csv,
    clean_budgets_to_csv,
)


# drop the null values first in tmdb, genres, and budgets
def drop_null_in_valid(df: pd.DataFrame, critical_cols: List[str]) -> pd.DataFrame:
    """
    Drops rows where any critical column value equals NaN, and rows where more
    than 80% of non-critical columns are NaN.
    ---
    Args:
        df (pd.DataFrame): input DataFrame
        critical_cols (List[str]): list of critical columns to check
    Returns:
        pd.DataFrame: cleaned DataFrame with invalid rows removed
    """
    df = df.dropna(subset=[col for col in critical_cols if col in df.columns])
    non_critical_cols = [col for col in df.columns if col not in critical_cols]
    if non_critical_cols:
        max_missing_allowed = int(0.8 * len(non_critical_cols))
        df = df[df[non_critical_cols].isnull().sum(axis=1) < max_missing_allowed]
    return df


## merging tmdb and genres on movie_ids
def merge_movie_ids(
    df1: pd.DataFrame, df2: pd.DataFrame, type: str = "left"
) -> pd.DataFrame:
    """
    Merges the TMDV and genres DataFrames based on movie_id using target join 'type'
    ---
    Args:
        df1 (pd.DataFrame), df2 (pd.DataFrame): the target dataframe
        type (str): the type of join
    Returns:
        pd.DataFrame merged on 'movie_id'
    """
    logger = setup_logger("movie_id_merger", "merge_datasets")
    if "movie_id" not in df1.columns or "movie_id" not in df2.columns:
        raise ValueError("Both DataFrames must contain a 'movie_id' column.")
    merged_df = df1.merge(df2, on="movie_id", how=type)
    logger.info(f"Successfully merged {len(merged_df)} rows")
    return merged_df


def assign_budget_movie_id(
    budgets_df: pd.DataFrame, tmdb_df: pd.DataFrame, genres_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Matches budgets to movies by merging on normalized_title + year
    First tries to match with TMDB, then falls back on the genres dataset
    Any remaining unmatched budget rows are dropped
    """
    logger = setup_logger("budget_merger", "merge_datasets")
    # merging with TMDB on normalized_title + year
    merged = budgets_df.merge(
        tmdb_df[["normalized_title", "year", "movie_id"]],
        on=["normalized_title", "year"],
        how="left",
    )
    logger.info(f"Number of matched rows: {len(merged)} rows")
    # checking unmatched rows (still missing movie_id)
    unmatched = merged[merged["movie_id"].isna()]
    logger.info(f"Remaining {len(unmatched)} rows")
    if not unmatched.empty:
        unmatched = unmatched.drop(columns=["movie_id"])
        unmatched = unmatched.merge(
            genres_df[["normalized_title", "year", "movie_id"]],
            on=["normalized_title", "year"],
            how="left",
        )
        matched = merged[~merged["movie_id"].isna()]
        merged = pd.concat([matched, unmatched], ignore_index=True)
    merged = merged.dropna(subset=["movie_id"]).reset_index(drop=True)
    logger.info(f"There were {len(merged)} still unmatched -> dropped")
    return merged


def clean_merged_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans up duplicated columns (resolving _x and _y) after the merge
    Prefers values from _x columns but falls back to _y if needed
    Removes the suffixed columns and replaces them with the single clean column
    """
    new_df = df.copy()
    for col in new_df.columns:
        if col.endswith("_x"):
            base_col = col[:-2]
            corresponding_y = base_col + "_y"
            if corresponding_y in new_df.columns:
                new_df[base_col] = new_df[col].combine_first(new_df[corresponding_y])
                new_df = new_df.drop(columns=[col, corresponding_y])
    return new_df


def fix_genre_strings(df: pd.DataFrame, genre_col: str = "genre") -> pd.DataFrame:
    """
    Converts genre column values from string representations to actual Python lists
    """
    df = df.copy()
    df[genre_col] = df[genre_col].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )
    return df


def create_genre_table(df: pd.DataFrame, genre_col: str = "genre") -> pd.DataFrame:
    """
    Builds a genre lookup table from all unique genre names in the dataset
    """
    # flattens all genres into a single list
    all_genres = set(genre for sublist in df[genre_col] for genre in sublist)
    # creates genre table
    genre_table = pd.DataFrame(
        {"genre_id": range(1, len(all_genres) + 1), "genre_name": sorted(all_genres)}
    )
    return genre_table


def create_movie_genre_links(
    df: pd.DataFrame, genre_table: pd.DataFrame, genre_col: str = "genre"
) -> pd.DataFrame:
    """
    Explodes the genres list in the movie DataFrame -> each row is single movie-genre pair
    Merges with the genre lookup table to get the corresponding genre_id
    ---
    Returns:
        pd.DataFrame of two columns with movie_id and genre_id
    """
    # explodes the genres first
    exploded = df[["movie_id", genre_col]].explode(genre_col)
    # merges to get genre_id
    link_table = exploded.merge(
        genre_table, left_on=genre_col, right_on="genre_name", how="left"
    )[["movie_id", "genre_id"]]
    return link_table


# final cleaning and merging steps put together
def cleaning_and_merging(
    tmdb_crit_cols: List[str] = TMDB_CRIT_COLS,
    genres_crit_cols: List[str] = GENRES_CRIT_COLS,
    budgets_crit_cols: List[str] = BUDGET_CRIT_COLS,
    export: bool = False,
) -> pd.DataFrame:
    """
    Cleans and merges MoVIZ's datasets in preparation for
    database ingestion
    """
    logger = setup_logger("finalizing_clean", "merge_datasets")
    logger.info("Beginning final clean and merge")
    # Raw to Processed DataFrames
    tmdb_df = clean_tmdb_to_csv(export=False)
    genres_df = clean_genres_to_csv(export=False)
    budgets_df = clean_budgets_to_csv(export=False)
    logger.info("Cleaning complete on raw datasets. Raw files loaded")
    # Dropping Additional Null Values in Processed Critical Columns
    logger.info("Dropping null values in critical columns")
    tmdb_df = drop_null_in_valid(tmdb_df, tmdb_crit_cols)
    genres_df = drop_null_in_valid(genres_df, genres_crit_cols)
    budgets_df = drop_null_in_valid(budgets_df, budgets_crit_cols)
    logger.info("Null filtering complete")
    # Implementing the TMDB-Genres Merge and Cleaning the Columns
    tmdb_genres_merge = merge_movie_ids(tmdb_df, genres_df)
    movies_master = clean_merged_columns(tmdb_genres_merge)
    logger.info(f"Merged movies DataFrame shape: {len(movies_master.shape)}")
    # Assigning movie_id for Budgets
    budgets_df = assign_budget_movie_id(budgets_df, tmdb_df, genres_df)
    logger.info(f"Budget DataFrame cleaned: {budgets_df.shape[0]} rows")
    # Parsing genre column from string to List[str] format
    movies_master = fix_genre_strings(movies_master)
    logger.info("Converted genre strings to lists")
    # Making the Movies-Genre Pivot Table
    genre_table = create_genre_table(movies_master)
    logger.info(f"Genre table constructed with {len(genre_table)} genres")
    movie_genre_pivot = create_movie_genre_links(movies_master, genre_table)
    logger.info(
        f"Movie-genre pivot table creation complete: {movie_genre_pivot.shape[0]} links"
    )
    # if export == True:
    #     movies_master.to_csv(TMDB_OUTPUT_PATH, index=False)
    #     genre_table.to_csv(GENRES_OUTPUT_PATH, index=False)
    #     budgets_df.to_csv(BUDGET_OUTPUT_PATH, index=False)
    #     movie_genre_pivot.to_csv(os.path.join(PROCESSED_PATH, "movie_genre_links.csv"), index=False)
    logger.info("Cleaning and merging stage complete")
    return movies_master, budgets_df, genre_table, movie_genre_pivot
