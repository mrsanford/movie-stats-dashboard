from dash import Dash, dcc, html, Input, Output, State, ctx, callback
from dash.dependencies import ALL
from src.dash.movie_db import MoVIZ
import plotly.express as px
import pandas as pd
import numpy as np

def run_app():
    app = Dash(__name__)
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

    app.layout = html.Div([
        html.H1("MoVIZ: Visualize Movie Stats", style={"textAlign": "center"}),

        html.Label("Select criteria you would like to filter:"),
        dcc.Dropdown(id="char-selector", options=characteristics, multi=True, placeholder="Filter characteristics..."),
        html.Div(id="dynamic-filters", style={"marginTop": "20px"}),
        html.Button("Apply Filters", id="apply-filters", n_clicks=0, style={"marginTop": "20px"}),
        dcc.Store(id="user-filters"),
        dcc.Store(id="filtered-data"),

        html.Div([
            html.Label("Select X and Y target variables:"),
            dcc.Dropdown(id="x-axis", placeholder="X Variable", disabled=True),
            dcc.Dropdown(id="y-axis", placeholder="Y Variable", disabled=True),
            html.Button("Go!", id="go-button", n_clicks=0)
        ], style={"marginTop": "20px"}),

        html.Hr(),
        dcc.Graph(id="main-graph")
    ])


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
@callback(Output("dynamic-filters", "children"), Input("char-selector", "value"))
def generate_filters(selected):
    if not selected:
        return []

    db = MoVIZ()
    df = db.get_filtered_data()
    widgets = []
    for col in selected:
        col_display = col.replace("_", " ").title()

        if pd.api.types.is_numeric_dtype(df[col]):

            col_series = df[col].dropna()

            # getting min/max from settings or data
            settings = custom_slider_settings.get(col, {})
            min_val = settings.get("min", col_series.min())
            max_val = settings.get("max", col_series.max())
            step = settings.get("step")
            formatter = settings.get("formatter", lambda v: str(round(v, 2)))

            range_span = max_val - min_val
            # if flat column (all values equal)
            if range_span == 0:
                marks = {round(min_val, 2): formatter(min_val)}
                slider = dcc.RangeSlider(
                    id={"type": "filter-slider", "index": col},
                    min=min_val,
                    max=max_val + 1,
                    step=1,
                    value=[min_val, max_val],
                    marks=marks,
                    disabled=True,
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            # int sliders (budget, revenue, votes, etc.)
            elif pd.api.types.is_integer_dtype(col_series):
                if step is None or step == 0:
                    step = max(1, int(range_span / 20))
                marks = settings.get("marks")
                if marks is None:
                    marks = {i: formatter(i) for i in range(int(min_val), int(max_val + 1), int(step))}
                slider = dcc.RangeSlider(
                    id={"type": "filter-slider", "index": col},
                    min=int(min_val),
                    max=int(max_val),
                    step=int(step),
                    value=[int(min_val), int(max_val)],
                    marks=marks,
                    tooltip={"placement": "bottom", "always_visible": True})
            else:
                # float sliders (rating, etc.)
                if step is None or step == 0:
                    step = round(range_span / 20, 2)
                tick_vals = np.arange(min_val, max_val + step, step)
                marks = settings.get("marks")
                if marks is None:
                    tick_vals = np.arange(min_val, max_val + step, step)
                    marks = {round(v, 2): formatter(v) for v in tick_vals}
                slider = dcc.RangeSlider(
                    id={"type": "filter-slider", "index": col},
                    min=min_val,
                    max=max_val,
                    step=step,
                    value=[min_val, max_val],
                    marks=marks,
                    tooltip={"placement": "bottom", "always_visible": True})
            widgets.append(html.Div([
                html.Label(f"{col_display} Range"),
                slider], style={"marginTop": "15px"}))
        else:
            # categorical fields
            options = sorted(df[col].dropna().unique())
            widgets.append(html.Div([
                html.Label(f"Select {col_display}"),
                dcc.Dropdown(
                    id={"type": "filter-dropdown", "index": col},
                    options=[{"label": v, "value": v} for v in options],
                    multi=True
                )], style={"marginTop": "15px"}))
    return widgets

@callback(Output("user-filters", "data"),
    Input("apply-filters", "n_clicks"),
    State("char-selector", "value"),
    State({"type": "filter-slider", "index": ALL}, "value"),
    State({"type": "filter-slider", "index": ALL}, "index"),
    State({"type": "filter-dropdown", "index": ALL}, "value"),
    State({"type": "filter-dropdown", "index": ALL}, "index"))
def store_user_filters(_, selected, slider_vals, slider_keys, drop_vals, drop_keys):
    filters = {}
    # add slider filters
    for i, col in enumerate(slider_keys):
        if col and col != 'null':
            filters[col] = slider_vals[i]
    # add dropdown filters
    for i, col in enumerate(drop_keys):
        if col and col != 'null':
            filters[col] = drop_vals[i]
    return filters


# @callback(Output("filtered-data", "data"), Input("user-filters", "data"))
# def filter_data(filters):
#     db = MoVIZ()
#     # if no filters are selected, full available data is returned
#     if not filters:
#         return db.get_filtered_data().to_dict("records")
#     # removing empty filters (None/empty lists)
#     clean_filters = {k: v for k, v in filters.items() if v is not None and v != []}
#     if not clean_filters:
#         return db.get_filtered_data().to_dict("records")
#     return db.get_filtered_data(**clean_filters).to_dict("records")


@callback(Output("filtered-data", "data"), Input("user-filters", "data"))
def filter_data(filters):
    db = MoVIZ()
    full_df = db.get_filtered_data()
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
            full_min, full_max = col_data.min(), col_data.max()
            sel_min, sel_max = user_val
            # only filter if user has changed the bounds
            if sel_min > full_min or sel_max < full_max:
                df = df[df[key].between(sel_min, sel_max)]
    return df.to_dict("records")


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
    columns = df.columns
    options = [{"label": col.replace("_", " ").title(), "value": col} for col in columns]
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
        fig = px.scatter(df, x=x, y=y, hover_data=["genre_name", "decade"])
    else:
        fig = px.bar(df, x=x, y=y, hover_data=["genre_name", "decade"])
    fig.update_layout(
    title={
        "text": f"{x.title()} vs {y.title()}",
        "x": 0.5,
        "xanchor": "center"})
    return fig


if __name__ == "__main__":
    run_app()
