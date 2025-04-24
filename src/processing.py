import pandas as pd
from datetime import datetime
import glob
import os
from src.utils.logging import setup_logger
from src.helpers import (
    GENRE_COLS_TO_DROP,
    TMDB_COLS_TO_DROP,
    GENRES_RAW_PATH,
    TMDB_RAW_PATH,
    GENRES_OUTPUT_PATH,
    TMDB_OUTPUT_PATH,
    BUDGET_RAW_PATH,
    BUDGET_OUTPUT_PATH,
    TMDB_COL_ORDER,
    GENRE_COL_ORDER,
    BUDGET_COL_ORDER,
    COLUMN_MAPPING,
    RATING_MAP,
)


def load_stack_csvs(folder_path: str = GENRES_RAW_PATH):
    """
    Loads and stacks any/all available CSV files from a specified folder
    into a single DataFrame
    ---
    Args:
        folder_path (str): Path to the folder containing the raw CSV files
    Returns:
        pd.DataFrame: concatenated DataFrame of all CSV files
    """
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    dfs = [pd.read_csv(f) for f in csv_files]
    return pd.concat(dfs, ignore_index=True)


def normalize_title_column(
    df: pd.DataFrame, column: str = "title", new_column: str = "normalized_title"
) -> pd.DataFrame:
    """
    Creates a new column of normalized movie titles (lowercases, removed
    nonalphanumeric characters, whitespace)
    ---
    Args:
        df (pd.DataFrame): the input DataFrame
        column (str): column containing original movie titles
        new_column (str): the name of the new normalized column
    Returns:
        pd.DataFrame: DataFrame with the added normalized title column
    """
    df[new_column] = (
        df[column]
        .astype(str)
        .str.lower()
        .str.replace(r"\W+", "", regex=True)
        .str.strip()
    )
    return df


def drop_unused_columns(df: pd.DataFrame, cols_to_drop: list) -> pd.DataFrame:
    """
    Dropping specified columns from the DataFrame
    ---
    Args:
        df (pd.DataFrame): the input DataFrame
        cols_to_drop (list): the list of column names to drop
    Returns:
        pd.DataFrame: DataFrame with specified columns removed
    """
    # df.drop([col for col in cols_to_drop if col in df.columns])
    return df.drop(columns=cols_to_drop, errors="ignore")


def extract_year(
    df: pd.DataFrame, date_column: str, output_column: str = "year"
) -> pd.DataFrame:
    """
    Extracts the year from the target date column and stores in a new column
    ---
    Args:
        df (pd.DataFrame): input DataFrame
        date_column (str): name of column with dates
        output_column (str): name of new column to store year
    Returns:
        pd.DataFrame: DataFrame with added 'year' column
    """
    df[output_column] = pd.to_datetime(df[date_column], errors="coerce").dt.year.astype(
        "Int64"
    )
    return df


def group_decades(year: int) -> None:
    """
    Converts year into decade label and adds new 'decade' column (e.g.,
    1986 -> '1980-1989')
    ---
    Args:
        year (int): the year to convert
    Returns:
        str: decade label or None if year is missing or invalid
    """
    try:
        start = int(year) // 10 * 10
        end = start + 9
        return f"{start}–{end}"
    except Exception:
        return None


def standardize_columns(
    df: pd.DataFrame, source: str, column_order: list = None
) -> pd.DataFrame:
    """
    Renames and reorders columns for standardization (SQL support) and improved readability
    ---
    Args:
        df (pd.DataFrame): input DataFrame
        source (str): the dataset source key (e.g., 'tmdb', 'genres', 'budget')
        column_order (list): final desired column order
    Returns:
        pd.DataFrame: DataFrame wih renamed columns (option to reorder too)
    """
    rename_map = {
        **COLUMN_MAPPING.get(source, {}),
        **COLUMN_MAPPING.get("shared", {}),
    }
    df = df.rename(columns=rename_map)
    if column_order:
        df = df.reindex(columns=column_order)
    return df


def add_normalized_title_year(df: pd.DataFrame, title_col: str, year_col: str = "year"):
    return df.assign(
        normalized_title_year=(
            df[title_col].astype(str).str.strip().str.lower()
            + "_"
            + df[year_col].astype(str).str.strip()
        )
    )


def clean_tmdb_to_csv(
    raw_path: str = TMDB_RAW_PATH,
    cols_to_drop: list = TMDB_COLS_TO_DROP,
    output_path: str = TMDB_OUTPUT_PATH,
    column_order: list = TMDB_COL_ORDER,
) -> pd.DataFrame:
    """
    Loads, cleans, and standardizes the TMDb dataset before exporting it to a processed CSV
    Steps for cleaning TMDb include
        1. instantly dropping unnecessary columns
        2. normalizing all movie titles
        3. dropping rows where 'title' is empty
        3. filtering rows where there is NaN or 0.0 value for runtime, revenue, AND budget
        4. selecting only 'Released' movies
        5. removing pornography
        6. extracting years, grouping by decade, and handling errors/edge cases
        7. dropping duplicate movies by normalized_name and year
        8. reordering columns, alphabetizing by title, and outputting to csv
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

    # reorganizing and outputting to CSV
    tmdb_df = standardize_columns(tmdb_df, source="tmdb", column_order=column_order)
    tmdb_df = tmdb_df.sort_values(by="title", ascending=True)
    tmdb_df.to_csv(output_path, index=False)
    logger.info("Exported cleaned TMDb data to %s", output_path)
    return tmdb_df


def clean_genres_to_csv(
    raw_path: str = GENRES_RAW_PATH,
    cols_to_drop: list = GENRE_COLS_TO_DROP,
    output_path: str = GENRES_OUTPUT_PATH,
    column_order: list = GENRE_COL_ORDER,
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

    # organizing and outputting results to CSV
    genres_df = standardize_columns(
        genres_df, source="genres", column_order=column_order
    )
    genres_df.to_csv(output_path, index=False)
    logger.info("Exported cleaned genres data to %s", output_path)
    return genres_df


def clean_budgets_to_csv(
    raw_path: str = BUDGET_RAW_PATH,
    output_path: str = BUDGET_OUTPUT_PATH,
    column_order: list = BUDGET_COL_ORDER,
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
    budgets_df = budgets_df.sort_values(by="title", ascending=True)
    budgets_df.to_csv(output_path, index=False)
    logger.info("Exported cleaned budget data to %s", output_path)
    return budgets_df
