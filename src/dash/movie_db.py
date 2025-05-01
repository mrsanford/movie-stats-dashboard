from src.database.database import BaseDB
import pandas as pd

PATH_DB = "data/processedmovies.sqlite"


class MovieDB(BaseDB):
    def __init__(self):
        super().__init__(path=PATH_DB, create=True)
        if not self._existed:
            pass
        return
    
    def get_genre_list(self) -> list:
        sql = "SELECT DISTINCT genre_name FROM tGenre ORDER BY genre_name;"
        return self.run_query(sql)["genre_name"].tolist()

    def get_decade_list(self, genre: str) -> list:
        sql = """
        SELECT DISTINCT m.decade
        FROM tMovie m
        JOIN tMovieGenre mg ON m.movie_id = mg.movie_id
        JOIN tGenre g ON mg.genre_id = g.genre_id
        WHERE g.genre_name = :genre
        ORDER BY m.decade;
        """
        return self.run_query(sql, {"genre": genre})["decade"].tolist()

    def get_title_list(self, genre: str, decade: str) -> list:
        sql = """
        SELECT DISTINCT m.normalized_title
        FROM tMovie m
        JOIN tMovieGenre mg ON m.movie_id = mg.movie_id
        JOIN tGenre g ON mg.genre_id = g.genre_id
        WHERE g.genre_name = :genre
          AND m.decade = :decade
        ORDER BY m.normalized_title;
        """
        return self.run_query(sql, {"genre": genre, "decade": decade})["normalized_title"].tolist()

    def get_data(self, genre: str = None, decade: str = None, title: str = None) -> pd.DataFrame:
        params = {"genre": genre, "decade": decade, "title": title}

        if title:
            sql = """
            SELECT b.production_budget AS x, b.worldwide_gross AS y
            FROM tBudget b
            JOIN tMovie m ON b.movie_id = m.movie_id
            WHERE m.normalized_title = :title;
            """
        elif decade:
            sql = """
            SELECT b.production_budget AS x, b.worldwide_gross AS y
            FROM tBudget b
            JOIN tMovie m ON b.movie_id = m.movie_id
            JOIN tMovieGenre mg ON m.movie_id = mg.movie_id
            JOIN tGenre g ON mg.genre_id = g.genre_id
            WHERE g.genre_name = :genre
              AND m.decade = :decade;
            """
        elif genre:
            sql = """
            SELECT b.production_budget AS x, b.worldwide_gross AS y
            FROM tBudget b
            JOIN tMovie m ON b.movie_id = m.movie_id
            JOIN tMovieGenre mg ON m.movie_id = mg.movie_id
            JOIN tGenre g ON mg.genre_id = g.genre_id
            WHERE g.genre_name = :genre;
            """
        else:
            sql = """
            SELECT b.production_budget AS x, b.worldwide_gross AS y
            FROM tBudget b;
            """

        return self.run_query(sql, params)
