import lightgbm as lgb
import neptune.new as neptune
import neptune.new.integrations.optuna as optuna_utils
import optuna
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split


def objective(trial):
    data, target = load_breast_cancer(return_X_y=True)
    train_x, test_x, train_y, test_y = train_test_split(data, target, test_size=0.25)
    dtrain = lgb.Dataset(train_x, label=train_y)

    param = {
        "verbose": -1,
        "objective": "binary",
        "metric": "binary_logloss",
        "num_leaves": trial.suggest_int("num_leaves", 2, 256),
        "feature_fraction": trial.suggest_uniform("feature_fraction", 0.2, 1.0),
        "bagging_fraction": trial.suggest_uniform("bagging_fraction", 0.2, 1.0),
        "min_child_samples": trial.suggest_int("min_child_samples", 3, 100),
    }

    gbm = lgb.train(param, dtrain)
    preds = gbm.predict(test_x)
    return roc_auc_score(test_y, preds)


# Create a Neptune run
run = neptune.init(
    api_token="ANONYMOUS", project="common/optuna-integration"
)  # you can pass your credentials here

# Pass NeptuneCallback to Optuna Study .optimize()
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=20)

# Log Optuna Study metadata
optuna_utils.log_study_metadata(study, run)

# Stop logging to a Neptune run
run.stop()
