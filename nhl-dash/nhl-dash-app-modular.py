# Bruno Vieira Ribeiro June, 2022

from matplotlib.pyplot import figure
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pickle
import base64

import plotly.io as pio

pio.templates.default = "simple_white"

from CONSTANTS import *
from functions import *

######################## Start of app
# app = Dash(__name__)
app = Dash(__name__, external_stylesheets=[dbc.themes.UNITED])

app.layout = html.Div(
    [
        html.H1(children="NHL - Game Explorer", style={"font-family": "Fantasy"}),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="team-choice",
                        options=team_options,
                        style={"color": "#000000"},
                        value=20,
                        placeholder="Select team...",
                        clearable=False,
                    ),
                    width=3,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="season-choice",
                        style={"color": "#000000"},
                        placeholder="Select season...",
                    ),
                    width=3,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="type-choice",
                        options=type_options,
                        style={"color": "#000000"},
                        value="Wrist Shot",
                        placeholder="Select type of event...",
                        clearable=False,
                    ),
                    width=3,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="game-choice",
                        style={"color": "#000000"},
                        placeholder="Select game...",
                        clearable=False,
                    ),
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(id="team-for"), width=2),
                dbc.Col(
                    [
                        html.Center(id="score-board"),
                        dcc.Graph(id="scatter-types"),
                    ],
                    width={"size": 8},
                ),
                dbc.Col(html.Div(id="team-against"), width=2),
            ],
            justify="center",
            align="center",
            className="h-50",
        ),
        ############## Start of two columns for bottom charts
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="event-choice",
                            options=event_options,
                            style={"color": "#000000"},
                            value="Shot",
                            placeholder="Select event...",
                            clearable=False,
                        ),
                        dcc.Graph(
                            id="heatmap-events",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    dcc.Graph(id="goals-evo"),
                    width=6,
                ),
            ]
        ),
    ],
    style=BG_STYLE,
)
######################## End of app

############################################################# CALLBACKS
@app.callback(
    Output("goals-evo", "figure"),
    Input("team-choice", "value"),
)
def get_goals_graph(team_id):
    if not team_id:
        return None
    else:
        return team_goals(team_id)


##############################
@app.callback(
    Output("scatter-types", "figure"),
    Input("season-choice", "value"),
    Input("team-choice", "value"),
    Input("type-choice", "value"),
    Input("game-choice", "value"),
)
def get_scatter_graph(season, team_id, type, game):
    if game == "all":
        return plot_shot_type(season, team_id, type)
    else:
        return plot_shot_type(season, team_id, type, game)


##############################
@app.callback(
    Output("heatmap-events", "figure"),
    Input("team-choice", "value"),
    Input("season-choice", "value"),
    Input("event-choice", "value"),
)
def get_heatmap_graph(team_id, season, event):
    return plot_heatmap_from_df(season, team_id, event)


# DO UPDATE DROPDOWN
# SHOULD GO:
# - Select Team
# - Select Season
# - Select game (if any)
# - Select event and type (these are independent)

##############################
@app.callback(Output("season-choice", "options"), Input("team-choice", "value"))
def update_season_dropdown(team):
    # Dropdown options for seasons
    season_options = []
    for s in np.sort(shots_df[shots_df["team_id_for"] == str(team)]["season"].unique()):
        my_dict = {}
        my_dict["label"] = s
        my_dict["value"] = s
        season_options.append(my_dict)

    return season_options


##############################
@app.callback(
    Output("game-choice", "options"),
    Input("team-choice", "value"),
    Input("season-choice", "value"),
)
def update_game_dropdown(team, season):
    game_options = []
    game_options.append({"label": "all", "value": "all"})
    for e in shots_df[
        (shots_df["team_id_for"] == str(team)) & (shots_df["season"] == str(season))
    ]["game_id"].unique():
        my_dict = {}
        my_dict["label"] = df_games.query(f"game_id == {e}")["date"].values[0]
        my_dict["value"] = e
        game_options.append(my_dict)

    game_options = sorted(game_options, key=lambda k: k["label"])
    return game_options


##############################
@app.callback(
    Output("team-for", "children"),
    Input("team-choice", "value"),
)
def get_team_card(team):
    card = dbc.Card(
        [
            dbc.CardImg(
                src=f"assets/logos-Transparent/{team}.png",
                top=True,
            ),
            dbc.CardBody(html.H4(team_dict[team])),
        ],
        style={"background-color": "rgba(0,0,0,0)", "border": "none"},
    )
    return card


##############################
@app.callback(
    Output("team-against", "children"),
    Input("team-choice", "value"),
    Input("game-choice", "value"),
)
def get_team_against_card(team, game):
    if (game == "all") or game == None:
        return None
    else:
        try:
            team_against = shots_df.query(
                f"game_id == {game} and team_id_for == '{team}'"
            )["team_id_against"].values[0]

            card = dbc.Card(
                [
                    dbc.CardImg(
                        src=f"assets/logos-Transparent/{team_against}.png",
                        top=True,
                    ),
                    dbc.CardBody(html.H4(team_dict[int(team_against)])),
                ],
                style={"background-color": "rgba(0,0,0,0)", "border": "none"},
            )
            return card
        except IndexError:
            return None


##############################
@app.callback(
    Output("score-board", "children"),
    Input("game-choice", "value"),
    Input("team-choice", "value"),
)
def get_score(game, team):
    if (game == "all") or game == None:
        return None
    else:
        try:
            goals_for = shots_df.query(
                f"game_id == {game} and team_id_for == '{team}'"
            )["event"].value_counts()["Goal"]
        except KeyError:
            goals_for = 0
        except IndexError:
            goals_for = "-"

        try:
            team_against = shots_df.query(
                f"game_id == {game} and team_id_for == '{team}'"
            )["team_id_against"].values[0]
        except IndexError:
            team_against = "-"

        try:
            goals_against = shots_df.query(
                f"game_id == {game} and team_id_for == '{team_against}'"
            )["event"].value_counts()["Goal"]
        except KeyError:
            goals_against = 0

        return [
            html.H2(f"{goals_for} x {goals_against}"),
            html.H4(df_games.query(f"game_id == {game}")["venue"].values[0]),
        ]


### Run Main program
if __name__ == "__main__":
    app.run_server(debug=True)
