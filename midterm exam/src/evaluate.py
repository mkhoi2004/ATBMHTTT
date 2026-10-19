"""
Mô-đun đánh giá toàn diện các chỉ số hiệu năng an toàn thông tin:
Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, FPR, Confusion Matrix.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
)


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray = None,
    threshold: float = 0.5,
) -> Dict[str, float]:
    """
    Tính toán đầy đủ các chỉ số hiệu năng chuẩn an ninh mạng.
    """
    y_true = np.asarray(y_true).astype(int)
    if y_prob is not None:
        y_prob = np.asarray(y_prob)
        y_pred = (y_prob >= threshold).astype(int)
    else:
        y_pred = np.asarray(y_pred).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    accuracy = float(accuracy_score(y_true, y_pred))
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    metrics = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "fnr": fnr,
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
    }

    if y_prob is not None:
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
        except Exception:
            metrics["roc_auc"] = 0.5
        try:
            metrics["pr_auc"] = float(average_precision_score(y_true, y_prob))
        except Exception:
            metrics["pr_auc"] = float(np.mean(y_true))
            
        # TPR tại ngưỡng FPR thấp (1% và 0.1% - đặc thù bài toán an ninh mạng)
        fprs, tprs, thresholds = roc_curve(y_true, y_prob)
        idx_1pct = np.where(fprs <= 0.01)[0]
        metrics["tpr_at_1pct_fpr"] = float(tprs[idx_1pct[-1]]) if len(idx_1pct) > 0 else 0.0
    else:
        metrics["roc_auc"] = None
        metrics["pr_auc"] = None
        metrics["tpr_at_1pct_fpr"] = None

    return metrics


def save_metrics_to_files(
    metrics_dict: Dict[str, Any],
    json_path: Path,
    csv_path: Path = None,
) -> None:
    """
    Lưu kết quả đo lường vào file JSON và CSV để đảm bảo tính minh bạch, không bịa số liệu.
    """
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_dict, f, indent=4, ensure_ascii=False)

    if csv_path:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(metrics_dict, dict):
            # Nếu là dict lồng nhau (mô hình -> metrics)
            if all(isinstance(v, dict) for v in metrics_dict.values()):
                df = pd.DataFrame.from_dict(metrics_dict, orient="index")
            else:
                df = pd.DataFrame([metrics_dict])
            df.to_csv(csv_path, index=True)
