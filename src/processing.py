import pandas as pd
from datetime import datetime
import glob
import os
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
    tmdb_df = load_stack_csvs(raw_path)
    # dropping unnecessary columns
    tmdb_df = drop_unused_columns(tmdb_df, cols_to_drop)
    # normalizing titles
    tmdb_df = normalize_title_column(
        tmdb_df, column="title", new_column="normalized_title"
    )
    # dropping row if the title is empty
    tmdb_df = tmdb_df[tmdb_df["title"].notna() & (tmdb_df["title"].str.strip() != "")]
    # filtering TMDb for invalid/null data
    tmdb_df = tmdb_df[
        ~tmdb_df[["runtime", "revenue", "budget"]].fillna(0).eq(0).all(axis=1)
    ]
    # filtering TMDb for only 'Released' movies
    tmdb_df = tmdb_df[tmdb_df["status"] == "Released"]
    # filtering out adult content
    if "adult" in tmdb_df.columns:
        tmdb_df = tmdb_df[tmdb_df["adult"].astype(str).str.lower() != "true"]
    # extracting the year
    if "release_date" in tmdb_df.columns:
        tmdb_df = extract_year(tmdb_df, date_column="release_date")
    # dropping where years are NaN, then turns in values into type int for handling
    tmdb_df = tmdb_df.dropna(subset=["year"])
    tmdb_df["year"] = tmdb_df["year"].astype(int)
    # adding decades
    tmdb_df["decade"] = tmdb_df["year"].apply(group_decades)
    # handling mistyped years
    tmdb_df = tmdb_df[(tmdb_df["year"] >= 1880) & (tmdb_df["year"] <= 2025)]
    # dropping any duplicates by the normalized title
    tmdb_df = tmdb_df.drop_duplicates(subset=["normalized_title", "year"])
    # renaming and reordering columns
    tmdb_df = standardize_columns(tmdb_df, source="tmdb", column_order=column_order)
    # alphabetizing results
    tmdb_df = tmdb_df.sort_values(by="title", ascending=True)
    # outputting to CSV
    tmdb_df.to_csv(output_path, index=False)
    print(
        f"Cleaning successful. Dataset length: {len(tmdb_df)}. Exporting to {output_path}"
    )
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
    # loading all available genre.csvs and stacking to single dataframe
    genres_df = load_stack_csvs(raw_path)
    # normalizing genre movie names
    genres_df = normalize_title_column(
        genres_df, column="movie_name", new_column="normalized_movie_name"
    )
    # dropping duplicates by movie_id (first) and normalized title + year as a fallback
    genres_df = genres_df.drop_duplicates(subset="movie_id")
    genres_df = genres_df.drop_duplicates(subset=["normalized_movie_name", "year"])
    # renaming "gross(in $)" column to "total_gross"
    genres_df["total_gross"] = genres_df["gross(in $)"]
    # dropping unused columns
    genres_df = drop_unused_columns(genres_df, cols_to_drop)
    # dropping rating values and mapping ratings to MPA's US Rating System
    drop_ratings = {
        "A",
        "T",
        "12",
        "7",
    }  # eliminating vaguely rated outliers and videogames
    genres_df = genres_df.loc[~genres_df["certificate"].isin(drop_ratings)].copy()
    genres_df["certificate"] = (
        genres_df["certificate"].map(RATING_MAP).fillna("Not Rated")
    )
    # cleaning and processing only valid 4 digit years between 1880 - 2025
    genres_df["year"] = genres_df["year"].astype(str).str.strip()
    genres_df = genres_df[
        genres_df["year"].str.fullmatch(r"\d{4}")  # must be exactly 4 digits
    ].copy()
    genres_df["year"] = genres_df["year"].astype(int)
    genres_df = genres_df[(genres_df["year"] >= 1880) & (genres_df["year"] <= 2025)]
    # if the values for year, decade, runtime, rating, votes, and total gross are NaN, drop the column
    # grouping decades
    genres_df["decade"] = genres_df["year"].apply(group_decades)
    # renaming and reordering columns
    genres_df = standardize_columns(
        genres_df, source="genres", column_order=column_order
    )
    # ouputting results to clean CSV
    genres_df.to_csv(output_path, index=False)
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
    # loading in the available budget data
    budgets_df = load_stack_csvs(raw_path)
    # dropping dates that are > than the current date
    if "Release Date" in budgets_df.columns:
        budgets_df["Release Date"] = pd.to_datetime(
            budgets_df["Release Date"], errors="coerce"
        )
        today = pd.to_datetime(datetime.today())
        budgets_df = budgets_df[budgets_df["Release Date"] <= today]
        # extracting the year value from the 'Release Date' column
        budgets_df = extract_year(budgets_df, date_column="Release Date")
    # normalizing movie titles & creating new column
    budgets_df = normalize_title_column(
        budgets_df, column="Movie", new_column="normalized_title"
    )
    # dropping duplicates based on the normalized title AND year
    budgets_df = budgets_df.drop_duplicates(subset=["normalized_title", "year"])
    # grouping decades
    budgets_df["decade"] = budgets_df["year"].apply(group_decades)
    # renaming and reordering columns
    budgets_df = standardize_columns(
        budgets_df, source="budget", column_order=column_order
    )
    # sorting the values alphabetically by movie title
    budgets_df = budgets_df.sort_values(by="title", ascending=True)
    # outputting to csv
    budgets_df.to_csv(output_path, index=False)
    return budgets_df
