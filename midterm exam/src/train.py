"""
Mô-đun huấn luyện các mô hình Machine Learning:
- Tái hiện Thực nghiệm 1: 5 thuật toán học máy (Random Forest, Extra Trees, Decision Tree, AdaBoost, Gradient Boosting) + Baseline
- Tái hiện Thực nghiệm 2: Đánh giá K-Fold Cross Validation (K = 10)
- Tái hiện Thực nghiệm 3: Khảo sát số lượng cây (n_estimators)
- Tái hiện Thực nghiệm 4: Giảm chiều đặc trưng (Top-15 features)
- Huấn luyện trên phân chia theo trục thời gian (Temporal Split)
"""

import time
from typing import Dict, Any, Tuple, List
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    AdaBoostClassifier,
    GradientBoostingClassifier,
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from lightgbm import LGBMClassifier

from src.config import MODELS_DIR, RANDOM_STATE, MODEL_PARAMS
from src.evaluate import calculate_metrics


def build_models() -> Dict[str, Any]:
    """
    Khởi tạo các mô hình học máy theo đúng bài báo và chuẩn EMBER.
    """
    models = {
        "Baseline_LogisticRegression": LogisticRegression(**MODEL_PARAMS["LogisticRegression"]),
        "DecisionTree": DecisionTreeClassifier(**MODEL_PARAMS["DecisionTree"]),
        "AdaBoost": AdaBoostClassifier(**MODEL_PARAMS["AdaBoost"]),
        "GradientBoosting": GradientBoostingClassifier(**MODEL_PARAMS["GradientBoosting"]),
        "ExtraTrees": ExtraTreesClassifier(**MODEL_PARAMS["ExtraTrees"]),
        "RandomForest": RandomForestClassifier(**MODEL_PARAMS["RandomForest"]),
        "LightGBM": LGBMClassifier(**MODEL_PARAMS["LightGBM"]),
    }
    return models


def train_and_evaluate_single_split(
    models: Dict[str, Any],
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """
    Tái hiện Thực nghiệm 1: Huấn luyện và đo đạc trên 1 phân chia Train/Test.
    """
    results = {}
    roc_data = {}

    for name, model in models.items():
        print(f"  [Train] Đang huấn luyện mô hình: {name}...")
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = round(time.time() - start_time, 3)

        # Dự đoán
        y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
        y_pred = model.predict(X_test)

        metrics = calculate_metrics(y_test, y_pred, y_prob)
        metrics["training_time_seconds"] = train_time
        metrics["model_name"] = name
        results[name] = metrics

        if y_prob is not None:
            from sklearn.metrics import roc_curve
            fpr, tpr, _ = roc_curve(y_test, y_prob)
            roc_data[name] = {"fpr": fpr, "tpr": tpr, "auc": metrics["roc_auc"]}

        # Lưu model artifact
        joblib.dump(model, MODELS_DIR / f"{name}.joblib")

    return results, roc_data


def run_kfold_experiment(
    models: Dict[str, Any],
    X: np.ndarray,
    y: np.ndarray,
    k: int = 10,
) -> Dict[str, Dict[str, float]]:
    """
    Tái hiện Thực nghiệm 2: Đánh giá K-Fold (K=10) Cross Validation.
    """
    kf = KFold(n_splits=k, shuffle=True, random_state=RANDOM_STATE)
    cv_results = {}

    # Chỉ đánh giá 5 mô hình cốt lõi của bài báo để tối ưu thời gian
    core_models = ["AdaBoost", "GradientBoosting", "DecisionTree", "ExtraTrees", "RandomForest"]

    for name in core_models:
        if name not in models:
            continue
        print(f"  [K-Fold] Chạy 10-Fold CV cho {name}...")
        base_model = models[name]
        accuracies = []
        train_times = []

        for train_idx, val_idx in kf.split(X):
            X_tr, X_val = X[train_idx], X[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]

            t0 = time.time()
            m = DecisionTreeClassifier(**MODEL_PARAMS["DecisionTree"]) if name == "DecisionTree" else \
                RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1) if name == "RandomForest" else \
                ExtraTreesClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1) if name == "ExtraTrees" else \
                AdaBoostClassifier(n_estimators=50, random_state=RANDOM_STATE) if name == "AdaBoost" else \
                GradientBoostingClassifier(n_estimators=100, random_state=RANDOM_STATE)
            m.fit(X_tr, y_tr)
            train_times.append(time.time() - t0)

            preds = m.predict(X_val)
            acc = float(np.mean(preds == y_val))
            accuracies.append(acc)

        cv_results[name] = {
            "mean_accuracy": round(float(np.mean(accuracies)), 4),
            "min_accuracy": round(float(np.min(accuracies)), 4),
            "max_accuracy": round(float(np.max(accuracies)), 4),
            "mean_training_time": round(float(np.mean(train_times)), 3),
        }

    return cv_results


def run_trees_tuning_experiment(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    trees_range: List[int] = None,
) -> Tuple[List[int], List[float], List[float]]:
    """
    Tái hiện Thực nghiệm 3: Khảo sát số cây n_estimators (10 đến 300).
    """
    if trees_range is None:
        trees_range = [10, 20, 30, 50, 75, 100, 150, 200, 250, 300]

    acc_list = []
    time_list = []

    print("  [Tuning] Khảo sát n_estimators của Random Forest...")
    for n_trees in trees_range:
        t0 = time.time()
        rf = RandomForestClassifier(n_estimators=n_trees, random_state=RANDOM_STATE, n_jobs=-1)
        rf.fit(X_train, y_train)
        elap = time.time() - t0

        acc = float(rf.score(X_test, y_test))
        acc_list.append(acc)
        time_list.append(elap)

    return trees_range, acc_list, time_list


def run_feature_reduction_experiment(
    rf_model: RandomForestClassifier,
    feature_names: List[str],
    X_train_df: pd.DataFrame,
    y_train: np.ndarray,
    X_test_df: pd.DataFrame,
    y_test: np.ndarray,
    top_k: int = 15,
) -> Dict[str, Any]:
    """
    Tái hiện Thực nghiệm 4: Giảm chiều từ 44 đặc trưng xuống Top-15 đặc trưng quan trọng nhất.
    """
    importances = rf_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    top_features = [feature_names[i] for i in sorted_idx[:top_k]]

    # Đo với toàn bộ đặc trưng ban đầu
    t0_full = time.time()
    rf_full = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)
    rf_full.fit(X_train_df[feature_names].values, y_train)
    time_full = time.time() - t0_full
    acc_full = float(rf_full.score(X_test_df[feature_names].values, y_test))

    # Đo với Top-15 đặc trưng
    t0_top = time.time()
    rf_top = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)
    rf_top.fit(X_train_df[top_features].values, y_train)
    time_top = time.time() - t0_top
    acc_top = float(rf_top.score(X_test_df[top_features].values, y_test))

    return {
        "full_features_count": len(feature_names),
        "full_accuracy": round(acc_full, 4),
        "full_training_time": round(time_full, 3),
        "reduced_features_count": top_k,
        "reduced_accuracy": round(acc_top, 4),
        "reduced_training_time": round(time_top, 3),
        "accuracy_drop": round(acc_full - acc_top, 4),
        "time_saved_percent": round((time_full - time_top) / time_full * 100, 2),
        "top_features_list": top_features,
    }
