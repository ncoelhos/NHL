import sqlite3 as sql
import pandas as pd


# Read data
print("=== Reading data")
model_df = pd.read_pickle("../SavedData/model_df.pkl")
# model_df.info()

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

model = RandomForestClassifier(n_estimators=10, class_weight="balanced")

# Final pipeline combined with model
pipeline = Pipeline(
    steps=[
        ("preprocess", full),
        ("clf", model),
    ]
)

# ## Pick best performing model and plot confusion matrix
# best_model = test_models[max(results, key=results.get)]

## Tuning best performing model:
from sklearn.model_selection import GridSearchCV

# Setting hyperparameters for our GridSearch
params = {}
params["clf__n_estimators"] = [10, 15, 20, 25, 30, 35]
params["clf__max_depth"] = [5, 10, 15, 20, 25]
params["clf__min_samples_leaf"] = [1, 2, 3, 4, 5]

cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=42)

grid = GridSearchCV(pipeline, param_grid=params, scoring="accuracy", cv=cv, verbose=2)

grid_result = grid.fit(X, y)

# convert results into a DataFrame
df_grid = pd.DataFrame(grid.cv_results_)[
    ["params", "mean_test_score", "rank_test_score"]
]

# df_grid.sort_values('rank_test_score')

df_grid.to_pickle("../SavedModels/grid_results.pkl")

best_rf = grid.best_estimator_

import joblib

# save the model to disk
filename = "../SavedModels/best_rf.sav"
joblib.dump(best_rf, filename)
