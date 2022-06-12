from cgi import test
import sqlite3 as sql
import pandas as pd

print("=== Connecting to database")

con = sql.connect("nhl-data.db")
cur = con.cursor()

print("=== Extracting data")
# Get our data for modeling
query = """
SELECT
    SUBSTR(game_id, 1, 4) AS season,
    team_id_for, team_id_against,
    event,
    period, periodTime,
    st_x, st_y
FROM
    game_plays
WHERE
    event IN ('Goal', 'Shot', 'Missed Shot')
    AND
        (x <> 'NA' AND y <> 'NA')
ORDER BY
    season, play_id;
"""

model_df = pd.read_sql(query, con)

# Numeric columns
num_cols = [
    "season",
    "team_id_for",
    "team_id_against",
    "period",
    "periodTime",
    "st_x",
    "st_y",
]

# Transform numeric columns to numeric types
model_df[num_cols] = model_df[num_cols].apply(pd.to_numeric)

# model_df.info()

# Get df to pickle file
model_df.to_pickle("../SavedData/model_df.pkl")

# # Read data
# print("=== Reading data")
# model_df = pd.read_pickle("model_df.pkl")
# # model_df.info()

# Get features and target
X = model_df.drop("event", axis=1)
y = model_df["event"]

# Preprocessing
from sklearn.compose import make_column_selector, make_column_transformer
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from imblearn.ensemble import BalancedBaggingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from numpy import mean
from numpy import std

# set up preprocessing for numeric columns
scaler = StandardScaler()

# set up preprocessing for categorical columns
ohe = OneHotEncoder()

# select columns by data type
num_cols = make_column_selector(dtype_include="number")
cat_cols = make_column_selector(dtype_exclude="number")

# Build categorical preprocessor
categorical_pipe = make_pipeline(ohe)

# Build numeric processor
numeric_pipe = make_pipeline(scaler)

# Full processor
full = ColumnTransformer(
    transformers=[
        ("categorical", categorical_pipe, cat_cols),
        ("numeric", numeric_pipe, num_cols),
    ]
)

# Trying different models
test_models = {
    "BalancedBaggingClassifier": BalancedBaggingClassifier(random_state=42),
    "RandomForestClassWeight": RandomForestClassifier(
        n_estimators=10, class_weight="balanced", random_state=42
    ),
    "RandomForestBoostrapClassWeight": RandomForestClassifier(
        n_estimators=10, class_weight="balanced_subsample", random_state=42
    ),
}

model_list = []
model_acc = []

# evaluate a model
def evaluate_model(X, y, model):
    # define evaluation procedure
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=1)
    # evaluate model
    scores = cross_val_score(model, X, y, scoring="accuracy", cv=cv)
    return scores


for model_name, model in test_models.items():
    print("=== Running model: " + model_name)
    # Define model
    # model = BalancedBaggingClassifier()

    # Final pipeline combined with model
    pipeline = Pipeline(
        steps=[
            ("preprocess", full),
            ("base", model),
        ]
    )

    print("Evaluating model")

    # evaluate the model
    scores = evaluate_model(X, y, pipeline)
    # summarize performance
    print(model_name + "---Mean Accuracy: %.3f (%.3f)" % (mean(scores), std(scores)))
    model_list.append(model_name)
    model_acc.append(mean(scores))

# Putting it all together in the dataframe
results = pd.DataFrame(
    {
        "model": model_list,
        "mean_accuracy": model_acc,
    }
)

print(results.to_markdown())
