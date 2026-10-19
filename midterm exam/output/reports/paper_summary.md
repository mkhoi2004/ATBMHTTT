# Tóm Tắt Báo Cáo Nghiên Cứu

## 1. Thông tin chung
- **Tên bài báo**: Phát hiện malware dựa trên header của tập tin PE sử dụng Machine learning (*Malware detection based on PE file header by using Machine learning*).
- **Tác giả**: Nguyễn Kim Tuấn (Trường Đại học Duy Tân) & Nguyễn Hoàng Hà (Trường Đại học Khoa học Huế).
- **Đối tượng nghiên cứu**: Tập tin thực thi PE (Portable Executable - `.exe`, `.dll`, ...) trên hệ điều hành Windows.

---

## 2. Bài toán và Động lực nghiên cứu
- **Bối cảnh**: Mã độc (malware) liên tục gia tăng và biến thể tinh vi trên nền tảng Windows.
- **Vấn đề của kỹ thuật truyền thống**: Kỹ thuật nhận dạng theo chữ ký (signature-based) có tỷ lệ cảnh báo sai thấp nhưng bất lực trước mã độc biến hình (polymorphic/metamorphic) và mã độc chưa từng biết (zero-day/unknown).
- **Ý tưởng tiếp cận**: Sử dụng Machine Learning phi chữ ký (non-signature based) khai thác các trường thông tin trong PE Header. Tập tin PE lành tính (benign) luôn tuân thủ cấu trúc chuẩn hóa của Windows API/Loader; ngược lại mã độc thường can thiệp, chỉnh sửa hoặc có cấu trúc bất thường tại các trường header này.

---

## 3. Dữ liệu thực nghiệm
- **Tổng số mẫu**: 140.297 mẫu PE header (tương đương với bộ dữ liệu benchmark ClaMP).
  - **Mẫu mã độc (Malware)**: 44.214 mẫu thu thập từ kho `virusshare.com`.
  - **Mẫu lành tính (Benign)**: 96.083 mẫu thu thập từ các tập tin PE sạch của hệ điều hành Windows.
  - Tỉ lệ phân bố: ~31.5% Malware và ~68.5% Benign.

---

## 4. Tập đặc trưng (PE Header Features)
- **Số đặc trưng ban đầu**: 54 trường (fields) trong PE Header.
- **Phương pháp đánh giá và lựa chọn đặc trưng**:
  - Dùng mô hình Random Forest và Extra Trees để tính toán mức độ quan trọng (Feature Importance).
  - **Top đặc trưng quan trọng nhất**:
    1. `ImageBase` (0.193689)
    2. `SizeOfStackReserve` (0.103419)
    3. `VersionInformationSize` (0.075304)
    4. `MinorImageVersion` (0.065888)
    5. `ResourcesMinSize` (0.058338)
    6. `Characteristics` (0.052923)
    7. `ExportNb` (0.052831)
    8. `Subsystem` (0.049870)
    9. `MajorOSVersion` (0.045429)
    10. `ResourcesNb` (0.037733)
  - **Loại bỏ các đặc trưng ít ảnh hưởng**: `LoaderFlags` (0.000002), `NumberOfRvaAndSizes` (0.000008), `SizeOfHeapCommit` (0.000225), `SizeOfHeapReserve` (0.000401)...
  - Giữ lại tập chuẩn gồm **44 đặc trưng** để cân bằng hiệu năng và tài nguyên tính toán.
  - Thử nghiệm rút gọn tối đa xuống **13 – 15 đặc trưng** quan trọng nhất.

---

## 5. Mô hình và Thực nghiệm

### Thực nghiệm 1: Phân chia 80% Train / 20% Test ngẫu nhiên
Đánh giá 5 thuật toán học máy trên tập 44 đặc trưng:
| Thuật toán | Độ chính xác (Accuracy) | Thời gian huấn luyện (s) |
|---|---|---|
| AdaBoost | 99.12% | 12.83 s |
| GradientBoosting | 99.30% | 30.76 s |
| DecisionTree | 99.34% | 0.98 s |
| ExtraTree | 99.69% | 9.74 s |
| **RandomForest** | **99.71%** | **13.17 s** |

### Thực nghiệm 2: Đánh giá K-Fold Cross Validation (K = 10)
Kiểm tra khả năng chống overfit trên toàn bộ tập dữ liệu:
| Thuật toán | Độ chính xác trung bình | Độ chính xác min | Độ chính xác max |
|---|---|---|---|
| AdaBoost | 99.11% | 99.05% | 99.17% |
| GradientBoosting | 99.31% | 99.24% | 99.37% |
| DecisionTree | 99.34% | 99.26% | 99.42% |
| ExtraTree | 99.71% | 99.67% | 99.75% |
| **RandomForest** | **99.72%** | **99.66%** | **99.76%** |

### Thực nghiệm 3: Khảo sát số cây (n_estimators) trong Random Forest
- Thử nghiệm từ 1 đến 500 cây (lấy trung bình 10 lần chạy).
- Dưới 20 cây: Độ chính xác thấp và dao động lớn.
- Từ 100 cây trở đi: Độ chính xác tiệm cận tối ưu (~99.71%) và bắt đầu bão hòa.
- Kết luận: Chọn $n_{estimators} = 100$ là điểm tối ưu cân bằng giữa độ chính xác và chi phí tài nguyên/thời gian.

### Thực nghiệm 4: Ảnh hưởng của việc cắt giảm số lượng đặc trưng
- Khi rút gọn từ 44 đặc trưng xuống còn 13 – 15 đặc trưng:
  - Accuracy: Giảm không đáng kể, từ 99.72% xuống 99.63% (chỉ giảm 0.09%).
  - Thời gian huấn luyện: Giảm mạnh từ 13.17s xuống 3.88s (tiết kiệm hơn 70% thời gian).

---

## 6. Hạn chế của bài báo (Khoảng trống nghiên cứu)
1. **Thiếu chiều thời gian (No Temporal Evaluation)**: Bài báo sử dụng phép chia ngẫu nhiên (random train-test split 80/20 và 10-fold CV). Trong thực tế, dữ liệu bảo mật luôn gắn liền với thời gian; chia ngẫu nhiên dẫn đến hiện tượng rò rỉ tương lai (*temporal data leakage* / *look-ahead bias*).
2. **Không đánh giá trôi dạt dữ liệu (Concept Drift & Data Drift)**: Mã độc luôn tiến hóa theo thời gian (kỹ thuật đóng gói packer mới, họ mã độc mới, chiến dịch tấn công mới). Mô hình không được kiểm tra xem sau 3, 6 hay 12 tháng thì hiệu năng suy giảm bao nhiêu.
3. **Thước đo đánh giá sơ sài (Evaluation Metrics)**: Chỉ báo cáo Accuracy và Training Time. Trong an ninh mạng, bài toán mất cân bằng lớp đòi hỏi phải đánh giá:
   - **FPR (False Positive Rate / False Alarm Rate)**: Báo nhầm phần mềm sạch thành mã độc sẽ làm gián đoạn vận hành hệ thống.
   - **Recall / TPR**: Tỷ lệ bắt trúng mã độc.
   - **ROC-AUC & PR-AUC**: Đánh giá toàn diện ngưỡng phân loại.
4. **Không có giải pháp thích ứng (Adaptation / Retraining Strategy)**: Không khảo sát các cơ chế huấn luyện lại (Retraining, Sliding Window) để bù đắp suy giảm hiệu năng khi có drift.

---

## 7. Định hướng mở rộng trong đề tài này
- Kế thừa nhóm đặc trưng PE Header và mô hình Random Forest / LightGBM.
- Khai thác tập dữ liệu **EMBER** (chuẩn benchmark bảo mật có gắn mốc thời gian `appeared` theo từng tháng).
- Thực hiện **Temporal Split** (huấn luyện trên các tháng đầu, kiểm thử trên các tháng tương lai).
- Đo lường mức độ suy giảm hiệu năng theo thời gian và phân tích drift bằng **PSI (Population Stability Index)** và **KS-test**.
- Triển khai chiến lược **Periodic Retraining (Sliding Window)** để chứng minh giải pháp kiểm soát drift hiệu quả.
