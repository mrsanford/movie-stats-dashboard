import pandas as pd
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
)


def load_stack_csvs(folder_path: str = GENRES_RAW_PATH):
    """
    Loads and stacks all csvs from a target folder and
    stacks them into a single dataframe
    ---
    Args:
        genres_path (str): the path to the raw genre csvs
    Returns:
        the full pd.DataFrame
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
    Drops target columns that will not be used in analysis
    in pd.DataFrame based on the list of columns to drop
    """
    # df.drop([col for col in cols_to_drop if col in df.columns])
    return df.drop(columns=cols_to_drop, errors="ignore")


def extract_year(
    df: pd.DataFrame, date_column: str, output_column: str = "year"
) -> pd.DataFrame:
    """
    Extracts just the year from the target date column
    """
    df[output_column] = pd.to_datetime(df[date_column], errors="coerce").dt.year.astype(
        "Int64"
    )
    return df


def group_decades(year: int) -> None:
    """
    Categorizes a single year under a larger decade label.
    For example: the year 1986 will return '1980-1989'
    ---
    Returns: None if year is missing or invalid
    """
    try:
        start = int(year) // 10 * 10
        end = start + 9
        return f"{start}–{end}"
    except Exception:
        return None


def clean_tmdb_to_csv(
    raw_path: str = TMDB_RAW_PATH,
    cols_to_drop: list = TMDB_COLS_TO_DROP,
    output_path: str = TMDB_OUTPUT_PATH,
    column_order: list = TMDB_COL_ORDER,
) -> pd.DataFrame:
    """
    Cleans the TMDb dataset and exports to CSV
    """

    def filter_tmdb_csv(df: pd.DataFrame) -> pd.DataFrame:
        """
        Further filters rows in tmdb.csv where:
        - observation in 'title' is missing/blank
        - all of runtime, revenue, AND budget are missing or 0
        - 'status' is not 'Released'
        """
        df = df[df["title"].notna() & (df["title"].str.strip() != "")]
        df = df[~df[["runtime", "revenue", "budget"]].fillna(0).eq(0).all(axis=1)]
        df = df[df["status"] == "Released"]
        return df

    # loading and concatenating any TMDb related CSVs
    tmdb_df = load_stack_csvs(raw_path)
    # dropping unnecessary columns
    tmdb_df = drop_unused_columns(tmdb_df, cols_to_drop)
    # normalizing titles
    tmdb_df = normalize_title_column(
        tmdb_df, column="title", new_column="normalized_title"
    )
    # filtering TMDb for invalid/null data
    if all(
        col in tmdb_df.columns
        for col in ["runtime", "revenue", "budget", "status", "title"]
    ):
        tmdb_df = filter_tmdb_csv(tmdb_df)
    else:
        print("TMDB DataFrame does not have the necessary columns to filter.")
    # filtering out adult content
    if "adult" in tmdb_df.columns:
        tmdb_df = tmdb_df[tmdb_df["adult"].astype(str).str.lower() != "true"]
    # extracting the year
    if "release_date" in tmdb_df.columns:
        tmdb_df = extract_year(tmdb_df, date_column="release_date")
    # adding decades
    tmdb_df["decade"] = tmdb_df["year"].apply(group_decades)
    # dropping any duplicates by the normalized title
    tmdb_df = tmdb_df.drop_duplicates(subset=["normalized_title", "year"])
    # reordering columns
    tmdb_df = tmdb_df[column_order]
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
    """ """
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
    # grouping decades
    genres_df["decade"] = genres_df["year"].apply(group_decades)
    # reordering columns
    target_order = column_order
    genres_df = genres_df[target_order]
    # ouputting results to clean CSV
    genres_df.to_csv(output_path, index=False)
    return genres_df


def clean_budgets_to_csv(
    raw_path: str = BUDGET_RAW_PATH,
    output_path: str = BUDGET_OUTPUT_PATH,
    column_order: list = BUDGET_COL_ORDER,
) -> pd.DataFrame:
    """
    Loads the Budget CSV from the raw subfolder 'budgets,' indexes the year and creates a new
    column 'year'
    Then outputs a new CSV to the processed folder
    ---
    Args:
        raw_path (str) is the path to 'budgets' subfolder
        output_path (str) is the path to the processed file
    """
    # loading in the available budget data
    budgets_df = load_stack_csvs(raw_path)
    # extracting the year value from the 'Release Date' column
    if "Release Date" in budgets_df.columns:
        budgets_df = extract_year(budgets_df, date_column="Release Date")
    # normalizing movie titles & creating new column
    budgets_df = normalize_title_column(
        budgets_df, column="Movie", new_column="normalized_title"
    )
    # dropping duplicates based on the normalized title AND year
    budgets_df = budgets_df.drop_duplicates(subset=["normalized_title", "year"])
    # grouping decades
    budgets_df["decade"] = budgets_df["year"].apply(group_decades)
    # reordering columns
    budgets_df = budgets_df[column_order]
    # sorting the values alphabetically by movie title
    budgets_df = budgets_df.sort_values(by="Movie", ascending=True)
    # outputting to csv
    budgets_df.to_csv(output_path, index=False)
    return budgets_df
