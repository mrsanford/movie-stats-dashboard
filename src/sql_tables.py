from src.helpers import (
    PROCESSED_PATH,
    TMDB_OUTPUT_PATH,
    GENRES_OUTPUT_PATH,
    BUDGET_OUTPUT_PATH,
)
import csv
import os
import inspect
import warnings
import sqlite3
from glob import glob
import pandas as pd
import numpy as np
from traceback import print_exc as pe
from datetime import datetime


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
    FOLDER = PROCESSED_PATH
    DB_NAME = "movies.sqlite"
    PATH = FOLDER + DB_NAME

    def __init__(self, path: str = PATH, create: bool = False):
        super().__init__(self.PATH, create=True)
        if not self._existed:
            self._create_tables()
            self.load_tmdb_data()
            self.load_genre_data()
            self.load_budget_data()

    def _create_tables(self) -> None:
        sql = """
            CREATE TABLE IF NOT EXISTS tMovie (
                movie_id TEXT PRIMARY KEY,
                title TEXT,
                release_year TEXT,
                certificate TEXT,
                runtime_minutes INTEGER,
                average_vote REAL,
                vote_count INTEGER,
                release_status TEXT,
                imdb_id TEXT,
                language TEXT,
                movie_overview TEXT, 
                movie_tagline TEXT,
                popularity_score REAL
            );"""
        self.run_action(sql)

        sql = """
            CREATE TABLE IF NOT EXISTS tBudget (
                budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id TEXT,
                release_date TEXT,
                production_budget_usd INTEGER,
                domestic_gross_usd INTEGER,
                worldwide_gross_usd INTEGER,
                FOREIGN KEY (movie_id) REFERENCES tMovie(movie_id)
            );"""
        self.run_action(sql)

        # sql = """
        # CREATE TABLE IF NOT EXISTS tGenre (
        #     genre_id INTEGER PRIMARY KEY,
        #     genre_name TEXT
        # );"""
        # self.run_action(sql)

        # sql = """
        # CREATE TABLE IF NOT EXISTS tMovieGenre (
        #     movie_id TEXT NOT NULL,
        #     genre_id INTEGER NOT NULL,
        #     FOREIGN KEY (movie_id) REFERENCES tMovie(movie_id),
        #     FOREIGN KEY (genre_id) REFERENCES tGenre(genre_id)
        # );"""
        # self.run_action(sql)

        # sql = """
        # CREATE TABLE IF NOT EXISTS tPeople (
        #     person_id INTEGER PRIMARY KEY,
        #     person_name TEXT
        # );"""
        # self.run_action(sql)

        # sql = """
        # CREATE TABLE IF NOT EXISTS tMoviePeople (
        #     movie_id TEXT NOT NULL,
        #     person_id INTEGER NOT NULL,
        #     person_role TEXT,
        #     FOREIGN KEY (movie_id) REFERENCES tMovie(movie_id),
        #     FOREIGN KEY (person_id) REFERENCES tPeople(person_id)
        # );"""
        # self.run_action(sql)
        return

    def load_tmdb_data(self) -> None:
        tmdb_data = pd.read_csv(TMDB_OUTPUT_PATH)

        ## STANDARDIZE COLUMN NAMES HERE ##
        sql = """
            INSERT INTO tMovie
            VALUES
        ;"""
        self._connect()
        try:
            for i, row in enumerate(tmdb_data.to_dict(orient="records")):
                try:
                    self.run_action(sql, params=row, commit=False, keep_open=True)
                except Exception as e:
                    raise type(e)(f"Error on row {i}") from e
            self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            raise e
        finally:
            self._close()
        return None

    def load_genre_data(self) -> None:
        genre_data = pd.read_csv(GENRES_OUTPUT_PATH)
        ## STANDARDIZE COLUMN NAMES HERE ##
        sql = """
            INSERT INTO tMovie
            VALUES
        ;"""
        self._connect()
        try:
            for i, row in enumerate(genre_data.to_dict(orient="records")):
                try:
                    self.run_action(sql, params=row, commit=False, keep_open=True)
                except Exception as e:
                    raise type(e)(f"Error on row {i}") from e
            self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            raise e
        finally:
            self._close()
        return None

    def load_budget_data(self) -> None:
        budget_data = pd.read_csv(BUDGET_OUTPUT_PATH)
        ## STANDARDIZE COLUMN NAMES HERE ##
        sql = """
            INSERT INTO tMovie
            VALUES
        ;"""
        self._connect()
        try:
            for i, row in enumerate(budget_data.to_dict(orient="records")):
                try:
                    self.run_action(sql, params=row, commit=False, keep_open=True)
                except Exception as e:
                    raise type(e)(f"Error on row {i}") from e
            self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            raise e
        finally:
            self._close()
        return None
