from dash import Dash, dcc, html, Input, Output, callback
from src.database.database import MovieDB
import plotly.express as px


def run_app() -> None:
    app = Dash(__name__)
    app.title = "MoVIZ: Movie Data Visualizer"
    create_layout(app)
    app.run(debug=True)


def create_layout(app: Dash) -> None:
    db = MovieDB()
    
    layout = html.Div([
        html.H1("MoVIZ: Explore Movie Trends"),
        html.Hr(),

        html.Label("Select a Genre"),
        dcc.Dropdown(id="genre-dd", options=[""] + db.get_genre_list(), value=""),

        html.Label("Select a Decade", id="decade-label"),
        dcc.Dropdown(id="decade-dd", options=[], value=""),

        html.Label("Select a Movie Title", id="movie-label"),
        dcc.Dropdown(id="movie-dd", options=[], value=""),

        html.H2(id="figure-title"),

        dcc.Graph(id="my-figure"),
    ])

    app.layout = layout


@callback(
    Output("decade-dd", "options"),
    Output("decade-dd", "style"),
    Output("decade-label", "style"),
    Input("genre-dd", "value")
)
def update_decade_options(genre: str):
    if not genre:
        return [], {"display": "none"}, {"display": "none"}
    vals = MovieDB().get_decade_list(genre)
    style = {"display": "block"} if vals else {"display": "none"}
    return [""] + vals, style, style


@callback(
    Output("movie-dd", "options"),
    Output("movie-dd", "style"),
    Output("movie-label", "style"),
    Input("genre-dd", "value"),
    Input("decade-dd", "value")
)
def update_movie_options(genre: str, decade: str):
    if not (genre and decade):
        return [], {"display": "none"}, {"display": "none"}
    vals = MovieDB().get_title_list(genre, decade)
    style = {"display": "block"} if vals else {"display": "none"}
    return [""] + vals, style, style


@callback(
    Output("my-figure", "figure"),
    Output("figure-title", "children"),
    Input("genre-dd", "value"),
    Input("decade-dd", "value"),
    Input("movie-dd", "value")
)
def update_figure(genre: str, decade: str, title: str):
    df = MovieDB().get_data(genre, decade, title)
    
    fig_title = ""
    if genre:
        fig_title += f"Genre: {genre}"
    if decade:
        fig_title += f" | Decade: {decade}"
    if title:
        fig_title += f" | Movie: {title}"

    fig = px.scatter(df, x="x", y="y", labels={"x": "Production Budget", "y": "Worldwide Gross"})
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(title="Budget vs. Gross")

    return fig, fig_title


if __name__ == "__main__":
    run_app()
