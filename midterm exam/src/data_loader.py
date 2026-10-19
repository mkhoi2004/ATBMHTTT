"""
Mô-đun tải, xử lý và phân tách dữ liệu EMBER:
- Tải từ archive tar.bz2 hoặc file jsonl
- Lọc nhãn unlabeled (-1)
- Lấy mẫu phân tầng theo Tháng và Nhãn (Stratified Temporal Sampling)
- Phân chia tập dữ liệu ngẫu nhiên (Random Split 80/20) và theo thời gian (Temporal Split)
"""

import bz2
import json
import tarfile
from pathlib import Path
from typing import Tuple, Dict, List
import numpy as np
import pandas as pd
from tqdm import tqdm

from src.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    RANDOM_STATE,
    SAMPLES_PER_MONTH,
    ALL_MONTHS,
    TRAIN_MONTHS,
    TEST_MONTHS,
)
from src.features import parse_ember_record_to_features, PE_HEADER_FEATURES


def process_raw_ember_stream(
    archive_path: Path,
    output_csv: Path,
    samples_per_month: int = SAMPLES_PER_MONTH,
) -> pd.DataFrame:
    """
    Đọc giải nén tar.bz2 và lấy mẫu phân tầng theo tháng và nhãn.
    Lọc bỏ hoàn toàn nhãn unlabeled (-1).
    """
    print(f"[DataLoader] Đang xử lý tệp nén: {archive_path.name}...")
    monthly_counts = {m: {0: 0, 1: 0} for m in ALL_MONTHS}
    target_per_class = samples_per_month // 2

    records = []

    with tarfile.open(archive_path, mode="r:bz2") as tar:
        for member in tar:
            if not member.isfile() or not member.name.endswith(".jsonl"):
                continue
            print(f"  -> Đang đọc thành phần: {member.name} ({member.size // 1024 // 1024} MB)...")
            f = tar.extractfile(member)
            if f is None:
                continue

            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line.decode("utf-8", errors="ignore"))
                except Exception:
                    continue

                label = int(obj.get("label", -1))
                appeared = obj.get("appeared", "")

                # Chỉ giữ các tháng năm 2018 và nhãn 0 hoặc 1
                if appeared not in monthly_counts or label not in (0, 1):
                    continue

                if monthly_counts[appeared][label] < target_per_class:
                    parsed_row = parse_ember_record_to_features(obj)
                    records.append(parsed_row)
                    monthly_counts[appeared][label] += 1

                # Kiểm tra xem tất cả các tháng đã đủ mẫu chưa
                all_done = all(
                    monthly_counts[m][0] >= target_per_class and monthly_counts[m][1] >= target_per_class
                    for m in ALL_MONTHS
                )
                if all_done:
                    print("  [DataLoader] Đã thu thập đủ số lượng mẫu phân tầng cho tất cả 12 tháng!")
                    break
            if all_done:
                break

    df = pd.DataFrame(records)
    print(f"[DataLoader] Hoàn tất trích xuất {len(df)} mẫu. Lưu vào {output_csv.name}...")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    return df


def load_dataset(force_reprocess: bool = False) -> pd.DataFrame:
    """
    Tải bộ dữ liệu đã được lấy mẫu phân tầng và làm sạch.
    Nếu chưa có, tự động xử lý từ raw data.
    """
    processed_csv = PROCESSED_DATA_DIR / "ember_sampled.csv"

    if processed_csv.exists() and not force_reprocess:
        print(f"[DataLoader] Đang nạp dữ liệu đã xử lý từ: {processed_csv.name}")
        df = pd.read_csv(processed_csv)
        return df

    # Tìm tệp nén trong raw data
    raw_archives = list(RAW_DATA_DIR.glob("*.tar.bz2"))
    raw_jsonls = list(RAW_DATA_DIR.glob("*.jsonl"))

    if raw_archives:
        return process_raw_ember_stream(raw_archives[0], processed_csv)
    elif raw_jsonls:
        # Nếu có file jsonl thô
        return process_raw_jsonl_files(raw_jsonls, processed_csv)
    else:
        raise FileNotFoundError(
            f"Không tìm thấy dữ liệu thô (.tar.bz2 hoặc .jsonl) trong thư mục: {RAW_DATA_DIR}"
        )


def process_raw_jsonl_files(
    jsonl_files: List[Path],
    output_csv: Path,
    samples_per_month: int = SAMPLES_PER_MONTH,
) -> pd.DataFrame:
    """
    Xử lý trực tiếp từ danh sách các file jsonl nếu người dùng đã giải nén trước.
    """
    print(f"[DataLoader] Đang xử lý {len(jsonl_files)} tệp jsonl...")
    monthly_counts = {m: {0: 0, 1: 0} for m in ALL_MONTHS}
    target_per_class = samples_per_month // 2
    records = []

    for jf in jsonl_files:
        with open(jf, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue

                label = int(obj.get("label", -1))
                appeared = obj.get("appeared", "")

                if appeared not in monthly_counts or label not in (0, 1):
                    continue

                if monthly_counts[appeared][label] < target_per_class:
                    parsed_row = parse_ember_record_to_features(obj)
                    records.append(parsed_row)
                    monthly_counts[appeared][label] += 1

    df = pd.DataFrame(records)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    return df


def get_random_split(
    df: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = RANDOM_STATE,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Tái hiện Thực nghiệm 1: Phân chia 80% Train / 20% Test ngẫu nhiên (có phân tầng nhãn).
    """
    from sklearn.model_selection import train_test_split
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df["label"],
    )
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def get_temporal_split(
    df: pd.DataFrame,
    train_months: List[str] = TRAIN_MONTHS,
    test_months: List[str] = TEST_MONTHS,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Phần B: Phân chia theo thời gian (Temporal Split)
    Train: Tháng 01 đến Tháng 08 năm 2018
    Test: Tháng 09 đến Tháng 12 năm 2018
    """
    train_df = df[df["appeared"].isin(train_months)].reset_index(drop=True)
    test_df = df[df["appeared"].isin(test_months)].reset_index(drop=True)
    return train_df, test_df


def get_monthly_test_subsets(
    test_df: pd.DataFrame,
    months: List[str] = TEST_MONTHS,
) -> Dict[str, pd.DataFrame]:
    """
    Chia nhỏ tập Test thành từng tháng riêng lẻ phục vụ đo lường drift.
    """
    subsets = {}
    for m in months:
        sub = test_df[test_df["appeared"] == m].reset_index(drop=True)
        if len(sub) > 0:
            subsets[m] = sub
    return subsets
