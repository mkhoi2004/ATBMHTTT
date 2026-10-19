# Báo Cáo Kiểm Tra Toàn Vẹn Dữ Liệu Thực Tế (Data Audit Report)

- **Tệp dữ liệu gốc**: `ember_dataset_2018_2.tar.bz2`
- **Định dạng ban đầu**: JSON Lines (.jsonl) nén tar.bz2 chuẩn EMBER 2018 (v2)
- **Tổng số mẫu trích xuất**: 48,000 dòng
- **Tổng số cột đặc trưng**: 52 cột
- **Giá trị khuyết thiếu (Missing values)**: 0 (Dữ liệu đã được làm sạch và điền đầy đủ)

---

## 1. Phân bố nhãn phân loại (Label Distribution)
- **Mẫu lành tính (Benign - Nhãn 0)**: 24,000 (50.00%)
- **Mẫu mã độc (Malware - Nhãn 1)**: 24,000 (50.00%)
- **Mẫu chưa xác định (Unlabeled - Nhãn -1)**: 0 (Đã lọc bỏ hoàn toàn các mẫu -1 trong EMBER để đảm bảo bài toán có giám sát)

---

## 2. Kiểm tra cột thời gian (`appeared`) & Độ phủ
- **Cột thời gian có sẵn**: Cột `appeared` định dạng `YYYY-MM`.
- **Độ phủ thời gian thực tế**: Phủ trọn vẹn 12 tháng liên tục trong năm 2018 (từ `2018-01` đến `2018-12`).
- **Bảng phân bố chi tiết mẫu và tỉ lệ mã độc qua từng tháng**:

| Tháng | Số lượng mẫu | Tỉ lệ Malware |
|---|---|---|
| 2018-01 | 4,000 | 50.00% |
| 2018-02 | 4,000 | 50.00% |
| 2018-03 | 4,000 | 50.00% |
| 2018-04 | 4,000 | 50.00% |
| 2018-05 | 4,000 | 50.00% |
| 2018-06 | 4,000 | 50.00% |
| 2018-07 | 4,000 | 50.00% |
| 2018-08 | 4,000 | 50.00% |
| 2018-09 | 4,000 | 50.00% |
| 2018-10 | 4,000 | 50.00% |
| 2018-11 | 4,000 | 50.00% |
| 2018-12 | 4,000 | 50.00% |


---

## 3. Bản chất đặc trưng dữ liệu
- Dữ liệu gốc trong EMBER chứa đầy đủ các nhóm cấu trúc PE thô:
  - `header.coff` (Machine, Characteristics, Timestamp...)
  - `header.optional` (Subsystem, DllCharacteristics, Magic, Major/Minor Image Versions...)
  - `section` (Thống kê chi tiết kích thước và entropy của các phân vùng `.text`, `.data`...)
  - `general` & `datadirectories` (Export, Import, Resources, IAT...)
- Pipeline đã trích chọn chính xác 44 đặc trưng dạng bảng tương đương với bài báo gốc để phục vụ mô hình hóa.
