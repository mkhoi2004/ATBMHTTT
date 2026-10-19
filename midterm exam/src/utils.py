"""
Mô-đun tiện ích: Trực quan hóa dữ liệu và biểu đồ khoa học chất lượng cao (300 DPI).
Tất cả biểu đồ được lưu tự động vào output/figures/ phục vụ chèn trực tiếp vào slide và báo cáo.
"""

from pathlib import Path
from typing import Dict, List, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from src.config import FIGURES_DIR

# Thiết lập style đồ họa
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Calibri"]
plt.rcParams["axes.unicode_minus"] = False


def plot_confusion_matrices(
    cm: np.ndarray,
    title: str = "Confusion Matrix - Random Forest (PE Header)",
    save_name: str = "confusion_matrix.png",
) -> Path:
    """
    Vẽ ma trận nhầm lẫn (Confusion Matrix).
    """
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Benign (0)", "Malware (1)"],
        yticklabels=["Benign (0)", "Malware (1)"],
        ax=ax,
        cbar=True,
    )
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Predicted Label", fontsize=10, fontweight="bold")
    ax.set_ylabel("True Label", fontsize=10, fontweight="bold")
    plt.tight_layout()

    out_path = FIGURES_DIR / save_name
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def plot_roc_curves(
    roc_data: Dict[str, Dict[str, Any]],
    title: str = "ROC Curves Comparison - PE Header Models",
    save_name: str = "roc_curves.png",
) -> Path:
    """
    Vẽ đường cong ROC đối sánh nhiều mô hình.
    """
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    for model_name, data in roc_data.items():
        fpr = data["fpr"]
        tpr = data["tpr"]
        auc = data["auc"]
        ax.plot(fpr, tpr, label=f"{model_name} (AUC = {auc:.4f})", lw=2)

    ax.plot([0, 1], [0, 1], "k--", lw=1.2, label="Random Guess (AUC = 0.5000)")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate (FPR)", fontsize=10, fontweight="bold")
    ax.set_ylabel("True Positive Rate (TPR / Recall)", fontsize=10, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="lower right", frameon=True, fontsize=9)
    plt.tight_layout()

    out_path = FIGURES_DIR / save_name
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def plot_feature_importance(
    importances: Dict[str, float],
    top_n: int = 15,
    title: str = "Top PE Header Feature Importances (Random Forest)",
    save_name: str = "feature_importance.png",
) -> Path:
    """
    Biểu đồ cột xếp hạng tầm quan trọng đặc trưng (Feature Importance).
    """
    sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:top_n]
    features = [x[0] for x in sorted_items][::-1]
    scores = [x[1] for x in sorted_items][::-1]

    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    bars = ax.barh(features, scores, color="#1f77b4", edgecolor="black", alpha=0.85)
    ax.set_xlabel("Relative Importance Score", fontsize=10, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    # Thêm giá trị số vào đầu mỗi cột
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.002, bar.get_y() + bar.get_height() / 2, f"{w:.4f}", va="center", fontsize=8)

    plt.tight_layout()
    out_path = FIGURES_DIR / save_name
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def plot_temporal_degradation(
    perf_df: pd.DataFrame,
    title: str = "Model Performance Degradation Over Time (Static Model)",
    save_name: str = "temporal_degradation.png",
) -> Path:
    """
    Vẽ đường suy giảm hiệu năng theo thời gian (AUC, F1, Recall, FPR).
    """
    fig, ax1 = plt.subplots(figsize=(8, 5), dpi=300)

    months = perf_df["month"].tolist()
    x = range(len(months))

    # Trục trái: AUC, F1, Recall
    l1 = ax1.plot(x, perf_df["roc_auc"], "b-o", label="ROC-AUC", lw=2.2)
    l2 = ax1.plot(x, perf_df["f1"], "g-s", label="F1-Score", lw=2)
    l3 = ax1.plot(x, perf_df["recall"], "m-^", label="Recall", lw=2)
    ax1.set_xlabel("Evaluation Month (Temporal Test Split)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Metric Score", fontsize=10, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(months)
    ax1.set_ylim([0.7, 1.02])

    # Trục phải: FPR (càng thấp càng tốt)
    ax2 = ax1.twinx()
    l4 = ax2.plot(x, perf_df["fpr"], "r--d", label="FPR (False Alarm)", lw=2)
    ax2.set_ylabel("False Positive Rate (FPR)", color="r", fontsize=10, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="r")

    # Gộp legend
    lines = l1 + l2 + l3 + l4
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="lower left", frameon=True, fontsize=9)

    ax1.set_title(title, fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()

    out_path = FIGURES_DIR / save_name
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def plot_retraining_comparison(
    compare_df: pd.DataFrame,
    title: str = "Mitigating Concept Drift: Static Model vs. Periodic Retraining",
    save_name: str = "retraining_comparison.png",
) -> Path:
    """
    Biểu đồ đối sánh hiệu năng giữa Mô hình tĩnh vs Huấn luyện lại (Sliding Window).
    """
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    months = compare_df["month"].tolist()
    x = np.arange(len(months))
    width = 0.35

    rects1 = ax.bar(x - width / 2, compare_df["static_auc"], width, label="Static Model (No Retrain)", color="#d95f02", alpha=0.85)
    rects2 = ax.bar(x + width / 2, compare_df["retrained_auc"], width, label="Retrained Model (Sliding Window)", color="#1b9e77", alpha=0.85)

    ax.set_ylabel("ROC-AUC Score", fontsize=10, fontweight="bold")
    ax.set_xlabel("Evaluation Month", fontsize=10, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.set_ylim([0.8, 1.02])
    ax.legend(loc="lower right", frameon=True, fontsize=9)

    # Ghi chú giá trị trên đầu cột
    for r in rects1:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width() / 2, h + 0.005, f"{h:.3f}", ha="center", fontsize=8)
    for r in rects2:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width() / 2, h + 0.005, f"{h:.3f}", ha="center", fontsize=8)

    plt.tight_layout()
    out_path = FIGURES_DIR / save_name
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def plot_psi_feature_drift(
    drift_df: pd.DataFrame,
    top_n: int = 12,
    title: str = "Feature Drift Detection (Population Stability Index - PSI)",
    save_name: str = "feature_drift_psi.png",
) -> Path:
    """
    Vẽ biểu đồ các đặc trưng bị trôi dạt (drift) mạnh nhất kèm đường ngưỡng PSI.
    """
    sub_df = drift_df.head(top_n).copy()
    sub_df = sub_df.sort_values(by="psi", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    colors = ["#2ca02c" if p < 0.1 else ("#ff7f0e" if p < 0.25 else "#d62728") for p in sub_df["psi"]]
    bars = ax.barh(sub_df["feature"], sub_df["psi"], color=colors, edgecolor="black", alpha=0.85)

    ax.axvline(x=0.1, color="orange", linestyle="--", lw=1.5, label="Moderate Drift Threshold (0.10)")
    ax.axvline(x=0.25, color="red", linestyle="--", lw=1.5, label="Significant Drift Threshold (0.25)")

    ax.set_xlabel("PSI Value", fontsize=10, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="lower right", frameon=True, fontsize=9)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.005, bar.get_y() + bar.get_height() / 2, f"{w:.3f}", va="center", fontsize=8)

    plt.tight_layout()
    out_path = FIGURES_DIR / save_name
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def plot_trees_tuning(
    trees_list: List[int],
    acc_list: List[float],
    time_list: List[float],
    title_acc: str = "Random Forest: Accuracy vs. Number of Trees",
    title_time: str = "Random Forest: Training Time vs. Number of Trees",
    save_name: str = "rf_trees_tuning.png",
) -> Path:
    """
    Tái hiện Thực nghiệm 3 của bài báo: Khảo sát số cây (n_estimators) từ 10 đến 300.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # Hình 1: Accuracy vs Trees
    ax1.plot(trees_list, acc_list, "b-o", lw=2, markersize=5)
    ax1.set_xlabel("Number of Trees (n_estimators)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Accuracy", fontsize=10, fontweight="bold")
    ax1.set_title(title_acc, fontsize=11, fontweight="bold", pad=10)
    ax1.axvline(x=100, color="red", linestyle="--", label="Optimal Threshold (n=100)")
    ax1.legend(loc="lower right", fontsize=8)

    # Hình 2: Training Time vs Trees
    ax2.plot(trees_list, time_list, "r-s", lw=2, markersize=5)
    ax2.set_xlabel("Number of Trees (n_estimators)", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Training Time (seconds)", fontsize=10, fontweight="bold")
    ax2.set_title(title_time, fontsize=11, fontweight="bold", pad=10)
    ax2.axvline(x=100, color="red", linestyle="--", label="Optimal Threshold (n=100)")
    ax2.legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    out_path = FIGURES_DIR / save_name
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path
