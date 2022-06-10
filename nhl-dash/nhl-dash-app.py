# Bruno Vieira Ribeiro June, 2022

from click import style
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

# Reading saved dataframes
df_games = pd.read_pickle("assets/df_games.data")
df_teams_conceded = pd.read_pickle("assets/df_teams_conceded.data")
df_teams_season = pd.read_pickle("assets/df_teams_season.data")
shots_df = pd.read_pickle("assets/shots_df.data")

# Rink image for background in graphs
IMAGE_FILENAME1 = "assets/img/NHL-rink-white.jpg"
image1 = base64.b64encode(open(IMAGE_FILENAME1, "rb").read())

# Team ID dictionary
with open("assets/team_dict.data", "rb") as f:
    team_dict = pickle.load(f)

# Preparing list of dictionaries for dropdown options
team_options = []
for team_id, team_name in team_dict.items():
    my_dict = {}
    my_dict["label"] = team_name
    my_dict["value"] = team_id
    team_options.append(my_dict)
team_options = sorted(team_options, key=lambda k: k["label"])

# Dropdown options for event
event_options = []
for e in shots_df["event"].unique():
    my_dict = {}
    my_dict["label"] = e
    my_dict["value"] = e
    event_options.append(my_dict)

# Dropdown options for type
type_options = []
for t in shots_df["secondaryType"].unique():
    my_dict = {}
    my_dict["label"] = t
    my_dict["value"] = t
    type_options.append(my_dict)

#####################################
# Plotting functions
def team_goals(team_id, df_pro=df_teams_season, df_con=df_teams_conceded):
    """Create plotly figure with line plots of goals scored and conceded
    for a given `team` across seasons"""

    fig = go.Figure()

    fig.add_scatter(
        x=df_pro[df_pro["team_id"] == team_id]["season"],
        y=df_pro[df_pro["team_id"] == team_id]["number_of_goals"],
        name="Scored",
        line=dict(color="#0f3e66"),
    )

    fig.add_scatter(
        x=df_con[df_con["team_id"] == team_id]["season"],
        y=df_con[df_con["team_id"] == team_id]["goals_conceded"],
        name="Conceded",
        line=dict(color="#b53312"),
    )

    fig.update_layout(
        title="Goals - " + team_dict[team_id], xaxis_title="Season", yaxis_title="Goals"
    )
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(tickangle=45)

    # Transparent background
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )

    return fig


def plot_heatmap_from_df(season, team_id, event, df=shots_df):
    """
    DOCUMENT THIS!
    """
    df = df.query(f"season == '{season}' and team_id_for == '{team_id}'")

    fig = px.density_heatmap(
        df.query(f"event == '{event}'"),
        x="st_x",
        y="st_y",
        nbinsx=80,
        nbinsy=40,
        range_x=[-100, 100],
        range_y=[-45, 45],
        color_continuous_scale="Reds",
        title=team_dict[team_id] + " " + str(season) + " " + event + "s",
    )

    fig.update_traces(opacity=0.6)

    fig.add_layout_image(
        dict(
            source="data:image/jpg;base64,{}".format(image1.decode()),
            xref="x",
            yref="y",
            x=-100,
            y=42.5,
            sizex=200,
            sizey=85,
            sizing="stretch",
            opacity=1,
            layer="below",
        )
    )

    fig.update_layout(template="simple_white")

    # legend
    fig.update_layout(showlegend=False)

    # x axis
    fig.update_xaxes(visible=False)

    # y axis
    fig.update_yaxes(visible=False)

    # Transparent background
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )

    return fig


def plot_shot_type(season, team_id, shot_type, game_id=None, df=shots_df):
    """
    Plots shot position with background rink (NHL official size).
    Arguments:
    - con: conncetion to nhl database (given in project folder or converted from kaggle dataset)
    - season: integer value of start year of season (currently available: 2000 to 2019)
    - team_id: ID of team as given by the table team_info
    - shot_type: secondary event type of shot events.
        * Available: 'Wrist Shot', 'Slap Shot', 'Snap Shot', 'Backhand', 'Tip-In', 'Deflected', 'Wrap-around'.
    - game_id (optional): if None is given, plots the entire season. Otherwise, plots only shots for specific game_id.
    """

    df = df.query(f"season == '{season}' and team_id_for == '{team_id}'")

    if game_id:
        df = df.query(f"secondaryType == '{shot_type}' and game_id == {game_id}")
        title = (
            team_dict[team_id]
            + " "
            + str(season)
            + " Game ID: "
            + str(game_id)
            + " "
            + shot_type
            + f"s <br><sup>{len(df)} shots</sup>"
        )

    else:
        df = df.query(f"secondaryType == '{shot_type}'")
        title = (
            team_dict[team_id]
            + " "
            + str(season)
            + " "
            + shot_type
            + f"s <br><sup>{len(df)} shots</sup>"
        )

    number_of_shots = len(df)

    marker_size = 10
    marker_width = 1

    fig = px.scatter(
        df,
        x="st_x",
        y="st_y",
        color="event",
        symbol="event",
        range_x=[-100, 100],
        range_y=[-45, 45],
        title=title,
        # color_discrete_map={  # replaces default color mapping by value
        #     "Goal": "DarkRed",
        #     "Shot": "LawnGreen",
        # },
        symbol_map={  # replaces default symbol mapping by value
            "Shot": "x",
            "Goal": "circle",
        },
    )

    fig.update_traces(
        marker=dict(
            size=marker_size, line=dict(width=marker_width, color="DarkSlateGrey")
        ),
        selector=dict(mode="markers"),
        opacity=0.6,
    )

    fig.add_layout_image(
        dict(
            source="data:image/jpg;base64,{}".format(image1.decode()),
            xref="x",
            yref="y",
            x=-100,
            y=42.5,
            sizex=200,
            sizey=85,
            sizing="stretch",
            opacity=0.8,
            layer="below",
        )
    )

    # x axis
    fig.update_xaxes(visible=False)

    # y axis
    fig.update_yaxes(visible=False)

    # Set templates
    fig.update_layout(template="plotly_white")

    # Transparent background
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )

    return fig


#####################################
# Background image settings
BG_STYLE = {
    "background-image": "url(assets/img/BG.jpg)",
    "background-color": "rgba(255,255,255,0.8)",
    "background-size": "cover",
    "background-repeat": "no-repeat",
    "opacity": "1",
    "background-blend-mode": "lighten",
    "padding": "1.5rem 2rem",
}
# Background image source: https://cdn.wallpapersafari.com/49/8/qo8Kmg.jpg

######################## Start of app
# app = Dash(__name__)
app = Dash(__name__, external_stylesheets=[dbc.themes.UNITED])

# fig = team_goals(20)
# heat_fig = plot_heatmap_from_df(2019, 20, "Goal")
# scatter_fig = plot_shot_type(2014, 20, "Slap Shot")

app.layout = html.Div(
    [
        html.H1(children="NHL - Game Explorer"),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="team-choice",
                        options=team_options,
                        style={"color": "#000000"},
                        value=20,
                        placeholder="Select team...",
                    ),
                    width=3,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="season-choice",
                        # options=season_options,
                        style={"color": "#000000"},
                        # value="2019",
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
                            value="Goal",
                            placeholder="Select event...",
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
            dbc.CardImg(src=f"assets/logos_id/{team}.gif", top=True),
        ],
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
        team_against = shots_df.query(f"game_id == {game} and team_id_for == '{team}'")[
            "team_id_against"
        ].values[0]
        card = dbc.Card(
            [
                dbc.CardImg(src=f"assets/logos_id/{team_against}.gif", top=True),
            ],
        )
        return card


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

        team_against = shots_df.query(f"game_id == {game} and team_id_for == '{team}'")[
            "team_id_against"
        ].values[0]

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
