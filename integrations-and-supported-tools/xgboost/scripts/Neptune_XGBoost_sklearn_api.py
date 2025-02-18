import neptune.new as neptune
import xgboost as xgb
from neptune.new.integrations.xgboost import NeptuneCallback
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split

# Create run
run = neptune.init(
    project="common/xgboost-integration",
    api_token="ANONYMOUS",
    name="xgb-sklearn-api",
    tags=["xgb-integration", "sklearn-api"],
)

# Create neptune callback
neptune_callback = NeptuneCallback(run=run, log_tree=[0, 1, 2, 3])

# Prepare data
data = fetch_california_housing()
y = data["target"]
X = data["data"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=123
)

# Define parameters
model_params = {
    "n_estimators": 70,
    "eta": 0.7,
    "gamma": 0.001,
    "max_depth": 9,
    "objective": "reg:squarederror",
    "eval_metric": ["mae", "rmse"],
}

reg = xgb.XGBRegressor(**model_params)

# Fit the model and log metadata to the run in Neptune
reg.fit(
    X_train,
    y_train,
    early_stopping_rounds=30,
    eval_metric=["mae", "rmse"],
    eval_set=[(X_train, y_train), (X_test, y_test)],
    callbacks=[
        neptune_callback,
        xgb.callback.LearningRateScheduler(lambda epoch: 0.99**epoch),
    ],
)
