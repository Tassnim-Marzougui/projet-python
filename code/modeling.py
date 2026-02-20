import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import joblib
import os
import json
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                              recall_score, confusion_matrix, classification_report)
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier
from datetime import datetime

print("=" * 60)
print("   MODELISATION - NURSERY DATASET")
print("=" * 60)

X_train = pd.read_csv('data/processed/X_train.csv')
X_test  = pd.read_csv('data/processed/X_test.csv')
y_train = pd.read_csv('data/processed/y_train.csv').values.ravel()
y_test  = pd.read_csv('data/processed/y_test.csv').values.ravel()
class_order = joblib.load('data/models/encoders/class_order.pkl')

print(f"\n[1] Donnees chargees :")
print(f"    X_train : {X_train.shape} | X_test : {X_test.shape}")
print(f"    Classes : {class_order}")

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("Nursery_Classification")
print("\n[2] MLflow configure -> http://127.0.0.1:5000")

def evaluate_model(model, X_test, y_test, class_order):
    y_pred = model.predict(X_test)
    metrics = {
        'accuracy':           round(accuracy_score(y_test, y_pred), 4),
        'f1_weighted':        round(f1_score(y_test, y_pred, average='weighted', zero_division=0), 4),
        'f1_macro':           round(f1_score(y_test, y_pred, average='macro',    zero_division=0), 4),
        'precision_weighted': round(precision_score(y_test, y_pred, average='weighted', zero_division=0), 4),
        'recall_weighted':    round(recall_score(y_test, y_pred, average='weighted',    zero_division=0), 4),
    }
    labels_present = sorted(np.unique(y_test))
    names_present  = [class_order[i] for i in labels_present]
    cm     = confusion_matrix(y_test, y_pred, labels=labels_present)
    report = classification_report(y_test, y_pred, labels=labels_present,
                                   target_names=names_present, zero_division=0)
    return metrics, cm, report

print("\n" + "=" * 60)
print("   [3] RANDOM FOREST - GridSearchCV")
print("=" * 60)

rf_params = {
    'n_estimators':      [100, 200],
    'max_depth':         [None, 10, 20],
    'min_samples_split': [2, 5],
    'class_weight':      ['balanced']
}
rf_grid = GridSearchCV(
    RandomForestClassifier(random_state=42),
    rf_params, cv=5, scoring='f1_macro', n_jobs=-1, verbose=1
)
print("GridSearchCV en cours (patience...)")
rf_grid.fit(X_train, y_train)
best_rf = rf_grid.best_estimator_

print(f"\nMeilleurs parametres RF : {rf_grid.best_params_}")
print(f"Meilleur score CV       : {rf_grid.best_score_:.4f}")

rf_metrics, rf_cm, rf_report = evaluate_model(best_rf, X_test, y_test, class_order)
print(f"\nResultats sur Test Set :")
for k, v in rf_metrics.items():
    print(f"  {k:<25} : {v}")
print(f"\nRapport de classification :\n{rf_report}")

with mlflow.start_run(run_name="RandomForest_GridSearch"):
    mlflow.log_params(rf_grid.best_params_)
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("cv_folds", 5)
    mlflow.log_param("scoring", "f1_macro")
    mlflow.log_param("train_size", len(X_train))
    mlflow.log_param("test_size", len(X_test))
    mlflow.log_metrics(rf_metrics)
    mlflow.log_metric("cv_best_score", rf_grid.best_score_)
    mlflow.sklearn.log_model(best_rf, "random_forest_model")
    os.makedirs('data/models', exist_ok=True)
    cm_path = 'data/models/rf_confusion_matrix.txt'
    np.savetxt(cm_path, rf_cm, fmt='%d')
    mlflow.log_artifact(cm_path)
    report_path = 'data/models/rf_classification_report.txt'
    with open(report_path, 'w') as f:
        f.write(rf_report)
    mlflow.log_artifact(report_path)
    rf_run_id = mlflow.active_run().info.run_id
    print(f"\n[MLflow] Run Random Forest enregistre : {rf_run_id[:8]}...")

print("\n" + "=" * 60)
print("   [4] XGBOOST - GridSearchCV")
print("=" * 60)

xgb_params = {
    'n_estimators':  [100, 200],
    'max_depth':     [3, 6, 9],
    'learning_rate': [0.01, 0.1],
    'subsample':     [0.8, 1.0],
}
xgb_grid = GridSearchCV(
    XGBClassifier(random_state=42, eval_metric='mlogloss', verbosity=0),
    xgb_params, cv=5, scoring='f1_macro', n_jobs=-1, verbose=1
)
print("GridSearchCV en cours (patience...)")
xgb_grid.fit(X_train, y_train)
best_xgb = xgb_grid.best_estimator_

print(f"\nMeilleurs parametres XGB : {xgb_grid.best_params_}")
print(f"Meilleur score CV        : {xgb_grid.best_score_:.4f}")

xgb_metrics, xgb_cm, xgb_report = evaluate_model(best_xgb, X_test, y_test, class_order)
print(f"\nResultats sur Test Set :")
for k, v in xgb_metrics.items():
    print(f"  {k:<25} : {v}")
print(f"\nRapport de classification :\n{xgb_report}")

with mlflow.start_run(run_name="XGBoost_GridSearch"):
    mlflow.log_params(xgb_grid.best_params_)
    mlflow.log_param("model_type", "XGBoost")
    mlflow.log_param("cv_folds", 5)
    mlflow.log_param("scoring", "f1_macro")
    mlflow.log_param("train_size", len(X_train))
    mlflow.log_param("test_size", len(X_test))
    mlflow.log_metrics(xgb_metrics)
    mlflow.log_metric("cv_best_score", xgb_grid.best_score_)
    mlflow.sklearn.log_model(best_xgb, "xgboost_model")
    cm_path = 'data/models/xgb_confusion_matrix.txt'
    np.savetxt(cm_path, xgb_cm, fmt='%d')
    mlflow.log_artifact(cm_path)
    report_path = 'data/models/xgb_classification_report.txt'
    with open(report_path, 'w') as f:
        f.write(xgb_report)
    mlflow.log_artifact(report_path)
    xgb_run_id = mlflow.active_run().info.run_id
    print(f"\n[MLflow] Run XGBoost enregistre : {xgb_run_id[:8]}...")

print("\n" + "=" * 60)
print("   [5] COMPARAISON DES MODELES")
print("=" * 60)

print(f"\n{'Metrique':<25} {'Random Forest':>15} {'XGBoost':>15}")
print("-" * 57)
for k in rf_metrics:
    print(f"{k:<25} {rf_metrics[k]:>15.4f} {xgb_metrics[k]:>15.4f}")

if rf_metrics['f1_macro'] >= xgb_metrics['f1_macro']:
    best_model, best_model_name, best_metrics, best_run_id = best_rf, "RandomForest", rf_metrics, rf_run_id
    print(f"\n=> MEILLEUR MODELE : Random Forest (F1-macro={rf_metrics['f1_macro']:.4f})")
else:
    best_model, best_model_name, best_metrics, best_run_id = best_xgb, "XGBoost", xgb_metrics, xgb_run_id
    print(f"\n=> MEILLEUR MODELE : XGBoost (F1-macro={xgb_metrics['f1_macro']:.4f})")

os.makedirs('data/models', exist_ok=True)
joblib.dump(best_model, 'data/models/best_model.pkl')

model_info = {
    "model_name":  best_model_name,
    "trained_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "metrics":     best_metrics,
    "class_order": class_order,
    "features":    list(X_train.columns),
    "rf_run_id":   rf_run_id,
    "xgb_run_id":  xgb_run_id,
    "best_run_id": best_run_id,
}
with open('data/models/model_info.json', 'w') as f:
    json.dump(model_info, f, indent=2)

print(f"\n[6] Meilleur modele sauvegarde  : data/models/best_model.pkl")
print(f"[7] Infos modele sauvegardees   : data/models/model_info.json")
print(f"""
+====================================================+
|        MODELISATION TERMINEE AVEC SUCCES          |
+====================================================+
  Meilleur modele  : {best_model_name}
  Accuracy         : {best_metrics['accuracy']:.4f}
  F1-weighted      : {best_metrics['f1_weighted']:.4f}
  F1-macro         : {best_metrics['f1_macro']:.4f}
  MLflow UI        : http://127.0.0.1:5000
+====================================================+
""")