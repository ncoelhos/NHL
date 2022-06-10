import plotly.express as px
import plotly.graph_objects as go

import plotly.io as pio

from CONSTANTS import *

pio.templates.default = "simple_white"
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
