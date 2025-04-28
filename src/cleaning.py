import pandas as pd
from datetime import datetime
import re
from src.utils.logging import setup_logger
from src.cleaner_tools import (load_stack_csvs, drop_unused_columns, normalize_title_column, extract_year,
                               add_normalized_title_year, group_decades, split_genres_list,
                               standardize_columns, generate_col_order, prune_columns)
from src.helpers import (GENRE_COLS_TO_DROP, TMDB_COLS_TO_DROP,
    GENRES_RAW_PATH, TMDB_RAW_PATH, BUDGET_RAW_PATH,
    GENRES_OUTPUT_PATH, TMDB_OUTPUT_PATH, BUDGET_OUTPUT_PATH, RATING_MAP, IMPORTANT_TMDB_COLS,
    IMPORTANT_GENRE_COLS, IMPORTANT_BUDGET_COLS)

# instantiating column order
TMDB_FULL_COL_ORDER = generate_col_order("tmdb")
GENRE_FULL_COL_ORDER = generate_col_order("genres")
BUDGET_FULL_COL_ORDER = generate_col_order("budget")


def clean_tmdb_to_csv(
    raw_path: str = TMDB_RAW_PATH,
    cols_to_drop: list = TMDB_COLS_TO_DROP,
    output_path: str = TMDB_OUTPUT_PATH,
    column_order: list = TMDB_FULL_COL_ORDER,
    target_column_order: list = IMPORTANT_TMDB_COLS,
    export: bool = True,
) -> pd.DataFrame:
    """
    Loads, cleans, and standardizes the TMDb dataset before exporting it to a processed CSV
    ---
    Args:
        raw_path (str): path to the raw TMDb CSV folder
        cols_to_drop (list): list of columns to drop
        output_path (str): path to save the cleaned CSV
        column_order (list): final column order for the output CSV
    Returns:
        pd.DataFrame: the cleaned TMDb dataset
    """
    logger = setup_logger("tmdb_cleaner", "process_datasets")
    logger.info("Starting TMDb cleaning pipeline...")

    # loading/stacking data
    tmdb_df = load_stack_csvs(raw_path)
    logger.info("Loaded TMDb CSVs. Total rows: %d", len(tmdb_df))

    # dropping unnecessary columns and missing values
    tmdb_df = drop_unused_columns(tmdb_df, cols_to_drop)
    logger.info("Dropped unused columns.")
    tmdb_df = tmdb_df[tmdb_df["title"].notna() & (tmdb_df["title"].str.strip() != "")]
    logger.info(
        "Removed rows with missing or empty 'title'. Remaining: %d", len(tmdb_df)
    )

    # normalizing titles
    tmdb_df = normalize_title_column(
        tmdb_df, column="title", new_column="normalized_title"
    )
    logger.info("Normalized titles.")

    # extracting the year
    if "release_date" in tmdb_df.columns:
        tmdb_df = extract_year(tmdb_df, date_column="release_date")
        logger.info("'year' extracted from 'release_date'")

    # generating fallback merge key: normalized_title + year
    tmdb_df = add_normalized_title_year(tmdb_df, title_col="normalized_title")
    logger.info("Created 'normalized_title_year' column for fallback merging.")

    # filtering TMDb for invalid/null data
    tmdb_df = tmdb_df[
        ~tmdb_df[["runtime", "revenue", "budget"]].fillna(0).eq(0).all(axis=1)
    ]
    logger.info("Filtered rows with all-zero or null runtime, revenue, and budget.")

    # filtering TMDb for only 'Released' movies
    tmdb_df = tmdb_df[tmdb_df["status"] == "Released"]
    logger.info("Filtered for 'Released' movies only.")

    # filtering out adult content
    if "adult" in tmdb_df.columns:
        tmdb_df = tmdb_df[tmdb_df["adult"].astype(str).str.lower() != "true"]
        logger.info("Removed adult content.")

    # dropping where 'year' = NaN, converting to int, handling edge cases in 'year'
    tmdb_df = tmdb_df.dropna(subset=["year"])
    tmdb_df["year"] = tmdb_df["year"].astype(int)
    tmdb_df = tmdb_df[(tmdb_df["year"] >= 1880) & (tmdb_df["year"] <= 2025)]
    logger.info("'year' validated and cleaned. Remaining: %d", len(tmdb_df))

    # handling duplicates (imdb_id and normalized title)
    tmdb_df = tmdb_df.sort_values(by="year", ascending=True)
    tmdb_df = tmdb_df.drop_duplicates(subset="imdb_id", keep="first")
    tmdb_df = tmdb_df.drop_duplicates(subset=["normalized_title", "year"])
    logger.info("Removed duplicates. Final row count: %d", len(tmdb_df))

    # adding decade grouping
    tmdb_df["decade"] = tmdb_df["year"].apply(group_decades)
    logger.info("Grouped data by decade.")

    # splitting and normalizing 'genres' columns
    tmdb_df = split_genres_list(tmdb_df, genre_column='genres')
    logger.info("Split 'genres' into lists.")

    # reorganizing and outputting to CSV
    tmdb_df = standardize_columns(tmdb_df, source="tmdb", column_order=column_order)
    tmdb_df = prune_columns(tmdb_df, target_cols=target_column_order, source_name='tmdb')
    tmdb_df = tmdb_df.sort_values(by="title", ascending=True)
    if export == True: 
        tmdb_df.to_csv(output_path, index=False)
        logger.info("Exported cleaned TMDb data to %s", output_path)
    return tmdb_df


def clean_genres_to_csv(
    raw_path: str = GENRES_RAW_PATH,
    cols_to_drop: list = GENRE_COLS_TO_DROP,
    output_path: str = GENRES_OUTPUT_PATH,
    column_order: list = GENRE_FULL_COL_ORDER,
    target_column_order : list = IMPORTANT_GENRE_COLS,
    export: bool = True,
):
    """
    Loads, cleans, and standardizes the genres dataset before exporting to CSV
    1. normalizes movie names
    2. drops duplicates by movid_id first, and then by normalized_title + year as a fallback
    3.
    ---
    Args:
        raw_path (str): path to the raw genres CSV folder
        cols_to_drop (list): list of columns to drop
        output_path (str): path to save the cleaned CSV
        column_order (list): final column order for the output CSV
    Returns:
        pd.DataFrame: cleaned genres dataset
    """
    logger = setup_logger("genres_cleaner", "process_datasets")
    logger.info("Starting genres cleaning pipeline...")

    # loading all available genre.csvs and stacking to single dataframe
    genres_df = load_stack_csvs(raw_path)
    logger.info("Loaded genre CSVs. Total rows: %d", len(genres_df))

    # normalizing genre movie names
    genres_df = normalize_title_column(
        genres_df, column="movie_name", new_column="normalized_movie_name"
    )
    logger.info("Normalized movie names.")

    # cleaning 'star' column into lists
    if "star" in genres_df.columns:
        genres_df["star"] = genres_df["star"].fillna("").apply(
            lambda x: [name.strip().strip("'") for name in re.sub(r"^\[|\]$", "", x.strip()).split(", \\n") if name.strip()]
        )
        logger.info("Corrected 'star' column from stringified list to clean list of names.")
    # dropping duplicates by movie_id (first) and normalized title + year as a fallback
    genres_df = genres_df.drop_duplicates(subset="movie_id")
    genres_df = genres_df.drop_duplicates(subset=["normalized_movie_name", "year"])
    logger.info("Dropped duplicates by movie_id and normalized name + year.")

    # cleaning and formatting 'year' column
    genres_df["year"] = genres_df["year"].astype(str).str.strip()
    genres_df = genres_df[genres_df["year"].str.fullmatch(r"\d{4}")].copy()
    genres_df["year"] = genres_df["year"].astype(int)
    genres_df = genres_df[(genres_df["year"] >= 1880) & (genres_df["year"] <= 2025)]
    logger.info("'year' column cleaned and validated.")

    # generating fallback merge key: normalized_title + year
    genres_df = add_normalized_title_year(genres_df, title_col="normalized_movie_name")
    logger.info("Created 'normalized_title_year' column for fallback merging.")

    # grouping decades
    genres_df["decade"] = genres_df["year"].apply(group_decades)
    logger.info("Grouped data by decade.")

    # renaming "gross(in $)" column to "total_gross"
    genres_df["total_gross"] = genres_df["gross(in $)"]
    logger.info("Renamed 'gross(in $)' to 'total_gross'.")

    # dropping unused columns
    genres_df = drop_unused_columns(genres_df, cols_to_drop)
    logger.info("Dropped unused columns.")

    # dropping outliers and videogame rating values and mapping ratings to MPA's US Rating System
    drop_ratings = {
        "A",
        "T",
        "12",
        "7",
    }
    genres_df = genres_df.loc[~genres_df["certificate"].isin(drop_ratings)].copy()
    genres_df["certificate"] = (
        genres_df["certificate"].map(RATING_MAP).fillna("Not Rated")
    )
    logger.info("Dropped unneccesary ratings and remapped certificate ratings.")

    # splitting 'genres' into lists
    genres_df = split_genres_list(genres_df, genre_column='genre')
    logger.info("Splitting 'genre' into lists.")

    # organizing and outputting results to CSV
    genres_df = standardize_columns(
        genres_df, source="genres", column_order=column_order
    )
    genres_df = prune_columns(genres_df, target_cols=target_column_order, source_name='genres')
    if export == True: 
        genres_df.to_csv(output_path, index=False)
        logger.info("Exported cleaned genres data to %s", output_path)
    return genres_df


def clean_budgets_to_csv(
    raw_path: str = BUDGET_RAW_PATH,
    output_path: str = BUDGET_OUTPUT_PATH,
    column_order: list = BUDGET_FULL_COL_ORDER,
    target_column_order: list = IMPORTANT_BUDGET_COLS,
    export: bool = True,
) -> pd.DataFrame:
    """
    Loads, cleans, and standardizes the budget dataset before exporting to CSV
    ---
    Args:
        raw_path (str): path to the raw budget CSV folder
        output_path (str): path to save the cleaned CSV
        column_order (list): final column order for the output CSV
    Returns:
        pd.DataFrame: cleaned budget dataset
    """
    logger = setup_logger("budget_cleaner", "process_datasets")
    logger.info("Starting budget cleaning pipeline...")

    # loading in the available budget data
    budgets_df = load_stack_csvs(raw_path)
    logger.info("Loaded budget CSVs. Total rows: %d", len(budgets_df))

    # dropping dates that are > than the current date
    if "Release Date" in budgets_df.columns:
        budgets_df["Release Date"] = pd.to_datetime(
            budgets_df["Release Date"], errors="coerce"
        )
        today = pd.to_datetime(datetime.today())
        budgets_df = budgets_df[budgets_df["Release Date"] <= today]
        logger.info("Filtered out future release dates.")
        budgets_df = extract_year(budgets_df, date_column="Release Date")
        logger.info("Extracted year from 'Release Date'.")

    # normalizing movie titles & creating new column
    budgets_df = normalize_title_column(
        budgets_df, column="Movie", new_column="normalized_title"
    )
    logger.info("Normalized movie titles.")

    # dropping duplicates based on the normalized title AND year
    pre_dupes = len(budgets_df)
    budgets_df = budgets_df.drop_duplicates(subset=["normalized_title", "year"])
    logger.info(
        "Dropped %d duplicate rows by normalized title and year.",
        pre_dupes - len(budgets_df),
    )

    # generating fallback merge key: normalized_title + year
    budgets_df = add_normalized_title_year(budgets_df, title_col="normalized_title")
    logger.info("Created 'normalized_title_year' column for fallback merging.")

    # grouping decades
    budgets_df["decade"] = budgets_df["year"].apply(group_decades)
    logger.info("Grouped data by decade.")

    # organizing and outputting results to CSV
    budgets_df = standardize_columns(
        budgets_df, source="budget", column_order=column_order
    )
    budgets_df = prune_columns(budgets_df, target_cols=target_column_order, source_name='budget')
    
    budgets_df = budgets_df.sort_values(by="title", ascending=True)
    if export == True: 
        budgets_df.to_csv(output_path, index=False)
        logger.info("Exported cleaned budget data to %s", output_path)
    return budgets_df
