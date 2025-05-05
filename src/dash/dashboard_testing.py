from dash import Input, Output, State, html, Dash, dcc
from dash import ctx, no_update, callback  # importing dash variables/function
from dash.dependencies import ALL
from src.dash.movie_db import MoVIZ
import plotly.express as px
import pandas as pd


def run_app() -> None:
    app = Dash(__name__)
    app.title = "MoVIZ Visualizer Tool"
    create_layout(app)
    app.run(debug=True)
    return None


def create_layout(app: Dash):
    db = MoVIZ()
    df = db.get_filtered_data()

    filter_characteristics = [
        {"label": "Genre", "value": "genre_name"},
        {"label": "Decade", "value": "decade"},
        {"label": "Certificate", "value": "certificate"},
        {"label": "Rating", "value": "rating"},
        {"label": "Revenue", "value": "worldwide_gross"},
        {"label": "Budget", "value": "production_budget"},
    ]

    header = html.Div(
        [
            html.H1("MoVIZ Visualization Explorer", style={"textAlign": "center"}),
            html.P(
                "Welcome to MoVIZ, where movies and visualization meet! You can explore "
                "budget, revenue, ratings, and other movie statistic relationships. Simply "
                "filter your desired characteristics and what relationship you want to see, and "
                "MoVIZ does the rest.",
                style={
                    "textAlign": "center",
                    "fontSize": "16px",
                    "marginTop": "-10px",
                    "color": "#555",
                },
            ),
        ],
        style={
            "fontFamily": "Calibri, sans-serif",
            "padding": "20px",
            "backgroundColor": "#f1f1f1",
            "borderRadius": "8px",
            "boxShadow": "0px 4px 10px rgba(0,0,0,0.05)",
        },
    )

    cat_label = html.Div(
        [
            html.Label("Select criteria you would like to filter:"),
            dcc.Dropdown(
                id="char-selector",
                options=filter_characteristics,
                multi=True,
                placeholder="Filter characteristics...",
            ),
            html.Div(id="dynamic-filters", style={"marginTop": "20px"}),
        ],
        style={
            "padding": "20px",
            "backgroundColor": "#fff",
            "borderRadius": "8px",
            "boxShadow": "0px 4px 10px rgba(0,0,0,0.05)",
        },
    )

    filter_controls = html.Div(
        [
            html.Button("Apply Filters", id="apply-filters", n_clicks=0),
            html.Button(
                "Clear Filters",
                id="clear-filters",
                n_clicks=0,
                style={"marginLeft": "10px"},
            ),
        ],
        style={"marginTop": "20px"},
    )

    filter_summary = html.Div(
        id="filter-summary",
        style={"marginTop": "10px", "fontSize": "15px", "color": "#333"},
    )

    stores = html.Div(
        [dcc.Store(id="user-filters", data={}), dcc.Store(id="filtered-data")]
    )

    axis_dd = html.Div(
        [
            html.Label("Select X and Y target variables:"),
            dcc.Dropdown(id="x-axis", placeholder="X Variable", disabled=True),
            dcc.Dropdown(id="y-axis", placeholder="Y Variable", disabled=True),
            html.Button("Go!", id="go-button", n_clicks=0),
        ],
        style={
            "marginTop": "20px",
            "padding": "20px",
            "backgroundColor": "#fff",
            "borderRadius": "8px",
            "boxShadow": "0px 4px 10px rgba(0,0,0,0.05)",
        },
    )

    graph_display = html.Div(
        [
            html.Hr(),
            html.Div(
                id="movie-count",
                style={
                    "marginTop": "20px",
                    "fontSize": "16px",
                    "color": "#444",
                    "textAlign": "center",
                },
            ),
            dcc.Loading(
                id="loading-graph", type="default", children=dcc.Graph(id="main-graph")
            ),
        ],
        style={
            "padding": "20px",
            "backgroundColor": "#fff",
            "borderRadius": "8px",
            "boxShadow": "0px 4px 10px rgba(0,0,0,0.05)",
        },
    )

    layout_style = {
        "fontFamily": "Calibri, sans-serif",
        "backgroundColor": "#fafafa",
        "padding": "30px",
        "maxWidth": "1100px",
        "margin": "auto",
    }

    children = [
        header,
        html.Hr(),
        cat_label,
        filter_controls,
        filter_summary,
        stores,
        axis_dd,
        graph_display,
    ]
    app.layout = html.Div(children=children, style=layout_style)


@callback(
    Output("dynamic-filters", "children"),
    Input("char-selector", "value"),
    Input("user-filters", "data"),
)
def generate_filter_widgets(selected, user_filters):
    custom_slider_settings = {
        "rating": {
            "step": 0.1,
            "marks": {i: str(i) for i in range(0, 11)},  # 0 to 10
        },
        "production_budget": {
            "step": 25_000_000,
            "marks": {
                0: "0",
                50_000_000: "50M",
                100_000_000: "100M",
                250_000_000: "250M",
                500_000_000: "500M",
            },
        },
        "worldwide_gross": {
            "step": 50_000_000,
            "marks": {
                0: "0",
                100_000_000: "100M",
                250_000_000: "250M",
                500_000_000: "500M",
                1_000_000_000: "1B",
                2_000_000_000: "2B",
                3_000_000_000: "3B",
            },
        },
    }
    if not selected:
        return []
    df = MoVIZ().get_filtered_data(**(user_filters or {}))
    widgets = []

    if "certificate" in selected:
        widgets.append(
            html.Div(
                [
                    html.P(
                        [
                            "Note: Certificate values such as 'Passed' and 'Approved' were classifications under the ",
                            "Hays Code, which was enforced until 1968. That year, the Motion Picture Association (MPAA) ",
                            "introduced content-based rating guidelines such as G, PG, PG-13, R, and X ",
                            html.I("(later renamed NC-17)"),
                            ". While many pre-1968 films have been reclassified, some still retain their original labels. ",
                            "Please interpret accordingly.",
                        ],
                        style={
                            "color": "crimson",
                            "fontSize": "14px",
                            "marginBottom": "5px",
                        },
                    ),
                    html.A(
                        "Learn more about the Hays Code and the history of film ratings.",
                        href="https://www.filmmaker.tools/what-was-hollywoods-hays-code-a-comprehensive-guide",
                        target="_blank",
                        style={
                            "color": "blue",
                            "textDecoration": "underline",
                            "fontSize": "14px",
                        },
                    ),
                ],
                style={"marginBottom": "10px"},
            )
        )

    for col in selected:
        col_series = df[col].dropna()
        user_val = user_filters.get(col) if user_filters else None

        if pd.api.types.is_numeric_dtype(col_series):
            min_val, max_val = col_series.min(), col_series.max()
            default_val = (
                user_val
                if isinstance(user_val, list) and len(user_val) == 2
                else [min_val, max_val]
            )

            settings = custom_slider_settings.get(col, {})
            step = settings.get("step", (max_val - min_val) / 100 or 1)
            marks = settings.get("marks", None)

            slider = dcc.RangeSlider(
                id={"type": "filter-slider", "index": col},
                min=min_val,
                max=max_val,
                step=step,
                value=default_val,
                marks=marks,
                tooltip={"placement": "bottom", "always_visible": True},
                allowCross=False,
            )
            widgets.append(
                html.Div(
                    [html.Label(f"{col.replace('_', ' ').title()} Range"), slider],
                    style={"marginBottom": "20px"},
                )
            )
            fig = px.histogram(col_series, nbins=30)
            dcc.Graph(
                figure=fig, config={"displayModeBar": False}, style={"height": "100px"}
            )
        else:
            options = sorted(col_series.unique())
            dropdown = dcc.Dropdown(
                id={"type": "filter-dropdown", "index": col},
                options=[{"label": v, "value": v} for v in options],
                multi=True,
                value=user_val if user_val else options,
            )
            widgets.append(
                html.Div(
                    [html.Label(f"Select {col.replace('_', ' ').title()}"), dropdown]
                )
            )
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
    State({"type": "filter-slider", "index": ALL}, "id"),
    State({"type": "filter-dropdown", "index": ALL}, "value"),
    State({"type": "filter-dropdown", "index": ALL}, "id"),
)
def store_user_filters(
    apply_clicks, clear_clicks, selected, slider_vals, slider_ids, drop_vals, drop_ids
):
    # if clear filters clicked, resets all filters
    if ctx.triggered_id == "clear-filters":
        return {}, None, None, None

    # extracting column keys from component ids
    slider_keys = [s["index"] for s in slider_ids]
    drop_keys = [d["index"] for d in drop_ids]
    # combining slider and dropdown filters into dictionary
    temp_filters = {
        key: val for key, val in zip(slider_keys + drop_keys, slider_vals + drop_vals)
    }
    # frontend column names mapped to backend column names
    filter_map = {
        "rating": "ratings_range",
        "worldwide_gross": "revenue_range",
        "production_budget": "budget_range",
        "decade": "decades",
        "genre_name": "genres",
        "certificate": "certificates",
    }
    filters = {
        filter_map[col]: temp_filters[col] for col in temp_filters if col in filter_map
    }
    return filters, no_update, no_update, no_update


@callback(Output("filter-summary", "children"), Input("user-filters", "data"))
def display_filter_summary(filters):
    if not filters:
        return "No filters applied. Showing all movies."

    def fmt(val):
        if isinstance(val, list):
            if len(val) == 2 and all(isinstance(x, (int, float)) for x in val):
                return f"{val[0]} to {val[1]}"
            return ", ".join(map(str, val))
        return str(val)

    return "Filters applied — " + "; ".join(
        [f"{k.replace('_', ' ').title()}: {fmt(v)}" for k, v in filters.items() if v]
    )


@callback(Output("filtered-data", "data"), Input("user-filters", "data"))
def filter_data(filters):
    db = MoVIZ()
    return (
        db.get_filtered_data(**filters).to_dict("records")
        if filters
        else db.get_filtered_data().to_dict("records")
    )


@callback(Output("movie-count", "children"), Input("filtered-data", "data"))
def update_movie_count(data):
    return (
        f"{len(data)} movies match your filters."
        if data
        else "No movies match your filters."
    )


@callback(
    Output("x-axis", "options"),
    Output("y-axis", "options"),
    Output("x-axis", "disabled"),
    Output("y-axis", "disabled"),
    Input("filtered-data", "data"),
)
def update_axis_options(data):
    if not data:
        return [], [], True, True
    df = pd.DataFrame(data)
    possible = [
        "rating",
        "worldwide_gross",
        "production_budget",
        "decade",
        "certificate",
        "genre_name",
    ]
    available = [col for col in possible if col in df.columns and df[col].notna().any()]
    opts = [{"label": col.replace("_", " ").title(), "value": col} for col in available]
    return opts, opts, False, False


@callback(
    Output("main-graph", "figure"),
    Input("go-button", "n_clicks"),
    State("filtered-data", "data"),
    State("x-axis", "value"),
    State("y-axis", "value"),
)
def update_main_graph(_, data, x, y):
    if not data or not x or not y:
        return px.scatter(title="Select X and Y axes variables to visualize movie data")

    df = pd.DataFrame(data)
    x_type = df[x].dtype
    y_type = df[y].dtype

    if pd.api.types.is_numeric_dtype(x_type) and pd.api.types.is_numeric_dtype(y_type):
        fig = px.scatter(
            df,
            x=x,
            y=y,
            hover_data=["title", "year", "genre_name", "certificate", "rating"],
            labels={x: x.replace("_", " ").title(), y: y.replace("_", " ").title()},
        )
        fig.update_layout(
            title=f"{x.replace('_', ' ').title()} vs {y.replace('_', ' ').title()}"
        )
    elif not pd.api.types.is_numeric_dtype(
        x_type
    ) and not pd.api.types.is_numeric_dtype(y_type):
        if x == "decade":
            order = sorted(df[x].dropna().unique(), key=lambda d: int(d.split("–")[0]))
            df[x] = pd.Categorical(df[x], categories=order, ordered=True)
        if y == "decade":
            order = sorted(df[y].dropna().unique(), key=lambda d: int(d.split("–")[0]))
            df[y] = pd.Categorical(df[y], categories=order, ordered=True)
        grouped = df.groupby([x, y]).size().reset_index(name="count")
        fig = px.bar(
            grouped,
            x=x,
            y="count",
            color=y,
            barmode="stack",
            labels={
                "\
                             count": "Count",
                x: x.replace("_", " ").title(),
                y: y.replace("_", " ").title(),
            },
            title=f"{x.replace('_', ' ').title()} by {y.replace('_', ' ').title()}",
        )
    else:
        grouped = df.groupby(x)[y].mean(numeric_only=True).reset_index()
        fig = px.bar(
            grouped,
            x=x,
            y=y,
            labels={
                x: x.replace("_", " ").title(),
                y: f"Avg {y.replace('_', ' ').title()}",
            },
            title=f"Avg {y.replace('_', ' ').title()} by {x.replace('_', ' ').title()}",
        )
        fig.update_layout(xaxis_tickangle=-45)
    return fig
