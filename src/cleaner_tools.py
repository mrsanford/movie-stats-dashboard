from src.helpers import GENRES_RAW_PATH, COLUMN_MAPPING
from src.utils.logging import setup_logger
import pandas as pd
from typing import List
from glob import glob
import os


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

def split_genres_list(df: pd.DataFrame, genre_column='genre') -> List[str]:
    """
    Converts genre strings to a list for each row
    ---
    Args:
        df (pd.DataFrame): input DataFrame with target genre column
        genre_column (str): name of the column containing genre strings
    Returns:
        pd.DataFrame: same DataFrame with genre column converted to List[str]
    """
    df = df.copy()
    df = df.dropna(subset=[genre_column])
    # applying string splitting and cleanup
    df[genre_column] = (
        df[genre_column]
        .str.split(",\s*")
        .apply(lambda genres: [g.strip().title() for g in genres])
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

def prune_columns(df: pd.DataFrame, target_cols: list, source_name: str = "") -> pd.DataFrame:
    logger = setup_logger("column_pruner", "merge_datasets")
    missing = set(target_cols) - set(df.columns)
    if missing:
        logger.info(f'Missing columns in {source_name}: {missing}')
    return df[[col for col in target_cols if col in df.columns]]
