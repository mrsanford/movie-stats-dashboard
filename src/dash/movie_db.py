from src.database.database import BaseDB
from src.utils.helpers import MOVIZ_DB_PATH
import pandas as pd

MOVIE_DB_PATH = 'data/processedmovies.sqlite'


class MoVIZ(BaseDB):
    def __init__(self):
        super().__init__(path=MOVIE_DB_PATH, create=True)
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

    def get_filtered_data(
        self,
        decades: list[str] = None,
        genres: list[str] = None,
        budget_range: list[int] = None,
        revenue_range: list[int] = None,
        ratings_range: list[float] = None,
        certificates: list[str] = None) -> pd.DataFrame:
        conditions = []
        params = {}

        if decades:
            placeholders = ', '.join([f":decade_{i}" for i in range(len(decades))])
            conditions.append(f"m.decade IN ({placeholders})")
            params.update({f"decade_{i}": val for i, val in enumerate(decades)})

        if genres:
            placeholders = ', '.join([f":genre_{i}" for i in range(len(genres))])
            conditions.append(f"g.genre_name IN ({placeholders})")
            params.update({f"genre_{i}": val for i, val in enumerate(genres)})

        if budget_range:
            conditions.append("b.production_budget BETWEEN :min_budget AND :max_budget")
            params["min_budget"] = budget_range[0]
            params["max_budget"] = budget_range[1]

        if revenue_range:
            conditions.append("b.worldwide_gross BETWEEN :min_gross AND :max_gross")
            params["min_gross"] = revenue_range[0]
            params["max_gross"] = revenue_range[1]

        if ratings_range:
            conditions.append("m.rating BETWEEN :min_rating AND :max_rating")
            params["min_rating"] = ratings_range[0]
            params["max_rating"] = ratings_range[1]

        if certificates:
            placeholders = ', '.join([f":cert_{i}" for i in range(len(certificates))])
            conditions.append(f"m.certificate IN ({placeholders})")
            params.update({f"cert_{i}": val for i, val in enumerate(certificates)})

        where_clause = " AND ".join(conditions)
        sql = f"""
        SELECT m.decade, g.genre_name, m.rating, m.certificate,
               b.production_budget, b.worldwide_gross
        FROM tMovie m
        JOIN tBudget b ON m.movie_id = b.movie_id
        JOIN tMovieGenre mg ON m.movie_id = mg.movie_id
        JOIN tGenre g ON mg.genre_id = g.genre_id
        {"WHERE " + where_clause if where_clause else ""}
        """
        return self.run_query(sql, params)

    def get_all_data(self) -> pd.DataFrame:
        sql = """
        SELECT m.title, m.year, m.decade, m.rating, m.certificate,
               m.votes, m.runtime, m.production_countries,
               g.genre_name,
               b.production_budget, b.domestic_gross, b.worldwide_gross
        FROM tMovie m
        JOIN tBudget b ON m.movie_id = b.movie_id
        JOIN tMovieGenre mg ON m.movie_id = mg.movie_id
        JOIN tGenre g ON mg.genre_id = g.genre_id
        """
        return self.run_query(sql)
