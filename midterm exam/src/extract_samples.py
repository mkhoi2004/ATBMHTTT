"""
Script trích xuất mẫu phân tầng theo thời gian từ tệp nén EMBER.
Đọc luồng bz2 tuần tự và lưu trực tiếp vào output/data/processed/ember_sampled.csv.
"""

import bz2
import json
import time
import sys
from pathlib import Path

# Thêm thư mục gốc dự án vào PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

from src.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    ALL_MONTHS,
    SAMPLES_PER_MONTH,
)
from src.features import parse_ember_record_to_features, PE_HEADER_FEATURES


def extract_stratified_dataset(
    archive_path: Path,
    output_csv: Path,
    target_per_class: int = 2000,
) -> pd.DataFrame:
    print(f"[Trích xuất] Đang mở luồng dữ liệu: {archive_path.name}")
    start_time = time.time()

    monthly_counts = {m: {0: 0, 1: 0} for m in ALL_MONTHS}
    records = []

    decompressor = bz2.BZ2Decompressor()
    chunk_size = 512 * 1024
    unconsumed = b""
    total_bytes_read = 0
    total_parsed = 0

    with open(archive_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            total_bytes_read += len(chunk)
            try:
                decompressed = decompressor.decompress(chunk)
            except Exception:
                continue

            unconsumed += decompressed
            lines = unconsumed.split(b"\n")
            unconsumed = lines[-1]

            for line in lines[:-1]:
                # Tìm bản ghi JSON
                line_str = line.strip()
                if not line_str or not line_str.startswith(b"{"):
                    continue

                try:
                    obj = json.loads(line_str.decode("utf-8", errors="ignore"))
                except Exception:
                    continue

                total_parsed += 1
                label = int(obj.get("label", -1))
                appeared = str(obj.get("appeared", ""))

                if appeared in monthly_counts and label in (0, 1):
                    if monthly_counts[appeared][label] < target_per_class:
                        parsed = parse_ember_record_to_features(obj)
                        records.append(parsed)
                        monthly_counts[appeared][label] += 1

            # Kiểm tra tiến độ mỗi 20MB đọc vào
            if total_bytes_read % (20 * 1024 * 1024) < chunk_size:
                collected_total = sum(
                    monthly_counts[m][0] + monthly_counts[m][1] for m in ALL_MONTHS
                )
                print(
                    f"  -> Đã đọc {total_bytes_read // (1024*1024)} MB | Thu thập: {collected_total:,} mẫu..."
                )

            # Kiểm tra xem đã đủ mẫu tất cả các tháng chưa
            if all(
                monthly_counts[m][0] >= target_per_class
                and monthly_counts[m][1] >= target_per_class
                for m in ALL_MONTHS
            ):
                print("[Trích xuất] Đã đạt đủ chỉ tiêu mẫu cho toàn bộ 12 tháng!")
                break

    df = pd.DataFrame(records)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    elapsed = round(time.time() - start_time, 2)
    print(f"[Trích xuất] Hoàn thành! Thu được {len(df):,} mẫu trong {elapsed} giây.")
    print(f"[Trích xuất] Lưu tệp tại: {output_csv}")
    return df


if __name__ == "__main__":
    raw_archive = RAW_DATA_DIR / "ember_dataset_2018_2.tar.bz2"
    out_file = PROCESSED_DATA_DIR / "ember_sampled.csv"
    extract_stratified_dataset(raw_archive, out_file)
