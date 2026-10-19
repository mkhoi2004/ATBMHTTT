# Phân Loại Malware PE Từ EMBER và Kiểm Tra Drift Theo Thời Gian

**Báo cáo giữa kì môn An toàn và bảo mật hệ thống thông tin**  
- **Trường**: Đại học Tài nguyên và Môi trường TP.HCM  
- **Khoa**: Công nghệ thông tin  
- **Lớp**: 11_DH_CNPM1  
- **Sinh viên thực hiện**: Trần Nguyễn Minh Khôi  
- **Mã số sinh viên**: 1150080059  
- **Giảng viên hướng dẫn**: ThS. Phạm Trọng Huynh  

---

## 1. Giới thiệu Đề tài
Dự án tập trung vào hai mục tiêu nghiên cứu cốt lõi:
1. **Tái hiện thực nghiệm (Phần A)**: Dựa trên bài báo khoa học *"Phát hiện malware dựa trên header của tập tin PE sử dụng Machine learning"* (Nguyễn Kim Tuấn, Nguyễn Hoàng Hà). Đánh giá các thuật toán học máy (Random Forest, Extra Trees, Decision Tree, AdaBoost, Gradient Boosting / LightGBM) chỉ dựa trên các trường thông tin trong PE Header.
2. **Kiểm tra trôi dạt dữ liệu theo thời gian (Phần B - Concept & Data Drift)**: Mở rộng giải quyết khoảng trống nghiên cứu lớn nhất của bài báo bằng cách sử dụng bộ dữ liệu chuẩn **EMBER 2018** có gắn mốc thời gian xuất hiện (`appeared`). Thực hiện **Temporal Split** (Train trên các tháng đầu, Test trên các tháng tương lai), đo lường mức độ suy giảm hiệu năng, tính toán chỉ số **PSI (Population Stability Index)**, kiểm định **KS-test**, và đánh giá hiệu quả của chiến lược huấn luyện lại định kỳ (**Periodic Retraining / Sliding Window**).

---

## 2. Cấu trúc thư mục dự án

```
project/
├── input/
│   ├── paper/              # File PDF báo cáo tham khảo gốc
│   └── data/
│       ├── raw/            # Dữ liệu gốc EMBER (tar.bz2 / jsonl)
│       └── DATA_SOURCE.md  # Nguồn gốc dữ liệu, ngày tải, giấy phép
├── src/
│   ├── config.py           # Thiết lập đường dẫn, seed, siêu tham số
│   ├── data_loader.py      # Tải dữ liệu, lọc nhãn, lấy mẫu phân tầng
│   ├── features.py         # Trích xuất 44 đặc trưng PE Header, pipeline tiền xử lý
│   ├── train.py            # Huấn luyện mô hình (single split, 10-fold, trees tuning, feature reduction)
│   ├── evaluate.py         # Đo lường Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, FPR
│   ├── drift.py            # Tính PSI, KS-test, Label drift, Temporal degradation, Retraining
│   └── utils.py            # Trực quan hóa và xuất biểu đồ khoa học 300 DPI
├── tests/                  # Bộ kiểm thử tự động (Unit Tests) cho loader, split, metric, PSI
├── output/
│   ├── data/processed/     # Dữ liệu đã làm sạch và lấy mẫu phân tầng
│   ├── models/             # Artifacts mô hình đã huấn luyện (.joblib)
│   ├── metrics/            # File số liệu định dạng .json và .csv
│   ├── figures/            # Toàn bộ biểu đồ khoa học (.png 300 DPI)
│   ├── reports/            # Các báo cáo: paper_summary.md, plan.md, dataset_candidates.md, feature_mapping.md, data_audit.md, reproduction_comparison.md
│   └── slides/             # File trình chiếu PowerPoint 10 trang (presentation.pptx)
├── requirements.txt        # Danh sách thư viện và phiên bản
├── README.md               # Hướng dẫn chi tiết cài đặt và thực thi
└── run_all.py              # Điều phối chạy toàn bộ pipeline bằng 1 lệnh duy nhất
```

---

## 3. Cài đặt môi trường

Yêu cầu môi trường Python 3.10 trở lên. Cài đặt các gói phụ thuộc:

```bash
pip install -r requirements.txt
```

---

## 4. Chạy toàn bộ Pipeline bằng một lệnh duy nhất

Chỉ cần chạy lệnh sau từ thư mục gốc của dự án:

```bash
python run_all.py
```

Lệnh trên sẽ tự động thực hiện tuần tự:
1. Nạp và xử lý dữ liệu phân tầng EMBER 2018 (48.000 mẫu đại diện phủ 12 tháng).
2. Sinh báo cáo kiểm tra toàn vẹn dữ liệu `output/reports/data_audit.md`.
3. Huấn luyện 5 mô hình bài báo + LightGBM + Baseline, tính toán các metrics (Accuracy, ROC-AUC, PR-AUC, F1, FPR).
4. Chạy 10-Fold Cross Validation và khảo sát số lượng cây ($n_{estimators} = 10 \dots 300$).
5. Thực hiện thực nghiệm giảm chiều đặc trưng (Top-15 features) và đo mức độ tiết kiệm thời gian train.
6. Đánh giá Temporal Split, đo lường Feature Drift qua PSI và KS-test, vẽ đường suy giảm hiệu năng theo tháng.
7. Mô phỏng chiến lược Huấn luyện lại theo cửa sổ trượt (Sliding Window Retraining).
8. Xuất toàn bộ biểu đồ khoa học chất lượng cao 300 DPI vào `output/figures/`.
9. Tự động biên soạn bộ Slide PowerPoint 10 trang kèm Speaker Notes chi tiết tại `output/slides/presentation.pptx`.

---

## 5. Chạy kiểm thử tự động (Unit Tests)

```bash
python -m unittest discover tests
```

---

## 6. Tóm tắt kết quả chính

- **Hiệu năng PE Header**: Khẳng định kết luận của bài báo gốc, thuật toán **Random Forest** (100 cây) đạt hiệu năng cao nhất với ROC-AUC > 0.98, F1 > 0.93, và tỷ lệ báo nhầm (FPR) thấp (< 6%).
- **Hiện tượng Drift theo thời gian**: Khi chuyển sang kiểm thử trên các tháng tương lai (Temporal Split), hiệu năng mô hình tĩnh suy giảm qua các tháng. Các đặc trưng bị trôi dạt mạnh nhất là kích thước vùng code (`sizeof_code`), cờ bảo mật (`dll_characteristics`), và entropy phân vùng (`sections_mean_entropy`).
- **Khắc phục Drift bằng Retraining**: Chiến lược huấn luyện lại theo cửa sổ trượt (Sliding Window) giúp phục hồi đáng kể ROC-AUC và giảm thiểu cảnh báo sai (FPR) so với việc giữ nguyên mô hình tĩnh.
