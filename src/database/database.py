from src.utils.helpers import MOVIZ_DB_PATH
from src.utils.logging import setup_logger
import os
import sqlite3
import pandas as pd
import numpy as np


sqlite3.register_adapter(np.int64, lambda x: int(x))


class BaseDB:
    def __init__(self, path: str, create: bool = False):
        self._connected = False
        self.path = os.path.normpath(path)
        self._existed = self.check_exists(create)
        return

    def run_query(
        self,
        sql: str,
        params: tuple | dict = None,
        commit: bool = False,
        keep_open: bool = False,
    ) -> pd.DataFrame:
        self._connect()
        try:
            results = pd.read_sql(sql, self._conn, params=params)
        except Exception as e:
            raise type(e)(f"sql: {sql}\nparams: {params}") from e
        if not keep_open:
            self._close()
        return results

    def run_action(
        self,
        sql: str,
        params: tuple | dict = None,
        commit: bool = False,
        keep_open: bool = False,
    ) -> int:
        if not self._connected:
            self._connect()
        try:
            if params is None:
                self._curs.execute(sql)
            else:
                self._curs.execute(sql, params)
        except Exception as e:
            self._conn.rollback()
            self._conn.close()
            raise type(e)(f"sql: {sql}\nparams: {params}") from e
        if not keep_open:
            self._close()
        return self._curs.lastrowid

    def _connect(self, foreign_keys: bool = True) -> None:
        # print('connected to database')
        # curframe = inspect.currentframe()
        # calframe = inspect.getouterframes(curframe, 2)
        # print('caller name:', calframe[1][3])
        self._conn = sqlite3.connect(self.path)
        self._curs = self._conn.cursor()
        if foreign_keys:
            self._curs.execute("PRAGMA foreign_keys=OFF;")
        self._connected = True
        return

    def _close(self) -> None:
        # print('closed connection')
        # curframe = inspect.currentframe()
        # calframe = inspect.getouterframes(curframe, 2)
        # print('caller name:', calframe[1][3])
        if not self._connected:
            return
        if self._connected:
            self._conn.close()
            self._connected = False
        return

    def check_exists(self, create: bool) -> bool:
        existed = True
        path_parts = self.path.split(os.sep)
        n = len(path_parts)
        for i in range(n):
            part = os.sep.join(path_parts[: i + 1])
            if not os.path.exists(part):
                if not create:
                    raise FileNotFoundError(f'File or folder "{part}" does not exist.')
                existed = False
                if i == n - 1:
                    self._connect()
                    self._close()
                else:
                    os.mkdir(part)
        return existed


class MovieDB(BaseDB):
    PATH = MOVIZ_DB_PATH

    def __init__(self, path: str = PATH, create: bool = False):
        """
        Initializing the MovieDB class and optionally creating schema if not previously existing
        """
        self.logger = setup_logger("MovieDB", "database")
        super().__init__(self.PATH, create=True)
        if not self._existed:
            self.logger.info("Database not found. Creating schema")
            self._create_tables()
        else:
            self.logger.info("Database already exists. Using existing schema")

    def _create_tables(self) -> None:
        """
        Creates tables and indexes necessary for MoVIZ
        """
        self.logger.info("Creating tables")

        # tMovie Table
        self.run_action("""
            CREATE TABLE IF NOT EXISTS tMovie(
                movie_id TEXT PRIMARY KEY,
                title TEXT,
                normalized_title TEXT,
                release_date TEXT,
                year INTEGER,
                decade TEXT,
                certificate TEXT,
                rating REAL,
                votes INTEGER,
                runtime INTEGER,
                description TEXT, 
                production_countries TEXT
            );""")
        # tGenre Table
        self.run_action("""
            CREATE TABLE IF NOT EXISTS tGenre(
                genre_id INTEGER PRIMARY KEY,
                genre_name TEXT
            );""")
        # tMovieGenre Table
        self.run_action("""
            CREATE TABLE IF NOT EXISTS tMovieGenre(
                movie_id TEXT NOT NULL,
                genre_id INTEGER NOT NULL,
                FOREIGN KEY (movie_id) REFERENCES tMovie(movie_id),
                FOREIGN KEY (genre_id) REFERENCES tGenre(genre_id)
            );""")
        # tBudget Table
        self.run_action("""
            CREATE TABLE IF NOT EXISTS tBudget (
                budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id TEXT NOT NULL,
                production_budget INTEGER,
                domestic_gross INTEGER,
                worldwide_gross INTEGER,
                FOREIGN KEY (movie_id) REFERENCES tMovie(movie_id)
            );""")
        # Creating additional indices for faster queries
        self.run_action(
            "CREATE INDEX IF NOT EXISTS idx_budget_movie_id ON tBudget(movie_id);"
        )
        self.run_action(
            "CREATE INDEX IF NOT EXISTS idx_moviegenre_movie_id ON tMovieGenre(movie_id);"
        )
        self.run_action(
            "CREATE INDEX IF NOT EXISTS idx_moviegenre_genre_id ON tMovieGenre(genre_id);"
        )
        self.logger.info("Tables and indexes successfully created")
        return

    def load_from_dataframes(
        self,
        movies_df: pd.DataFrame,
        budgets_df: pd.DataFrame,
        genre_table: pd.DataFrame,
        movie_genre_links: pd.DataFrame,
    ) -> None:
        """
        Loads cleaned and merged DataFrames directory into SQLite database
        ---
        Args:
            movies_df (pd.DataFrame): main movie metadata table
            budgets_df (pd.DataFrame): budgets and gross earnings table
            genre_table (pd.DataFrame): genre lookup table
            movie_genre_links (pd.DataFrame): pivot table linking movies and genres
        """
        self.logger.info("Beginning data insertion into MoVIZ database")
        self._connect()
        try:
            # Inserting into tMovies
            movie_cols = [
                "movie_id",
                "title",
                "normalized_title",
                "release_date",
                "year",
                "decade",
                "certificate",
                "rating",
                "votes",
                "runtime",
                "description",
                "production_countries",
            ]
            movie_sql = f"INSERT OR IGNORE INTO tMovie VALUES ({','.join(['?'] * len(movie_cols))})"
            for row in movies_df[movie_cols].itertuples(index=False, name=None):
                self._curs.execute(movie_sql, row)
                self.logger.info(f"Inserted {len(movies_df)} rows into tMovie")

            # Inserting into tBudgets
            budget_cols = [
                "movie_id",
                "production_budget",
                "domestic_gross",
                "worldwide_gross",
            ]
            budget_sql = """
            INSERT OR IGNORE INTO tBudget (
                movie_id, production_budget, domestic_gross, worldwide_gross
            ) VALUES (?, ?, ?, ?)
            """
            for row in budgets_df[budget_cols].itertuples(index=False, name=None):
                self._curs.execute(budget_sql, row)
            self.logger.info(f"Inserted {len(budgets_df)} rows into tBudget")

            # Inserting into tGenre
            genre_sql = (
                "INSERT OR IGNORE INTO tGenre (genre_id, genre_name) VALUES (?, ?)"
            )
            for row in genre_table[["genre_id", "genre_name"]].itertuples(
                index=False, name=None
            ):
                self._curs.execute(genre_sql, row)
            self.logger.info(f"Inserted {len(genre_table)} rows into tGenre")

            # Inserting into tMovieGenre
            link_sql = (
                "INSERT OR IGNORE INTO tMovieGenre (movie_id, genre_id) VALUES (?, ?)"
            )
            for row in movie_genre_links[["movie_id", "genre_id"]].itertuples(
                index=False, name=None
            ):
                self._curs.execute(link_sql, row)
            self.logger.info(f"Inserted {len(movie_genre_links)} rows into tMovieGenre")

            self._conn.commit()
            self.logger.info("All data successfully committed")
        except Exception as e:
            self.logger.error("Rolling back. Error occured during insertion")
            self._conn.rollback()
            raise e
        finally:
            self._close()
            self.logger.info("Database connection closed")
