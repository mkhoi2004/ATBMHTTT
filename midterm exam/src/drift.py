"""
Mô-đun phân tích trôi dạt dữ liệu theo thời gian (Temporal Drift):
- Tính toán PSI (Population Stability Index)
- Kiểm định Kolmogorov-Smirnov (KS-test)
- Đo lường Label Drift (tỉ lệ malware theo tháng)
- Đánh giá suy giảm hiệu năng mô hình tĩnh theo thời gian
- Thực nghiệm chiến lược Retraining (Sliding Window) để khắc phục drift
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import clone

from src.evaluate import calculate_metrics


def calculate_psi(
    expected: np.ndarray,
    actual: np.ndarray,
    num_bins: int = 10,
    epsilon: float = 1e-4,
) -> float:
    """
    Tính chỉ số Population Stability Index (PSI) cho 1 đặc trưng.
    expected: Dữ liệu phân bố gốc (ví dụ: tập Train)
    actual: Dữ liệu phân bố hiện tại (ví dụ: tập Test tháng t)
    """
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)

    # Loại bỏ NaN / Inf
    expected = expected[np.isfinite(expected)]
    actual = actual[np.isfinite(actual)]

    if len(expected) == 0 or len(actual) == 0:
        return 0.0

    # Nếu đặc trưng là hằng số
    if np.all(expected == expected[0]) and np.all(actual == actual[0]):
        return 0.0

    # Chia bins dựa trên quantiles của tập expected
    quantiles = np.linspace(0, 100, num_bins + 1)
    bin_edges = np.percentile(expected, quantiles)
    bin_edges = np.unique(bin_edges)  # Loại bỏ trùng

    if len(bin_edges) < 2:
        return 0.0

    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    # Đếm số lượng trong từng bin
    exp_counts, _ = np.histogram(expected, bins=bin_edges)
    act_counts, _ = np.histogram(actual, bins=bin_edges)

    # Chuyển sang tỷ lệ %
    exp_pct = exp_counts / len(expected)
    act_pct = act_counts / len(actual)

    # Thêm epsilon tránh log(0) và chia cho 0
    exp_pct = np.where(exp_pct == 0, epsilon, exp_pct)
    act_pct = np.where(act_pct == 0, epsilon, act_pct)

    # Chuẩn hóa lại tổng = 1
    exp_pct = exp_pct / np.sum(exp_pct)
    act_pct = act_pct / np.sum(act_pct)

    # Công thức PSI: sum((actual - expected) * ln(actual / expected))
    psi_value = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return float(psi_value)


def calculate_ks_test(
    reference: np.ndarray,
    current: np.ndarray,
) -> Tuple[float, float]:
    """
    Thực hiện kiểm định 2 mẫu Kolmogorov-Smirnov.
    Trả về: (ks_statistic, p_value)
    """
    reference = np.asarray(reference, dtype=float)
    current = np.asarray(current, dtype=float)

    reference = reference[np.isfinite(reference)]
    current = current[np.isfinite(current)]

    if len(reference) == 0 or len(current) == 0:
        return 0.0, 1.0

    res = stats.ks_2samp(reference, current)
    return float(res.statistic), float(res.pvalue)


def compute_feature_drift_report(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: List[str],
) -> pd.DataFrame:
    """
    Tính PSI và KS-test cho toàn bộ danh sách đặc trưng giữa Train và Test.
    """
    results = []
    for col in feature_cols:
        if col not in train_df.columns or col not in test_df.columns:
            continue
        train_vals = train_df[col].values
        test_vals = test_df[col].values

        psi = calculate_psi(train_vals, test_vals)
        ks_stat, ks_pval = calculate_ks_test(train_vals, test_vals)

        if psi < 0.1:
            status = "Stable (Không drift)"
        elif psi < 0.25:
            status = "Moderate (Drift vừa)"
        else:
            status = "Significant (Drift nghiêm trọng)"

        results.append({
            "feature": col,
            "psi": round(psi, 4),
            "ks_statistic": round(ks_stat, 4),
            "ks_pvalue": round(ks_pval, 6),
            "status": status,
        })

    df = pd.DataFrame(results)
    return df.sort_values(by="psi", ascending=False).reset_index(drop=True)


def compute_label_drift(df: pd.DataFrame, time_col: str = "appeared", label_col: str = "label") -> pd.DataFrame:
    """
    Đo lường biến thiên tỉ lệ mã độc qua từng tháng.
    """
    grouped = df.groupby(time_col)[label_col].agg(["count", "sum"]).reset_index()
    grouped.columns = [time_col, "total_samples", "malware_samples"]
    grouped["malware_ratio"] = grouped["malware_samples"] / grouped["total_samples"]
    grouped["benign_samples"] = grouped["total_samples"] - grouped["malware_samples"]
    return grouped


def evaluate_temporal_performance(
    model,
    X_dict: Dict[str, np.ndarray],
    y_dict: Dict[str, np.ndarray],
    months: List[str],
) -> pd.DataFrame:
    """
    Đánh giá hiệu năng của mô hình cố định trên từng tháng riêng biệt.
    """
    records = []
    for m in months:
        X_m = X_dict[m]
        y_m = y_dict[m]
        y_prob = model.predict_proba(X_m)[:, 1] if hasattr(model, "predict_proba") else None
        y_pred = model.predict(X_m)

        metrics = calculate_metrics(y_m, y_pred, y_prob)
        metrics["month"] = m
        metrics["samples"] = len(y_m)
        records.append(metrics)

    df = pd.DataFrame(records)
    # Đưa cột month lên đầu
    cols = ["month", "samples", "roc_auc", "f1", "recall", "precision", "accuracy", "fpr", "tpr_at_1pct_fpr"]
    return df[[c for c in cols if c in df.columns]]


def evaluate_sliding_window_retraining(
    base_model,
    full_df: pd.DataFrame,
    feature_cols: List[str],
    train_months: List[str],
    test_months: List[str],
    window_size: int = 4,
) -> pd.DataFrame:
    """
    Mô phỏng chiến lược Huấn luyện lại định kỳ (Sliding Window):
    Với mỗi tháng kiểm thử t:
    - Mô hình tĩnh: Giữ nguyên mô hình chỉ train trên train_months.
    - Mô hình Retrained: Huấn luyện lại mô hình trên cửa sổ `window_size` tháng gần nhất trước t.
    """
    all_months = train_months + test_months
    results = []

    # 1. Huấn luyện mô hình tĩnh ban đầu trên train_months
    train_mask = full_df["appeared"].isin(train_months)
    X_train_static = full_df.loc[train_mask, feature_cols].fillna(0).values
    y_train_static = full_df.loc[train_mask, "label"].values

    static_model = clone(base_model)
    static_model.fit(X_train_static, y_train_static)

    for i, test_m in enumerate(test_months):
        test_mask = full_df["appeared"] == test_m
        X_test = full_df.loc[test_mask, feature_cols].fillna(0).values
        y_test = full_df.loc[test_mask, "label"].values

        # Đánh giá Static Model
        p_static = static_model.predict_proba(X_test)[:, 1]
        m_static = calculate_metrics(y_test, None, p_static)

        # 2. Huấn luyện Retrained Model với Sliding Window (window_size tháng trước test_m)
        curr_idx = all_months.index(test_m)
        window_train_months = all_months[max(0, curr_idx - window_size) : curr_idx]
        retrain_mask = full_df["appeared"].isin(window_train_months)
        X_retrain = full_df.loc[retrain_mask, feature_cols].fillna(0).values
        y_retrain = full_df.loc[retrain_mask, "label"].values

        retrained_model = clone(base_model)
        retrained_model.fit(X_retrain, y_retrain)
        p_retrain = retrained_model.predict_proba(X_test)[:, 1]
        m_retrain = calculate_metrics(y_test, None, p_retrain)

        results.append({
            "month": test_m,
            "static_auc": m_static["roc_auc"],
            "retrained_auc": m_retrain["roc_auc"],
            "auc_delta": m_retrain["roc_auc"] - m_static["roc_auc"],
            "static_f1": m_static["f1"],
            "retrained_f1": m_retrain["f1"],
            "f1_delta": m_retrain["f1"] - m_static["f1"],
            "static_fpr": m_static["fpr"],
            "retrained_fpr": m_retrain["fpr"],
            "static_recall": m_static["recall"],
            "retrained_recall": m_retrain["recall"],
        })

    return pd.DataFrame(results)
