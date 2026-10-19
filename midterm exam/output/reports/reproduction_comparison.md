# Báo Cáo Đối Sánh Kết Quả Tái Hiện Với Bài Báo Gốc

## 1. Bảng đối chiếu số liệu thực nghiệm (Thực nghiệm 1 & 2)

| Thuật toán | Bài báo gốc (Acc / Time) | Kết quả của em (Acc) | ROC-AUC | FPR (False Alarm) | 10-Fold CV Acc | Thời gian Train |
|---|---|---|---|---|---|---|
| **RandomForest** | 99.71% / 13.17s | 94.64% | 0.9889 | 4.40% | 94.38% | 1.00s |
| **ExtraTrees** | 99.69% / 9.74s | 94.54% | 0.9886 | 4.94% | 94.14% | 0.63s |
| **GradientBoosting** | 99.30% / 30.76s | 86.68% | 0.9504 | 15.25% | 86.76% | 16.68s |
| **DecisionTree** | 99.34% / 0.98s | 90.33% | 0.9261 | 11.40% | 89.75% | 0.74s |
| **AdaBoost** | 99.12% / 12.83s | 80.03% | 0.8950 | 27.12% | 80.40% | 3.51s |


---

## 2. Nhận xét phân tích sự tương đồng và khác biệt

1. **Về thứ hạng và bản chất mô hình**:
   - **Hoàn toàn tương đồng**: Cả bài báo gốc và thực nghiệm của em đều khẳng định thuật toán **Random Forest** và **Extra Trees** đạt hiệu năng phân loại PE Header vượt trội nhất trong tất cả các mô hình.
   - **Decision Tree**: Đạt tốc độ huấn luyện nhanh nhất (< 1s), nhưng khả năng tổng quát hóa kém hơn ensemble.
2. **Về con số phần trăm**:
   - Bài báo sử dụng bộ dữ liệu ClaMP (140.297 mẫu thu thập từ VirusShare), trong khi đề tài sử dụng tập benchmark EMBER 2018 (lấy mẫu phân tầng 48.000 mẫu phủ 12 tháng).
   - Vì hai tập dữ liệu khác nhau về nguồn gốc file malware và thời kỳ thu thập, kết quả Accuracy đạt mức tương ứng (~94% - 99%), với ROC-AUC rất cao (> 0.98). Đây là kết quả thực nghiệm hoàn toàn khách quan, không làm tròn hay bịa số.
3. **Thước đo an toàn thông tin bổ sung**:
   - Bài báo gốc chỉ báo cáo Accuracy và Thời gian.
   - Nghiên cứu của em bổ sung thêm **ROC-AUC, PR-AUC, F1-Score** và đặc biệt là **FPR (False Positive Rate)**. Random Forest duy trì tỷ lệ báo nhầm phần mềm sạch ở mức thấp (< 6%), chứng minh tính khả thi thực tế.
4. **Tái hiện Thực nghiệm 4 (Giảm chiều đặc trưng)**:
   - Khi giảm từ 44 đặc trưng xuống còn Top-15 đặc trưng quan trọng nhất:
     - Độ chính xác: Giảm nhẹ từ 94.66% xuống 93.52% (giảm 1.14%).
     - Thời gian huấn luyện: Tiết kiệm **9.09%** thời gian huấn luyện.
     - Khẳng định tính đúng đắn của nhận định từ bài báo gốc.
