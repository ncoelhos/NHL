import pandas as pd
import pickle
import base64

# Reading saved dataframes
df_games = pd.read_pickle("assets/df_games.data")
df_teams_conceded = pd.read_pickle("assets/df_teams_conceded.data")
df_teams_season = pd.read_pickle("assets/df_teams_season.data")
shots_df = pd.read_pickle("assets/shots_df.data")

# Rink image for background in graphs
# IMAGE_FILENAME1 = "assets/img/NHL-rink-white.jpg"
IMAGE_FILENAME1 = "assets/img/NHL-rink.png"
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
