from dash import Dash, dcc, html, Input, Output, State, ctx, callback, no_update
from dash.dependencies import ALL
from src.dash.movie_db import MoVIZ
import plotly.express as px
import pandas as pd
import numpy as np


custom_slider_settings = {
    "production_budget": {
        "min": 0,
        "max": 500_000_000,
        "step": 25_000_000,
        "formatter": lambda v: f"${int(v / 1e6)}M",
        "marks": {i: f"${int(i / 1e6)}M" for i in range(0, 500_000_000, 50_000_000)}
    },
    "worldwide_gross": {
        "min": 0,
        "max": 3_000_000_000,
        "step": 50_000_000,
        "formatter": lambda v: f"${int(v / 1e9)}B" if v >= 1_000_000_000 else f"${int(v / 1e6)}M",
        "marks": {i: f"${int(i / 1e6)}M" for i in range(0, 3_000_000_001, 500_000_000)}
    },
    "rating": {
        "min": 0.0,
        "max": 10.0,
        "step": 0.1,
        "formatter": lambda v: f"{v:.1f}",
        "marks": {i: f"{i:.1f}" for i in range(0, 11, 2)}
    }
}


def run_app():
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.title = "MoVIZ: Movie Visualizer"
    create_layout(app)
    app.run(debug=True)

def create_layout(app: Dash):
    db = MoVIZ()
    df = db.get_filtered_data()

    characteristics = [
        {"label": "Genre", "value": "genre_name"},
        {"label": "Decade", "value": "decade"},
        {"label": "Certificate", "value": "certificate"},
        {"label": "Rating", "value": "rating"},
        {"label": "Revenue", "value": "worldwide_gross"},
        {"label": "Budget", "value": "production_budget"},
    ]

    app.layout = html.Div(style={"fontFamily": "Calibri, sans-serif"}, children=[
        html.Div([
            html.H1("MoVIZ Visualization Tool", style={"textAlign": "center"}),
            html.P(
                "Welcome to MoVIZ, where movies and visualization meet! You can explore" \
                " budget, revenue, ratings, and other movie statistic relationships. Simply" \
                " filter your desired characteristics and what relationship you want to see, and" \
                " MoVIZ does the rest",
                style={
                    "textAlign": "center",
                    "fontSize": "16px",
                    "marginTop": "-10px",
                    "color": "#555"
                }
            )
        ]),

        html.Label("Select criteria you would like to filter:"),
        dcc.Dropdown(
            id="char-selector",
            options=characteristics,
            multi=True,
            placeholder="Filter characteristics..."
        ),
        html.Div(id="dynamic-filters", style={"marginTop": "20px"}),

        html.Div([
        html.Button("Apply Filters", id="apply-filters", n_clicks=0),
        html.Button("Clear Filters", id="clear-filters", n_clicks=0, style={"marginLeft": "10px"})
        ], style={"marginTop": "20px"}),

        html.Div(id="filter-summary", style={"marginTop": "10px", "fontSize": "15px", "color": "#333"}),

        dcc.Store(id="user-filters"),
        dcc.Store(id="filtered-data"),

        html.Div([
            html.Label("Select X and Y target variables:"),
            dcc.Dropdown(id="x-axis", placeholder="X Variable", disabled=True),
            dcc.Dropdown(id="y-axis", placeholder="Y Variable", disabled=True),
            html.Button("Go!", id="go-button", n_clicks=0)
        ], style={"marginTop": "20px"}),

        html.Hr(),
        html.Div(id="movie-count",
        style={"marginTop": "20px", "fontSize": "16px", "color": "#444", "textAlign": "center"}),
        dcc.Graph(id="main-graph")
    ])


@callback(
    Output("dynamic-filters", "children"),
    Input("char-selector", "value"),
    Input("user-filters", "data"))
def generate_filters(selected, user_filters):
    if not selected:
        return []
    db = MoVIZ()
    df = db.get_filtered_data()
    widgets = []

    # certificate disclaimer
    if "certificate" in selected:
        widgets.append(html.Div([
            html.P([
                "Note: 'Certificate' values such as 'Passed' and 'Approved' were valid classifications ",
                "under the Hays Code until 1968, when Motion Picture Association (MPAA) established ",
                "content-based rating guidelines (e.g. G, PG, PG-13, R, and X, ",
                html.I("later NC-17"),
                "). Interpret accordingly."
            ], style={"color": "crimson", "fontSize": "14px", "marginBottom": "5px"}),
            html.A(
                "Learn more about the Hays Code and film rating history here.",
                href="https://www.filmmaker.tools/what-was-hollywoods-hays-code-a-comprehensive-guide",
                target="_blank",
                style={"color": "blue", "textDecoration": "underline", "fontSize": "14px"}
            )], style={"marginBottom": "10px"}))

    for col in selected:
        print("Generating filter for column:", col, type(col))
        col_display = col.replace("_", " ").title()
        user_value = user_filters.get(col) if user_filters else None
        col_series = df[col].dropna()

        if pd.api.types.is_numeric_dtype(col_series):
            settings = custom_slider_settings.get(col, {})
            min_val = settings.get("min", col_series.min())
            max_val = settings.get("max", col_series.max())
            step = settings.get("step")
            formatter = settings.get("formatter", lambda v: str(round(v, 2)))
            marks = settings.get("marks")

            range_span = max_val - min_val
            if range_span == 0:
                marks = {round(min_val, 2): formatter(min_val)}
                slider = dcc.RangeSlider(
                    id={"type": "filter-slider", "index": str(col)},
                    min=min_val,
                    max=max_val + 1,
                    step=1,
                    value=user_value if user_value else [min_val, max_val],
                    marks=marks,
                    disabled=True,
                    tooltip={"placement": "bottom", "always_visible": True})
            elif pd.api.types.is_integer_dtype(col_series):
                if step is None or step == 0:
                    step = max(1, int(range_span / 20))
                if not marks:
                    marks = {i: formatter(i) for i in range(int(min_val), int(max_val + 1), int(step))}
                print("Creating slider for:", col, "→ ID:", {"type": "filter-slider", "index": str(col)})
                slider = dcc.RangeSlider(
                    id={"type": "filter-slider", "index": str(col)},
                    min=int(min_val),
                    max=int(max_val),
                    step=int(step),
                    value=user_value if user_value else [int(min_val), int(max_val)],
                    marks=marks,
                    tooltip={"placement": "bottom", "always_visible": True})
            else:
                if step is None or step == 0:
                    step = round(range_span / 20, 2)
                if not marks:
                    tick_vals = np.arange(min_val, max_val + step, step)
                    marks = {round(v, 2): formatter(v) for v in tick_vals}
                print("Creating slider for:", col, "→ ID:", {"type": "filter-slider", "index": str(col)})
                slider = dcc.RangeSlider(
                    id={"type": "filter-slider", "index": str(col)},
                    min=min_val,
                    max=max_val,
                    step=step,
                    value=user_value if user_value else [min_val, max_val],
                    marks=marks,
                    tooltip={"placement": "bottom", "always_visible": True})
            widgets.append(html.Div([
                html.Label(f"{col_display} Range"),
                slider], style={"marginTop": "15px"}))
        else:
            options = sorted(col_series.unique())
            print("Creating dropdown for:", col, "→ ID:", {"type": "filter-dropdown", "index": str(col)})
            dropdown = dcc.Dropdown(
                id={"type": "filter-dropdown", "index": str(col)},
                options=[{"label": v, "value": v} for v in options],
                multi=True,
                value=user_value if user_value else None)
            widgets.append(html.Div([
                html.Label(f"Select {col_display}"),
                dropdown], style={"marginTop": "15px"}))
    return widgets


@callback(
    Output("user-filters", "data"),
    Output("char-selector", "value"),
    Output("x-axis", "value"),
    Output("y-axis", "value"),
    Input("apply-filters", "n_clicks"),
    Input("clear-filters", "n_clicks"),
    State("char-selector", "value"),
    State({"type": "filter-slider", "index": ALL}, "value"),
    State({"type": "filter-slider", "index": ALL}, "index"),
    State({"type": "filter-dropdown", "index": ALL}, "value"),
    State({"type": "filter-dropdown", "index": ALL}, "index"))
def store_user_filters(apply_clicks, clear_clicks, selected, slider_vals, slider_keys, drop_vals, drop_keys):
    triggered = ctx.triggered_id
    if triggered == "clear-filters":
        return {}, None, None, None  # full reset
    filters = {}
    # adding slider filters
    for i, col in enumerate(slider_keys):
        if col and col != 'null':
            filters[col] = slider_vals[i]
    # adding dropdown filters
    for i, col in enumerate(drop_keys):
        if col and col != 'null':
            filters[col] = drop_vals[i]
    print("Triggered store_user_filters:", ctx.triggered_id)
    print("Slider keys:", slider_keys)
    print("Slider values:", slider_vals)
    print("Dropdown keys:", drop_keys)
    print("Dropdown values:", drop_vals)
    return filters, no_update, no_update, no_update
    

@callback(
    Output("filter-summary", "children"),
    Input("user-filters", "data")
)
def display_filter_summary(filters):
    if not filters:
        return "No filters applied. Showing all movies."
    def format_value(val):
        if isinstance(val, list):
            if all(isinstance(x, (int, float)) for x in val) and len(val) == 2:
                return f"{val[0]} to {val[1]}"
            return ", ".join(str(x) for x in val)
        return str(val)
    parts = [f"{key.replace('_', ' ').title()}: {format_value(value)}"
             for key, value in filters.items() if value]
    return "Filters applied — " + "; ".join(parts)


@callback(Output("filtered-data", "data"), Input("user-filters", "data"))
def filter_data(filters):
    db = MoVIZ()
    full_df = db.get_filtered_data()
    print("Applying filters to dataframe:", filters)
    # if no filters are selected, full available data is returned
    if not filters:
        return full_df.to_dict("records")
    df = full_df.copy()
    for key, user_val in filters.items():
        if user_val is None:
            continue
        col_data = full_df[key].dropna()
        # handling categorical filters (e.g. dropdowns)
        if isinstance(user_val, list) and col_data.dtype == "object":
            all_vals = set(col_data.unique())
            selected_vals = set(user_val)
            if selected_vals != all_vals:
                df = df[df[key].isin(user_val)]
        # handling numeric range sliders
        elif isinstance(user_val, list) and pd.api.types.is_numeric_dtype(col_data):
            sel_min, sel_max = user_val
            df = df[df[key].between(sel_min, sel_max)]
    return df.to_dict("records")

@callback(
    Output("movie-count", "children"),
    Input("filtered-data", "data"))
def update_movie_count(data):
    if not data:
        return "No movies match your filters."
    return f"{len(data)} movies match your filters."

@callback(
    Output("x-axis", "options"),
    Output("y-axis", "options"),
    Output("x-axis", "disabled"),
    Output("y-axis", "disabled"),
    Input("filtered-data", "data"))
def update_axis_options(data):
    if not data:
        return [], [], True, True
    df = pd.DataFrame(data)
    # allowing only numeric and categorical columns that are useful
    possible_x_y_cols = ["rating", "worldwide_gross", "production_budget", "decade", "certificate", "genre_name"]
    available = [col for col in possible_x_y_cols if col in df.columns and df[col].notna().any()]
    options = [{"label": col.replace("_", " ").title(), "value": col} for col in available]
    return options, options, False, False


@callback(Output("main-graph", "figure"),
    Input("go-button", "n_clicks"),
    State("filtered-data", "data"),
    State("x-axis", "value"),
    State("y-axis", "value"))
def update_graph(_, data, x, y):
    if not data or not x or not y:
        return px.scatter(title="No data or axes selected.")
    df = pd.DataFrame(data)
    x_is_numeric = pd.api.types.is_numeric_dtype(df[x])
    y_is_numeric = pd.api.types.is_numeric_dtype(df[y])

    if x_is_numeric and y_is_numeric:
        # scatterplots show individual points with movie titles + years
        fig = px.scatter(df, x=x, y=y, hover_data=["title", "year", "genre_name", "decade"])
    else:
        # bar charts aggregate y-values by x category
        grouped = df.groupby(x)[y].mean().reset_index()
        fig = px.bar(grouped, x=x, y=y, hover_data={x: True, y: True})
        fig.update_layout(title={"text": f"{x.title()} vs {y.title()}", "x": 0.5, "xanchor": "center"})
        fig.update_layout(yaxis_tickformat="~s")
        return fig
