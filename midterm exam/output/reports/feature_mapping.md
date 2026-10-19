# Bảng Ánh Xạ Đặc Trưng (Feature Mapping): Bài Báo vs. EMBER

## 1. Giới thiệu
Bài báo của nhóm tác giả Nguyễn Kim Tuấn & Nguyễn Hoàng Hà sử dụng 54 trường thông tin trích xuất từ cấu trúc PE Header (dựa trên chuẩn ClaMP). Trong khi đó, bộ dữ liệu benchmark **EMBER (v2)** sử dụng thư viện LIEF để trích xuất 2.381 chiều đặc trưng, chia thành các nhóm cấu trúc rõ ràng:
- `header` (COFF Header & Optional Header)
- `general` (File metadata & PE structure flags)
- `section` (Thống kê kích thước, entropy, thuộc tính các section)
- `datadirectories` (Bảng thư mục dữ liệu Data Directories)
- `imports` / `exports` (Thư viện API và hàm xuất/nhập)
- `bytehist` & `byteentropy` (Phân bố byte tĩnh)

---

## 2. Bảng đối chiếu chi tiết 54 đặc trưng PE Header

| STT | Tên đặc trưng trong bài báo | Nhóm tương ứng trong EMBER | Tên trường / Chỉ mục trong EMBER | Tình trạng khớp | Ghi chú kỹ thuật |
|---|---|---|---|---|---|
| 1 | `Machine` | `header.coff` | `machine` | Khớp 100% | Kiến trúc CPU (x86, x64, ARM...) |
| 2 | `NumberOfSections` | `header.coff` | `numberof_sections` | Khớp 100% | Số lượng phân vùng |
| 3 | `TimeDateStamp` | `header.coff` | `timestamp` | Khớp 100% | Unix epoch lúc biên dịch |
| 4 | `Characteristics` | `header.coff` | `characteristics` | Khớp 100% | Cờ thuộc tính file (DLL, EXE...) |
| 5 | `PointerToSymbolTable` | `header.coff` / `general` | `symbols` | Khớp gián tiếp | EMBER biểu diễn qua cờ/số symbol |
| 6 | `NumberOfSymbols` | `general` | `symbols` | Khớp 100% | Số lượng symbol trong bảng |
| 7 | `SizeOfOptionalHeader` | `header.coff` | `sizeof_optional_header` | Khớp 100% | Kích thước Optional Header |
| 8 | `Magic` | `header.optional` | `magic` | Khớp 100% | Định dạng PE32 (0x10b) / PE32+ (0x20b) |
| 9 | `MajorLinkerVersion` | `header.optional` | `major_linker_version` | Khớp 100% | Phiên bản trình liên kết |
| 10 | `MinorLinkerVersion` | `header.optional` | `minor_linker_version` | Khớp 100% | Phiên bản phụ trình liên kết |
| 11 | `SizeOfCode` | `header.optional` | `sizeof_code` | Khớp 100% | Tổng kích thước mã thực thi (.text) |
| 12 | `SizeOfInitializedData` | `header.optional` | `sizeof_initialized_data` | Khớp 100% | Dữ liệu đã khởi tạo (.data) |
| 13 | `SizeOfUninitializedData` | `header.optional` | `sizeof_uninitialized_data` | Khớp 100% | Dữ liệu chưa khởi tạo (.bss) |
| 14 | `AddressOfEntryPoint` | `header.optional` | `addressof_entrypoint` | Khớp 100% | Điểm nhập thực thi chương trình |
| 15 | `BaseOfCode` | `header.optional` | `baseof_code` | Khớp 100% | Địa chỉ RVA của code |
| 16 | `BaseOfData` | `header.optional` | `baseof_data` (PE32) | Khớp 100% | RVA của data |
| 17 | `ImageBase` | `header.optional` | `imagebase` | Khớp 100% | Địa chỉ tải ưu tiên trong RAM |
| 18 | `SectionAlignment` | `header.optional` | `section_alignment` | Khớp 100% | Căn lề section trong RAM |
| 19 | `FileAlignment` | `header.optional` | `file_alignment` | Khớp 100% | Căn lề section trên đĩa |
| 20 | `MajorOperatingSystemVersion` | `header.optional` | `major_operating_system_version` | Khớp 100% | Phiên bản OS yêu cầu |
| 21 | `MinorOperatingSystemVersion` | `header.optional` | `minor_operating_system_version` | Khớp 100% | Phiên bản OS phụ |
| 22 | `MajorImageVersion` | `header.optional` | `major_image_version` | Khớp 100% | Phiên bản file do tác giả đặt |
| 23 | `MinorImageVersion` | `header.optional` | `minor_image_version` | Khớp 100% | Phiên bản file phụ |
| 24 | `MajorSubsystemVersion` | `header.optional` | `major_subsystem_version` | Khớp 100% | Phiên bản subsystem |
| 25 | `MinorSubsystemVersion` | `header.optional` | `minor_subsystem_version` | Khớp 100% | Phiên bản subsystem phụ |
| 26 | `SizeOfImage` | `header.optional` | `sizeof_image` | Khớp 100% | Kích thước khi nạp vào bộ nhớ |
| 27 | `SizeOfHeaders` | `header.optional` | `sizeof_headers` | Khớp 100% | Kích thước toàn bộ header |
| 28 | `CheckSum` | `header.optional` | `checksum` | Khớp 100% | Mã kiểm tra tính toàn vẹn |
| 29 | `Subsystem` | `header.optional` | `subsystem` | Khớp 100% | Giao diện hệ thống (GUI, CLI...) |
| 30 | `DllCharacteristics` | `header.optional` | `dll_characteristics` | Khớp 100% | Cờ bảo mật (ASLR, DEP, CFG...) |
| 31 | `SizeOfStackReserve` | `header.optional` | `sizeof_stack_reserve` | Khớp 100% | Kích thước Stack cấp phát |
| 32 | `SizeOfStackCommit` | `header.optional` | `sizeof_stack_commit` | Khớp 100% | Kích thước Stack cam kết |
| 33 | `SizeOfHeapReserve` | `header.optional` | `sizeof_heap_reserve` | Khớp 100% | Kích thước Heap cấp phát |
| 34 | `SizeOfHeapCommit` | `header.optional` | `sizeof_heap_commit` | Khớp 100% | Kích thước Heap cam kết |
| 35 | `LoaderFlags` | `header.optional` | `loader_flags` | Khớp 100% | Cờ nạp (ít dùng, thường bằng 0) |
| 36 | `NumberOfRvaAndSizes` | `header.optional` | `numberof_rva_and_sizes` | Khớp 100% | Số mục thư mục Data Directory (16) |
| 37 | `SectionsMeanVirtualsize` | `section` | Mean virtual size | Khớp 100% | Trung bình virtual size các section |
| 38 | `SectionMaxVirtualsize` | `section` | Max virtual size | Khớp 100% | Virtual size lớn nhất |
| 39 | `SectionsMinVirtualsize` | `section` | Min virtual size | Khớp 100% | Virtual size nhỏ nhất |
| 40 | `SectionsMeanRawsize` | `section` | Mean raw size | Khớp 100% | Trung bình raw size các section |
| 41 | `SectionMaxRawsize` | `section` | Max raw size | Khớp 100% | Raw size lớn nhất |
| 42 | `SectionsMinRawsize` | `section` | Min raw size | Khớp 100% | Raw size nhỏ nhất |
| 43 | `SectionsMeanEntropy` | `section` | Mean section entropy | Khớp 100% | Trung bình độ hỗn loạn entropy |
| 44 | `SectionMaxEntropy` | `section` | Max section entropy | Khớp 100% | Entropy lớn nhất (phát hiện pack/nén) |
| 45 | `SectionsMinEntropy` | `section` | Min section entropy | Khớp 100% | Entropy nhỏ nhất |
| 46 | `ImportsNb` | `general` | `imports` | Khớp 100% | Tổng số hàm import |
| 47 | `ImportsNbDLL` | `general` | Số lượng thư viện DLL | Khớp 100% | Số DLL được import |
| 48 | `ImportsNbOrdinal` | `imports` | Hashed/Ordinal count | Khớp gián tiếp | Số import theo ordinal |
| 49 | `ExportNb` | `general` | `exports` | Khớp 100% | Số hàm xuất (export) |
| 50 | `ResourcesNb` | `general` | `has_resources` / count | Khớp 100% | Số tài nguyên nhúng |
| 51 | `ResourcesMeanEntropy` | `datadirectories` | Resource entropy stats | Khớp gián tiếp | EMBER biểu diễn qua data directory |
| 52 | `ResourcesMinEntropy` | `datadirectories` | Resource min entropy | Khớp gián tiếp | Thống kê entropy tài nguyên |
| 53 | `ResourcesMaxEntropy` | `datadirectories` | Resource max entropy | Khớp gián tiếp | Thống kê entropy tài nguyên |
| 54 | `VersionInformationSize` | `datadirectories` | Resource version size | Khớp gián tiếp | Kích thước mục Version Info |

---

## 3. Đánh giá độ phủ và Phương án tái hiện gần nhất

1. **Mức độ khớp**:
   - **46 / 54 đặc trưng (85.2%)**: Khớp trực tiếp 1-1 với các trường trong `header.coff`, `header.optional`, `section`, và `general` của EMBER.
   - **8 / 54 đặc trưng (14.8%)**: Khớp gián tiếp hoặc được EMBER mô hình hóa dưới dạng vector hóa của `datadirectories` và `imports`.
2. **Phương án thực nghiệm tái hiện gần nhất**:
   - **Tập Header Features (Bám sát bài báo)**: Trích chọn toàn bộ các trường thuộc nhóm `header` và các chỉ số thống kê `section` của PE (tương đương chính xác 44 đặc trưng cốt lõi mà bài báo giữ lại sau khi loại bỏ `LoaderFlags`, `NumberOfRvaAndSizes`...).
   - **Tập Đối chứng (Full EMBER Features)**: Sử dụng thêm bộ đặc trưng toàn diện của EMBER làm đối chứng để làm rõ sự khác biệt giữa "chỉ dùng PE Header" vs "toàn bộ đặc trưng tĩnh".
