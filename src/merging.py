import pandas as pd
import ast
from typing import List
from src.utils.logging import setup_logger


# drop the null values first in tmdb, genres, and budgets
def drop_null_in_valid(df: pd.DataFrame, critical_cols: List[str]) -> pd.DataFrame:
    """
    Drops rows where any critical column is NaN, and rows where more than
    80% of non-critical columns are NaN.
    ---
    Args:
        df (pd.DataFrame): Input DataFrame.
        critical_cols (List[str]): List of critical columns to check.
    Returns:
        pd.DataFrame: Cleaned DataFrame with invalid rows removed.
    """
    df = df.dropna(subset=[col for col in critical_cols if col in df.columns])
    non_critical_cols = [col for col in df.columns if col not in critical_cols]
    if non_critical_cols:
        max_missing_allowed = int(0.8 * len(non_critical_cols))
        df = df[df[non_critical_cols].isnull().sum(axis=1) < max_missing_allowed]
    return df


## merging tmdb and genres on movie_ids
def merge_movie_ids(df1: pd.DataFrame, df2: pd.DataFrame, type: str = "left") -> pd.DataFrame:
    logger = setup_logger('movie_id_merger', 'merge_datasets')
    if 'movie_id' not in df1.columns or 'movie_id' not in df2.columns:
        raise ValueError("Both DataFrames must contain a 'movie_id' column.")
    merged_df = df1.merge(df2, on='movie_id', how=type)
    logger.info(f'Successfully merged {len(merged_df)} rows')
    return merged_df


## merging budgets on normalized_title + year with tmdb and then assigning movie ids
### if any go unmatched with tmdb, do the same to genres and assign movie ids
### if any are still unmatched, drop the budget rows
def assign_budget_movie_id(budgets_df: pd.DataFrame,
                           tmdb_df: pd.DataFrame,
                           genres_df: pd.DataFrame) -> pd.DataFrame:
    logger = setup_logger("budget_merger", "merge_datasets")
    # merging with TMDB on normalized_title + year
    merged = budgets_df.merge(tmdb_df[['normalized_title', 'year', 'movie_id']],
        on=['normalized_title', 'year'],how='left')
    logger.info(f'Number of matched rows: {len(merged)} rows')
    # checking unmatched rows (still missing movie_id)
    unmatched = merged[merged['movie_id'].isna()]
    logger.info(f'Remaining {len(unmatched)} rows')
    if not unmatched.empty:
        unmatched = unmatched.drop(columns=['movie_id'])
        unmatched = unmatched.merge(
            genres_df[['normalized_title', 'year', 'movie_id']],
            on=['normalized_title', 'year'],
            how='left'
        )
        matched = merged[~merged['movie_id'].isna()]
        merged = pd.concat([matched, unmatched], ignore_index=True)
    merged = merged.dropna(subset=['movie_id']).reset_index(drop=True)
    logger.info(f'There were {len(merged)} still unmatched -> dropped')
    return merged


def clean_merged_columns(df: pd.DataFrame) -> pd.DataFrame:
    new_df = df.copy()
    for col in new_df.columns:
        if col.endswith('_x'):
            base_col = col[:-2]
            corresponding_y = base_col + '_y'

            if corresponding_y in new_df.columns:
                new_df[base_col] = new_df[col].combine_first(new_df[corresponding_y])
                new_df = new_df.drop(columns=[col, corresponding_y])
    return new_df


def fix_genre_strings(df: pd.DataFrame, genre_col: str = 'genre') -> pd.DataFrame:
    """
    Converts genre column from stringified lists to actual Python lists.
    """
    df = df.copy()
    df[genre_col] = df[genre_col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    return df


def create_genre_table(df: pd.DataFrame, genre_col: str = 'genre') -> pd.DataFrame:
    """
    Creates a genre table assigning each unique genre an ID
    """
    # Flatten all genres into a single list
    all_genres = set(genre for sublist in df[genre_col] for genre in sublist)

    # Create genre table
    genre_table = pd.DataFrame({
        'genre_id': range(1, len(all_genres) + 1),
        'genre_name': sorted(all_genres)  # Sort alphabetically if you want
    })
    return genre_table


def create_movie_genre_links(df: pd.DataFrame, genre_table: pd.DataFrame, genre_col: str = 'genre') -> pd.DataFrame:
    """
    Creates a linking table between movies and genres
    """
    # explodes the genres first
    exploded = df[['movie_id', genre_col]].explode(genre_col)
    # merges to get genre_id
    link_table = exploded.merge(
        genre_table,
        left_on=genre_col,
        right_on='genre_name',
        how='left'
    )[['movie_id', 'genre_id']]
    return link_table