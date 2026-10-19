"""
Cấu hình trung tâm cho dự án Phân loại Malware PE từ EMBER và Kiểm tra Drift theo thời gian.
Tác giả: Trần Nguyễn Minh Khôi (MSSV: 1150080059)
"""

import os
from pathlib import Path

# Thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parent.parent

# Các đường dẫn dữ liệu
INPUT_DIR = BASE_DIR / "input"
DATA_DIR = INPUT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PAPER_DIR = INPUT_DIR / "paper"

OUTPUT_DIR = BASE_DIR / "output"
PROCESSED_DATA_DIR = OUTPUT_DIR / "data" / "processed"
MODELS_DIR = OUTPUT_DIR / "models"
METRICS_DIR = OUTPUT_DIR / "metrics"
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORTS_DIR = OUTPUT_DIR / "reports"
SLIDES_DIR = OUTPUT_DIR / "slides"

# Đảm bảo các thư mục luôn tồn tại
for path in [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    MODELS_DIR,
    METRICS_DIR,
    FIGURES_DIR,
    REPORTS_DIR,
    SLIDES_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)

# Cố định Seed ngẫu nhiên để tái lặp kết quả
RANDOM_STATE = 42

# Cấu hình lấy mẫu dữ liệu phân tầng (Stratified Sampling)
SAMPLES_PER_MONTH = 4000  # Lấy 4.000 mẫu/tháng cân bằng, tổng 48.000 mẫu cho cả năm 2018
TOTAL_TARGET_SAMPLES = 48000

# Trục thời gian EMBER 2018
ALL_MONTHS = [
    "2018-01", "2018-02", "2018-03", "2018-04",
    "2018-05", "2018-06", "2018-07", "2018-08",
    "2018-09", "2018-10", "2018-11", "2018-12",
]

# Phân chia theo thời gian (Temporal Split)
TRAIN_MONTHS = [
    "2018-01", "2018-02", "2018-03", "2018-04",
    "2018-05", "2018-06", "2018-07", "2018-08",
]  # Huấn luyện trên 8 tháng đầu
TEST_MONTHS = ["2018-09", "2018-10", "2018-11", "2018-12"]  # Kiểm thử drift trên 4 tháng sau

# Danh sách 44 đặc trưng PE Header cốt lõi (theo bài báo của Nguyễn Kim Tuấn & Nguyễn Hoàng Hà)
HEADER_FEATURES = [
    # General / Metadata
    "size",
    "vsize",
    "has_debug",
    "exports_nb",
    "imports_nb",
    "has_relocations",
    "has_resources",
    "has_signature",
    "has_tls",
    "symbols_nb",
    # COFF Header
    "timestamp",
    "machine",
    "characteristics",
    # Optional Header
    "subsystem",
    "dll_characteristics",
    "magic",
    "major_image_version",
    "minor_image_version",
    "major_linker_version",
    "minor_linker_version",
    "major_operating_system_version",
    "minor_operating_system_version",
    "major_subsystem_version",
    "minor_subsystem_version",
    "sizeof_code",
    "sizeof_headers",
    "sizeof_heap_commit",
    "sizeof_image",
    "sizeof_initialized_data",
    "sizeof_uninitialized_data",
    "sizeof_stack_commit",
    "sizeof_stack_reserve",
    "imagebase",
    "section_alignment",
    "file_alignment",
    "checksum",
    # Section statistics
    "sections_count",
    "sections_mean_size",
    "sections_max_size",
    "sections_min_size",
    "sections_mean_entropy",
    "sections_max_entropy",
    "sections_min_entropy",
    "sections_mean_vsize",
]

# Siêu tham số các mô hình học máy
MODEL_PARAMS = {
    "LogisticRegression": {
        "max_iter": 1000,
        "random_state": RANDOM_STATE,
        "C": 1.0,
    },
    "DecisionTree": {
        "max_depth": 15,
        "random_state": RANDOM_STATE,
    },
    "AdaBoost": {
        "n_estimators": 50,
        "random_state": RANDOM_STATE,
    },
    "RandomForest": {
        "n_estimators": 100,  # Bão hòa tối ưu theo Thực nghiệm 3 của bài báo
        "max_depth": None,
        "random_state": RANDOM_STATE,
        "n_jobs": -1,
    },
    "ExtraTrees": {
        "n_estimators": 100,
        "random_state": RANDOM_STATE,
        "n_jobs": -1,
    },
    "GradientBoosting": {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "random_state": RANDOM_STATE,
    },
    "LightGBM": {
        "n_estimators": 100,
        "learning_rate": 0.05,
        "random_state": RANDOM_STATE,
        "n_jobs": -1,
        "verbose": -1,
    },
}

# Ngưỡng đánh giá drift (Population Stability Index - PSI)
PSI_THRESHOLDS = {
    "stable": 0.1,       # Không có drift đáng kể (< 0.1)
    "moderate": 0.25,    # Drift vừa phải (0.1 - 0.25)
    "significant": 0.25  # Drift nghiêm trọng (> 0.25)
}
