# Kế Hoạch Thực Hiện Dự Án (Project Plan)

## Đề tài: Phân loại malware PE từ EMBER và kiểm tra drift theo thời gian
**Môn học**: An toàn và bảo mật hệ thống thông tin (Báo cáo giữa kì)  
**Sinh viên**: Trần Nguyễn Minh Khôi (MSSV: 1150080059)  
**Giảng viên hướng dẫn**: ThS. Phạm Trọng Huynh  

---

## 1. Mục tiêu và Câu hỏi nghiên cứu (Research Questions)
- **RQ1 (Tái hiện & Đối sánh)**: Các thuật toán Machine Learning (Random Forest, Extra Trees, LightGBM, Decision Tree) khi sử dụng các trường đặc trưng PE Header đạt hiệu năng phân loại như thế nào (Accuracy, Precision, Recall, F1, ROC-AUC, FPR)? Mức độ tương đồng và sai lệch so với bài báo gốc ra sao?
- **RQ2 (Kiểm tra trôi dạt theo thời gian - Temporal Drift)**: Khi chuyển từ phép chia ngẫu nhiên (Random Split) sang phân chia theo trục thời gian thực (Temporal Split - train trên các tháng quá khứ, test trên các tháng tương lai), hiệu năng của mô hình suy giảm như thế nào theo từng tháng? Những đặc trưng PE Header nào chịu ảnh hưởng drift nghiêm trọng nhất (đo lường qua chỉ số PSI và KS-statistic)?
- **RQ3 (Giảm thiểu Drift)**: Giải pháp huấn luyện lại định kỳ (Periodic Retraining / Sliding Window) có giúp phục hồi và ổn định độ nhạy của hệ thống phát hiện mã độc so với việc giữ nguyên mô hình tĩnh (Static Model) hay không?

---

## 2. Kế hoạch từng giai đoạn

### Giai đoạn 1: Tìm kiếm & Thu thập Dữ liệu từ Kaggle
- Khảo sát các dataset liên quan trên Kaggle: `EMBER`, `PE malware dataset`, `PE Header features`, `ClaMP`.
- Lập bảng so sánh 5 ứng viên tiềm năng vào `output/reports/dataset_candidates.md`.
- Tiêu chí lựa chọn: Phải có nhãn phân loại (0: benign, 1: malware), các đặc trưng cấu trúc PE Header, và **bắt buộc phải có nhãn thời gian (`appeared` / timestamp / month)** để phục vụ phân tích drift.
- Thực hiện tải dữ liệu tự động hoặc cung cấp hướng dẫn qua Kaggle API vào `input/data/raw/`.
- Tài liệu hóa nguồn gốc và giấy phép trong `input/data/DATA_SOURCE.md`.

### Giai đoạn 2: Phát triển Hệ thống Thực nghiệm Python
- **Cấu trúc module chuẩn**:
  - `src/config.py`: Thiết lập tham số, đường dẫn, seed, các nhóm đặc trưng PE Header.
  - `src/data_loader.py`: Tải dữ liệu, lọc bỏ nhãn không xác định (-1), tạo cột tháng/thời gian, phân tầng mẫu.
  - `src/features.py`: Trích chọn 44 đặc trưng PE header (theo bài báo) và tập mở rộng, chuẩn hóa dữ liệu.
  - `src/train.py`: Huấn luyện Random Forest, LightGBM, Extra Trees, Decision Tree, Logistic Regression.
  - `src/evaluate.py`: Đo đạc toàn diện Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, FPR ở ngưỡng thấp, Confusion Matrix.
  - `src/drift.py`: Tính toán Population Stability Index (PSI), Kolmogorov-Smirnov test (KS-test), đánh giá hiệu năng suy giảm theo từng tháng, mô phỏng chiến lược Sliding Window Retraining.
  - `src/utils.py`: Lưu trữ metrics (JSON, CSV), vẽ biểu đồ chất lượng cao (ROC curve, Confusion Matrix, Temporal Degradation, Feature Drift).
  - `run_all.py`: Điều phối chạy toàn bộ quy trình tự động từ dữ liệu thô đến xuất biểu đồ, bảng số liệu và slide.
  - `tests/`: Bộ kiểm thử tự động (Unit Tests) kiểm tra tính toàn vẹn của loader, temporal split, metrics, và hàm tính PSI.

### Giai đoạn 3: Xây dựng Slide Thuyết trình PowerPoint (10 trang)
- Biên soạn file `output/slides/presentation.pptx` gồm đúng 10 trang theo chuẩn yêu cầu.
- Tích hợp số liệu thực nghiệm chính xác 100% từ `output/metrics/`.
- Chèn trực tiếp các hình ảnh biểu đồ trực quan từ `output/figures/`.
- Bổ sung Speaker Notes chi tiết cho từng slide giúp việc thuyết trình mạch lạc, tự tin.

---

## 3. Các Giả Định Kỹ Thuật (Assumptions)
1. **Giả định về Nhãn dữ liệu**: Chỉ sử dụng các mẫu có nhãn nhị phân rõ ràng: `0` (Lành tính - Benign) và `1` (Mã độc - Malware). Bỏ qua nhãn `-1` (chưa gán nhãn trong EMBER gốc) để đảm bảo bài toán phân loại có giám sát chuẩn xác.
2. **Giả định về Lấy mẫu (Sampling)**: Tập dữ liệu EMBER đầy đủ có dung lượng rất lớn (~1 triệu mẫu, hàng chục GB). Để đảm bảo tính khả thi về RAM, CPU và thời gian chạy lặp lại trên máy tính cá nhân, dự án sẽ áp dụng phương pháp **lấy mẫu phân tầng theo thời gian và nhãn** (Stratified Temporal Sampling) với kích thước hợp lý (từ 20.000 đến 60.000 mẫu), giữ nguyên chính xác tỷ lệ phân bố malware/benign qua từng tháng.
3. **Giả định về Phân chia Thời gian (Temporal Split)**: 
   - Tập huấn luyện (Train set): Sử dụng dữ liệu của các tháng đầu (ví dụ: Tháng 1 đến Tháng 8 năm 2018).
   - Tập kiểm thử (Test set theo tháng): Sử dụng dữ liệu của các tháng tương lai (ví dụ: Tháng 9, 10, 11, 12 năm 2018) để đánh giá drift thực tế.
4. **Giả định về Đặc trưng PE Header**: Trích chọn các trường thông tin trong PE Header (General PE info, Section characteristics, Resource info, Optional Header) tương thích cao nhất với 44 trường được mô tả trong bài báo gốc của Nguyễn Kim Tuấn & Nguyễn Hoàng Hà.
5. **Độ lặp lại (Reproducibility)**: Cố định `random_state = 42` trên tất cả các thuật toán và thao tác lấy mẫu.
