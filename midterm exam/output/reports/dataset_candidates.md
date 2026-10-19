# Bảng So Sánh Các Ứng Viên Dataset Trên Kaggle

Nhằm phục vụ hai mục tiêu cốt lõi của đề tài:
1. **Tái hiện thực nghiệm (Phần A)**: Khai thác các trường đặc trưng thuộc PE Header để phân loại mã độc/lành tính theo phương pháp của bài báo.
2. **Kiểm tra trôi dạt dữ liệu theo thời gian (Phần B - Temporal Drift)**: Đòi hỏi dataset **bắt buộc phải có thông tin thời gian** (`appeared` / timestamp) để phân chia dữ liệu theo trình tự thời gian (Temporal Split) và đánh giá độ suy giảm hiệu năng theo từng tháng.

Dưới đây là 5 bộ dữ liệu ứng viên tiềm năng nhất trên Kaggle:

| STT | Tên Dataset | Link Kaggle | Kích thước | Số lượng mẫu | Có nhãn (Label)? | Nhãn thời gian (Timestamp/Appeared)? | Giấy phép | Đánh giá độ phù hợp & Lựa chọn |
|---|---|---|---|---|---|---|---|---|
| **1** | **Ember-2018-V2-features** *(dhoogla)* | [Link](https://www.kaggle.com/datasets/dhoogla/ember-2018-v2-features) | ~1.6 GB (Parquet) | 1.000.000 | Có (0: Benign, 1: Malware, -1: Unlabeled) | **Có** (Cột `appeared` định dạng `YYYY-MM` từ 2018-01 đến 2018-12) | CC BY 4.0 / Elastic License | **Cực kỳ phù hợp (Lựa chọn ưu tiên số 1)**: Đúng chuẩn EMBER 2018 benchmark, chứa đầy đủ nhóm PE header features, có nhãn `appeared` chuẩn theo từng tháng để kiểm tra temporal drift. |
| **2** | **PE Malware Machine Learning Dataset** *(subhajournal)* | [Link](https://www.kaggle.com/datasets/subhajournal/pe-malware-machine-learning-dataset) | ~34 MB (CSV) | 19.611 | Có (Cột `Malware`: 0, 1) | **Có** (`TimeDateStamp` Unix timestamp từ header) | ODC-By / CC BY 4.0 | **Phù hợp**: File CSV nhẹ, 78 đặc trưng PE Header chi tiết. Nhược điểm: `TimeDateStamp` là thời gian biên dịch (compile-time) có thể bị tác giả mã độc làm sai lệch (timestomping), không chuẩn bằng `appeared`. |
| **3** | **Malware Detection in PE Files** *(nsaravanan / al2laa)* | [Link](https://www.kaggle.com/datasets/nsaravanan/malware-detection-in-pe-files) | ~45 MB (CSV) | 140.297 | Có (Cột `legitimate`: 0, 1) | Không có nhãn thời gian thu thập (chỉ có `TimeDateStamp`) | Open / Public Domain | **Phù hợp tái hiện Phần A**: Đây chính là tập dữ liệu 140.297 mẫu chứa 54 trường PE Header được tác giả bài báo gốc sử dụng; tuy nhiên thiếu trục thời gian xuất hiện thực tế để làm Phần B. |
| **4** | **Classification of Malwares (CLaMP)** *(saurabhshahane)* | [Link](https://www.kaggle.com/datasets/saurabhshahane/cla-mp-malware-detection-using-pe-header) | ~5 MB (CSV) | 5.184 | Có (Cột `class`: 0, 1) | **Không** | CC BY 4.0 | **Trung bình**: Tập dữ liệu học thuật kinh điển với 54-69 đặc trưng PE Header; kích thước nhỏ (~5k mẫu) và không có nhãn thời gian nên không thể đánh giá drift. |
| **5** | **EMBER 2018 Subset for Malware Detection** *(ang3l0)* | [Link](https://www.kaggle.com/datasets/ang3l0/malware-detection-dataset-ember-2018) | ~250 MB | 100.000 | Có (0: Benign, 1: Malware) | **Có** (`appeared` 2018-01 đến 2018-12) | MIT License | **Rất phù hợp (Dự phòng cho EMBER 1M)**: Bản rút gọn chuẩn của EMBER 2018, giảm tải lưu lượng mạng và RAM nhưng vẫn giữ cấu trúc tháng và các đặc trưng header. |

---

## Quyết định lựa chọn Dataset chính
- **Bộ dữ liệu chính được chọn**: **`dhoogla/ember-2018-v2-features`** (hoặc tập đặc trưng chuẩn của **EMBER 2018**).
- **Lý do lựa chọn**:
  1. Đáp ứng trọn vẹn yêu cầu đề bài: *"Phân loại malware PE từ EMBER và kiểm tra drift theo thời gian"*.
  2. Cung cấp trường nhãn thời gian `appeared` tin cậy (thời điểm mẫu được quan sát thực tế tại VirusTotal/Elastic), hoàn toàn loại bỏ nguy cơ *timestomping*.
  3. Chứa toàn bộ các trường định dạng PE Header (thuộc nhóm đặc trưng LIEF v2) tương thích với 44 trường trong bài báo gốc.
- **Phương pháp lấy mẫu phân tầng (Stratified Temporal Sampling)**:
  - Dataset EMBER gốc có 1.000.000 mẫu (~1.6GB Parquet / ~20GB thô), vượt quá khả năng xử lý mượt mà và nhanh chóng trên máy tính cá nhân nếu huấn luyện 5 thuật toán + cross validation + sliding window.
  - Do đó, thực hiện **lấy mẫu phân tầng theo Tháng và Nhãn** (Stratified Sampling by `appeared` and `label`): Lấy mẫu đại diện cân bằng (ví dụ: 5.000 mẫu/tháng từ tháng 1 đến tháng 12 năm 2018, tổng ~50.000 - 60.000 mẫu) nhằm:
    - Giữ nguyên 100% phân bố tỷ lệ nhãn qua từng tháng.
    - Đảm bảo tính toàn vẹn của hiện tượng drift theo thời gian thực.
    - Tối ưu hóa thời gian chạy `run_all.py` trong khoảng vài phút, bộ nhớ RAM ổn định < 2GB.
