# Thông Tin Nguồn Dữ Liệu (Data Source)

- **Tên bộ dữ liệu**: EMBER 2018 (Elastic Malware Benchmark for Empowering Researchers) - V2 Features
- **Nguồn chính thức**: Elastic Security Benchmark ([ember.elastic.co](https://ember.elastic.co/)) / Mirrored on Kaggle ([dhoogla/ember-2018-v2-features](https://www.kaggle.com/datasets/dhoogla/ember-2018-v2-features))
- **Tệp lưu trữ gốc**: `input/data/raw/ember_dataset_2018_2.tar.bz2`
- **Kích thước file gốc**: 1.696.539.273 bytes (~1.58 GB)
- **SHA-256 Checksum**: `b6052eb8d350a49a8d5a5396fbe7d16cf42848b86ff969b77464434cf2997812`
- **Ngày tải về**: 18/10/2026
- **Giấy phép (License)**: Creative Commons Attribution 4.0 International (CC BY 4.0) / Elastic License
- **Đặc điểm cấu trúc**:
  - Chứa đầy đủ các trường đặc trưng tĩnh trích xuất từ phần PE Header của các file thực thi Windows PE bằng thư viện LIEF (`header.coff`, `header.optional`, `section`, `general`, `datadirectories`).
  - Có nhãn phân lớp rõ ràng: `0` (Lành tính - Benign) và `1` (Mã độc - Malware), các mẫu `-1` (unlabeled) được lọc bỏ.
  - Có cột mốc thời gian xuất hiện (`appeared` định dạng `YYYY-MM` phủ từ `2018-01` đến `2018-12`) phục vụ trực tiếp cho việc phân tích trôi dạt dữ liệu theo thời gian (Concept Drift / Data Drift).
- **Quy trình lấy mẫu**:
  - Dữ liệu gốc 1.000.000 mẫu được lấy mẫu phân tầng theo thời gian (Stratified Temporal Sampling) theo từng tháng (từ tháng 01/2018 đến tháng 12/2018, 4.000 mẫu/tháng cân bằng 2.000 benign và 2.000 malware, tổng 48.000 mẫu) nhằm đảm bảo phản ánh chân thực phân bố nhãn và sự biến đổi đặc trưng theo thời gian thực mà vẫn tối ưu tài nguyên tính toán (RAM < 2GB).
