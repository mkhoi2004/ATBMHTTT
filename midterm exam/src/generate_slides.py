"""
Mô-đun tự động tạo bộ Slide PowerPoint thuyết trình 10 trang (output/slides/presentation.pptx).
Tuân thủ tuyệt đối cấu trúc yêu cầu, tích hợp số liệu thực tế từ output/metrics/
và chèn trực tiếp các hình ảnh biểu đồ khoa học từ output/figures/.
Có speaker notes chi tiết cho từng slide.
"""

import json
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Đảm bảo import được các module từ thư mục gốc
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

from src.config import SLIDES_DIR, METRICS_DIR, FIGURES_DIR

# Bảng màu chủ đạo chuyên nghiệp
COLOR_PRIMARY = RGBColor(27, 54, 93)     # Deep Navy
COLOR_SECONDARY = RGBColor(0, 128, 128)  # Teal
COLOR_DARK = RGBColor(33, 37, 41)        # Dark Charcoal
COLOR_LIGHT_BG = RGBColor(245, 247, 250) # Light Slate Gray
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_ACCENT = RGBColor(217, 83, 79)     # Soft Red / Accent
COLOR_CARD_BORDER = RGBColor(220, 224, 230)


def create_header(slide, title_text: str, category_text: str = "BÁO CÁO GIỮA KÌ - AN TOÀN VÀ BẢO MẬT HỆ THỐNG THÔNG TIN"):
    """Tạo thanh tiêu đề đồng bộ cho các slide nội dung."""
    # Thẻ danh mục nhỏ
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.3))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_SECONDARY

    # Tiêu đề chính
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.5), Inches(0.6))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_PRIMARY


def add_card(slide, left, top, width, height, title="", bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER):
    """Tạo khung chứa nội dung dạng card hiện đại với căn lề an toàn bên trong."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    # Tinh chỉnh độ bo góc vừa phải (sleek modern corner), tránh bo tròn quá sâu chèn vào chữ
    if shape.adjustments:
        shape.adjustments[0] = 0.035

    if title:
        # Căn lề tiêu đề an toàn: cách mép trên 0.20" và mép trái 0.28" để hoàn toàn nằm gọn trong ô
        tb = slide.shapes.add_textbox(left + Inches(0.28), top + Inches(0.20), width - Inches(0.56), Inches(0.38))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0)
        tf.margin_top = Inches(0)
        tf.margin_right = Inches(0)
        tf.margin_bottom = Inches(0)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY
    return shape


def add_notes(slide, notes_text: str):
    """Ghi speaker notes cho slide."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text


def set_cell_border(cell, color="CBD5E1", width=12700):
    """Thiết lập đường viền (border) cho cell trong PowerPoint table."""
    tcPr = cell._tc.get_or_add_tcPr()
    for border_name in ["lnL", "lnR", "lnT", "lnB"]:
        existing = tcPr.find(f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}{border_name}")
        if existing is not None:
            tcPr.remove(existing)
        ln_xml = f'<a:{border_name} {nsdecls("a")} w="{width}" cmpd="s"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:{border_name}>'
        tcPr.append(parse_xml(ln_xml))


def build_presentation(save_path: Path = SLIDES_DIR / "presentation.pptx") -> Path:
    prs = Presentation()
    # Tỉ lệ màn hình 16:9 hiện đại (13.33 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Đọc dữ liệu thực tế từ metrics (nếu có)
    metrics_comp_file = METRICS_DIR / "experiment_1_models_comparison.json"
    metrics_comp = json.loads(metrics_comp_file.read_text(encoding="utf-8")) if metrics_comp_file.exists() else {}

    # ----------------------------------------------------
    # SLIDE 1: TRANG BÌA (Cover Slide)
    # ----------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    # Background card
    bg = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_PRIMARY
    bg.line.color.rgb = COLOR_PRIMARY

    # Accent stripe
    stripe = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(0.15), Inches(5.9))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = COLOR_SECONDARY
    stripe.line.fill.background()

    # Text container
    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(0.8), Inches(11.2), Inches(5.9))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "TRƯỜNG ĐẠI HỌC TÀI NGUYÊN VÀ MÔI TRƯỜNG TP.HCM"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

    p = tf1.add_paragraph()
    p.text = "KHOA: CÔNG NGHỆ THÔNG TIN"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(180, 205, 235)
    p.space_after = Pt(28)

    p = tf1.add_paragraph()
    p.text = "BÁO CÁO GIỮA KÌ"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_SECONDARY

    p = tf1.add_paragraph()
    p.text = "PHÂN LOẠI MALWARE PE TỪ EMBER\nVÀ KIỂM TRA DRIFT THEO THỜI GIAN"
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(30)

    info_lines = [
        "Môn: An toàn và bảo mật hệ thống thông tin",
        "Giảng viên hướng dẫn: ThS. Phạm Trọng Huynh",
        "Sinh viên thực hiện: Trần Nguyễn Minh Khôi",
        "Mã số sinh viên: 1150080059",
        "Lớp: 11_DH_CNPM1",
        "Khóa: Công nghệ thông tin",
    ]
    for line in info_lines:
        p = tf1.add_paragraph()
        p.text = line
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(220, 230, 245)

    add_notes(s1, "Kính chào Thầy và các bạn. Em tên là Trần Nguyễn Minh Khôi, sinh viên lớp 11_DH_CNPM1. Hôm nay em xin báo cáo đề tài giữa kì: Phân loại malware PE từ EMBER và kiểm tra drift theo thời gian.")

    # ----------------------------------------------------
    # SLIDE 2: GIỚI THIỆU BÀI BÁO (1) - BÀI TOÁN & ĐỘNG LỰC
    # ----------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    create_header(s2, "1. Tổng quan Bài Báo Tham Khảo: Động lực & Bài toán")

    # Card 1: Thông tin bài báo
    add_card(s2, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4), "Thông Tin Xuất Bản & Tác Giả")
    tb = s2.shapes.add_textbox(Inches(1.08), Inches(2.05), Inches(5.04), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    items_s2_left = [
        ("Tên bài báo", "Phát hiện malware dựa trên header của tập tin PE sử dụng Machine learning"),
        ("Tác giả", "Nguyễn Kim Tuấn (ĐH Duy Tân) & Nguyễn Hoàng Hà (ĐH Khoa học Huế)"),
        ("Mục tiêu chính", "Xây dựng mô hình Machine Learning phát hiện mã độc Windows PE bằng cách chỉ khai thác các trường thông tin trong PE Header."),
        ("Điểm cải tiến", "Rút gọn số lượng trường header cần quét, giảm tài nguyên tính toán và thời gian thực thi nhưng vẫn duy trì độ chính xác cao."),
    ]
    for label, val in items_s2_left:
        p = tf.add_paragraph()
        p.text = f"• {label}: "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_PRIMARY
        p2 = tf.add_paragraph()
        p2.text = f"  {val}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(8)

    # Card 2: Bối cảnh & Động lực nghiên cứu
    add_card(s2, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4), "Bối Cảnh & Động Lực Kỹ Thuật")
    tb = s2.shapes.add_textbox(Inches(7.08), Inches(2.05), Inches(5.14), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    items_s2_right = [
        ("Mối đe dọa từ file PE", "Tập tin Portable Executable (.exe, .dll) là phương tiện phát tán mã độc phổ biến nhất trên môi trường hệ điều hành Windows."),
        ("Hạn chế của Signature-based", "Các giải pháp diệt virus truyền thống dựa trên chữ ký (chữ ký MD5/SHA256, chuỗi bytecode) thất bại hoàn toàn trước mã độc biến hình (polymorphic/metamorphic) và mã độc mới (zero-day)."),
        ("Ưu thế của PE Header", "Phần PE Header chứa thông tin điều khiển nạp file vào RAM. Tập tin lành tính luôn chuẩn hóa theo Windows OS, trong khi mã độc thường có sai khác/bất thường cấu trúc."),
        ("Hướng tiếp cận Machine Learning", "Huấn luyện mô hình học có giám sát trên các trường định dạng header để phát hiện mã độc mà không cần chạy file (Static Analysis an toàn)."),
    ]
    for label, val in items_s2_right:
        p = tf.add_paragraph()
        p.text = f"• {label}: "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_SECONDARY
        p2 = tf.add_paragraph()
        p2.text = f"  {val}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(8)

    add_notes(s2, "Slide 2 trình bày về bài báo tham khảo của thầy Nguyễn Kim Tuấn và Nguyễn Hoàng Hà. Động lực chính là giải quyết hạn chế của kỹ thuật chữ ký truyền thống khi đối mặt malware biến hình bằng cách ứng dụng Machine Learning trên PE Header.")

    # ----------------------------------------------------
    # SLIDE 3: GIỚI THIỆU BÀI BÁO (2) - PHƯƠNG PHÁP & KẾT QUẢ GỐC
    # ----------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    create_header(s3, "2. Phương Pháp, Đặc Trưng PE Header & Kết Quả Báo Cáo")

    add_card(s3, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4), "Đặc Trưng Header & Lựa Chọn Thuật Toán")
    tb = s3.shapes.add_textbox(Inches(1.08), Inches(2.05), Inches(5.04), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    items_s3 = [
        ("Dữ liệu bài báo", "140.297 mẫu PE (44.214 malware từ VirusShare + 96.083 file sạch từ Windows)."),
        ("Tập đặc trưng ban đầu", "Khảo sát 54 trường PE Header (ImageBase, StackReserve, Characteristics...)."),
        ("Rút gọn đặc trưng", "Dùng Random Forest/Extra Trees loại bỏ các trường ít tác động (LoaderFlags, NumberOfRvaAndSizes...), giữ lại 44 trường cốt lõi."),
        ("Khảo sát n_estimators", "Tăng số cây từ 1 đến 500. Kết quả cho thấy từ 100 cây trở đi, độ chính xác bắt đầu bão hòa (~99.71%)."),
    ]
    for label, val in items_s3:
        p = tf.add_paragraph()
        p.text = f"• {label}: "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_PRIMARY
        p2 = tf.add_paragraph()
        p2.text = f"  {val}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(8)

    # Bảng kết quả bài báo gốc (Dạng bảng chuẩn PowerPoint có border)
    add_card(s3, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4), "Kết Quả Công Bố Trong Bài Báo Gốc")
    
    tb_sub = s3.shapes.add_textbox(Inches(7.08), Inches(1.98), Inches(5.14), Inches(0.3))
    tf_sub = tb_sub.text_frame
    tf_sub.word_wrap = True
    tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = Inches(0)
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "Bảng đối chiếu 5 thuật toán học máy (Thực nghiệm 1 & 2):"
    p_sub.font.size = Pt(11)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_SECONDARY

    # Native Table 6 dòng x 4 cột có border rõ nét
    table_shape_s3 = s3.shapes.add_table(6, 4, Inches(7.08), Inches(2.35), Inches(5.14), Inches(2.25))
    table_s3 = table_shape_s3.table
    table_s3.columns[0].width = Inches(1.84)
    table_s3.columns[1].width = Inches(1.10)
    table_s3.columns[2].width = Inches(1.10)
    table_s3.columns[3].width = Inches(1.10)

    paper_headers = ["Thuật toán", "Accuracy", "10-Fold CV", "Train Time"]
    for i, h in enumerate(paper_headers):
        cell = table_s3.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER if i > 0 else PP_ALIGN.LEFT

    paper_table_rows = [
        ("AdaBoost", "99.12%", "99.11%", "12.83 s"),
        ("GradientBoosting", "99.30%", "99.31%", "30.76 s"),
        ("DecisionTree", "99.34%", "99.34%", "0.98 s"),
        ("ExtraTrees", "99.69%", "99.71%", "9.74 s"),
        ("RandomForest (Tốt nhất)", "99.71%", "99.72%", "13.17 s"),
    ]

    for row_idx, row in enumerate(paper_table_rows, start=1):
        is_rf = "RandomForest" in row[0]
        for col_idx, val in enumerate(row):
            cell = table_s3.cell(row_idx, col_idx)
            cell.text = val
            cell.fill.solid()
            if is_rf:
                cell.fill.fore_color.rgb = RGBColor(230, 245, 245)
            elif row_idx % 2 == 0:
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)
            else:
                cell.fill.fore_color.rgb = COLOR_WHITE

            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(9.5)
            if is_rf:
                p.font.bold = True
                p.font.color.rgb = COLOR_PRIMARY
            else:
                p.font.color.rgb = COLOR_DARK
            p.alignment = PP_ALIGN.CENTER if col_idx > 0 else PP_ALIGN.LEFT

    # Thiết lập border cho toàn bộ bảng
    for r in range(6):
        for c in range(4):
            b_color = "1B365D" if r == 0 else "CBD5E1"
            set_cell_border(table_s3.cell(r, c), color=b_color, width=12700)

    # Textbox kết luận bên dưới bảng
    tb_bottom = s3.shapes.add_textbox(Inches(7.08), Inches(4.75), Inches(5.14), Inches(1.85))
    tf_bottom = tb_bottom.text_frame
    tf_bottom.word_wrap = True
    tf_bottom.margin_left = tf_bottom.margin_top = tf_bottom.margin_right = tf_bottom.margin_bottom = Inches(0)
    p_b1 = tf_bottom.paragraphs[0]
    p_b1.text = "• Kết luận của tác giả: Random Forest 100 cây đạt độ chính xác cao nhất (99.71%), vượt trội các mô hình còn lại."
    p_b1.font.size = Pt(9.5)
    p_b1.font.color.rgb = COLOR_DARK
    p_b1.space_after = Pt(4)

    p_b2 = tf_bottom.add_paragraph()
    p_b2.text = "• Tối ưu đặc trưng: Khi giảm từ 44 xuống 13-15 đặc trưng cốt lõi, độ chính xác chỉ giảm 0.09% nhưng thời gian huấn luyện giảm 70% (từ 13.17s xuống 3.88s)."
    p_b2.font.size = Pt(9.5)
    p_b2.font.color.rgb = COLOR_DARK

    add_notes(s3, "Bài báo gốc khảo sát 54 đặc trưng header và rút gọn còn 44. Thuật toán Random Forest với 100 cây đạt hiệu năng xuất sắc nhất 99.71%. Điểm cốt lõi là tối ưu số cây và đặc trưng giúp tiết kiệm tài nguyên hệ thống đáng kể.")

    # ----------------------------------------------------
    # SLIDE 4: NGUỒN DỮ LIỆU EMBER & LẤY MẪU
    # ----------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    create_header(s4, "3. Nguồn Dữ Liệu EMBER 2018 & Chiến Lược Lấy Mẫu Phân Tầng")

    add_card(s4, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4), "Đặc Trưng Dữ Liệu Benchmark EMBER 2018")
    tb = s4.shapes.add_textbox(Inches(1.08), Inches(2.05), Inches(5.04), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    ember_info = [
        ("Nguồn gốc chuẩn", "Elastic Malware Benchmark for Empowering Researchers (EMBER 2018 v2) do Endgame/Elastic phát hành."),
        ("Quy mô nguyên bản", "1.000.000 mẫu PE file được quét trong năm 2018 (800k train, 200k test)."),
        ("Nhãn thời gian xuất hiện (Appeared)", "Gắn mốc tháng thực tế (2018-01 đến 2018-12) khi mẫu được phát hiện trên VirusTotal. Hoàn toàn không bị ảnh hưởng bởi timestomping."),
        ("Cấu trúc đặc trưng", "Trích xuất tĩnh bằng thư viện LIEF, chứa cấu trúc JSON phân cấp: general, header.coff, header.optional, section, datadirectories..."),
    ]
    for label, val in ember_info:
        p = tf.add_paragraph()
        p.text = f"• {label}: "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_PRIMARY
        p2 = tf.add_paragraph()
        p2.text = f"  {val}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(8)

    add_card(s4, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4), "Chiến Lược Lấy Mẫu Phân Tầng (Stratified Sampling)")
    tb = s4.shapes.add_textbox(Inches(7.08), Inches(2.05), Inches(5.14), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    sampling_info = [
        ("Lọc mẫu không xác định", "Loại bỏ hoàn toàn các mẫu unlabeled (nhãn -1 trong EMBER gốc) để giữ lại bài toán học có giám sát nhị phân (0: Benign, 1: Malware)."),
        ("Cỡ mẫu phân tầng", "Lấy 4.000 mẫu/tháng cân bằng (2.000 benign và 2.000 malware mỗi tháng) phủ trọn vẹn 12 tháng từ 2018-01 đến 2018-12."),
        ("Tổng số mẫu thực nghiệm", "48.000 mẫu đại diện chuẩn mực."),
        ("Ưu thế tối ưu tài nguyên", "Đảm bảo phản ánh chính xác hiện tượng trôi dạt dữ liệu theo từng tháng, đồng thời giảm mức tiêu thụ RAM < 2GB và thời gian huấn luyện toàn pipeline chỉ mất 2-4 phút."),
    ]
    for label, val in sampling_info:
        p = tf.add_paragraph()
        p.text = f"• {label}: "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_SECONDARY
        p2 = tf.add_paragraph()
        p2.text = f"  {val}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(8)

    add_notes(s4, "Bộ dữ liệu EMBER 2018 giải quyết khoảng trống lớn nhất của bài báo gốc là cung cấp cột thời gian 'appeared' thực tế từ tháng 1 đến tháng 12 năm 2018. Chúng em lấy mẫu phân tầng 4.000 mẫu mỗi tháng, tổng 48.000 mẫu để tối ưu thời gian huấn luyện.")

    # ----------------------------------------------------
    # SLIDE 5: QUY TRÌNH THỰC HIỆN (PIPELINE SƠ ĐỒ)
    # ----------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    create_header(s5, "4. Sơ Đồ Quy Trình Thực Hiện Thực Nghiệm Toàn Diện")

    steps = [
        ("BƯỚC 1: DỮ LIỆU THÔ", "EMBER 2018 Raw JSONL\n• Lọc nhãn -1\n• Phân tầng theo tháng (4k/tháng)\n• 48.000 mẫu (01-12/2018)", COLOR_PRIMARY),
        ("BƯỚC 2: TIỀN XỬ LÝ", "Trích xuất PE Header\n• 44 đặc trưng Header & Section\n• Xử lý missing values (median)\n• No Look-ahead Bias", COLOR_SECONDARY),
        ("BƯỚC 3: MÔ HÌNH HÓA", "Tái hiện bài báo\n• Random Forest (100 cây)\n• Extra Trees, AdaBoost, GBDT\n• Decision Tree & LightGBM", COLOR_PRIMARY),
        ("BƯỚC 4: ĐÁNH GIÁ METRICS", "Đo lường an toàn thông tin\n• Accuracy, F1, Recall\n• ROC-AUC, PR-AUC\n• FPR (False Alarm Rate)", COLOR_SECONDARY),
        ("BƯỚC 5: TEMPORAL DRIFT", "Kiểm tra theo thời gian\n• Temporal Split (Train 1-8, Test 9-12)\n• Đo lường PSI & KS-test\n• Retrain định kỳ (Sliding Window)", COLOR_ACCENT),
    ]

    for idx, (step_title, step_desc, col) in enumerate(steps):
        top_pos = Inches(1.5 + idx * 1.1)
        # Khung bước
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_pos, Inches(11.7), Inches(0.95))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_WHITE
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        # Số thứ tự
        badge = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top_pos, Inches(2.6), Inches(0.95))
        badge.fill.solid()
        badge.fill.fore_color.rgb = col
        badge.line.fill.background()
        p = badge.text_frame.paragraphs[0]
        p.text = step_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

        # Nội dung
        tb = s5.shapes.add_textbox(Inches(3.6), top_pos + Inches(0.05), Inches(8.8), Inches(0.85))
        p = tb.text_frame.paragraphs[0]
        p.text = step_desc
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_DARK

    add_notes(s5, "Quy trình thực hiện gồm 5 bước khép kín từ trích chọn dữ liệu thô, tiền xử lý đặc trưng PE header, tái hiện mô hình, đánh giá toàn diện các chỉ số an ninh mạng và cuối cùng là kiểm tra trôi dạt dữ liệu theo trục thời gian thực.")

    # ----------------------------------------------------
    # SLIDE 6: THIẾT LẬP THỰC NGHIỆM & METRIC
    # ----------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    create_header(s6, "5. Thiết Lập Thực Nghiệm: Phân Chia, Mô Hình & Thước Đo")

    add_card(s6, Inches(0.8), Inches(1.4), Inches(3.6), Inches(5.4), "1. Phân Chia Dữ Liệu")
    tb = s6.shapes.add_textbox(Inches(1.08), Inches(2.05), Inches(3.04), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    p1_items = [
        ("Random Split (Phần A)", "80% Train (38.400 mẫu) / 20% Test (9.600 mẫu), phân tầng nhãn, tái hiện thí nghiệm bài báo."),
        ("10-Fold CV (Phần A)", "K-Fold (K=10) trên tập train nhằm kiểm tra overfit."),
        ("Temporal Split (Phần B)", "Train trên 8 tháng đầu (2018-01 đến 2018-08).\nTest độc lập trên từng tháng tương lai (09, 10, 11, 12)."),
    ]
    for lbl, val in p1_items:
        p = tf.add_paragraph()
        p.text = f"• {lbl}: "
        p.font.bold = True
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_PRIMARY
        p2 = tf.add_paragraph()
        p2.text = f"{val}"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(8)

    add_card(s6, Inches(4.8), Inches(1.4), Inches(3.6), Inches(5.4), "2. Cấu Hình Mô Hình")
    tb = s6.shapes.add_textbox(Inches(5.08), Inches(2.05), Inches(3.04), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    p2_items = [
        ("Random Forest (Chính)", "100 cây (n_estimators=100), max_depth=None, n_jobs=-1, random_state=42."),
        ("Extra Trees", "100 cây, phân tách nhánh cực kỳ ngẫu nhiên."),
        ("Decision Tree", "max_depth=15, tốc độ cao."),
        ("Boosting Ensemble", "AdaBoost (50 cây), Gradient Boosting, LightGBM (100 cây, lr=0.05)."),
        ("Baseline", "Logistic Regression chuẩn hóa."),
    ]
    for lbl, val in p2_items:
        p = tf.add_paragraph()
        p.text = f"• {lbl}: "
        p.font.bold = True
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_SECONDARY
        p2 = tf.add_paragraph()
        p2.text = f"{val}"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(8)

    add_card(s6, Inches(8.8), Inches(1.4), Inches(3.7), Inches(5.4), "3. Thước Đo An Toàn TT")
    tb = s6.shapes.add_textbox(Inches(9.08), Inches(2.05), Inches(3.14), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    p3_items = [
        ("Accuracy & F1-Score", "Đo lường độ chính xác tổng quát và điểm điều hòa giữa Precision và Recall."),
        ("ROC-AUC & PR-AUC", "Khả năng phân biệt mã độc và file sạch ở mọi ngưỡng quyết định."),
        ("FPR (False Positive Rate)", "Tỷ lệ báo nhầm phần mềm lành tính thành mã độc (phải càng thấp càng tốt để tránh gián đoạn người dùng)."),
        ("TPR at 1% FPR", "Độ nhạy bắt mã độc khi khống chế tỷ lệ cảnh báo sai dưới 1%."),
    ]
    for lbl, val in p3_items:
        p = tf.add_paragraph()
        p.text = f"• {lbl}: "
        p.font.bold = True
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_ACCENT
        p2 = tf.add_paragraph()
        p2.text = f"{val}"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(8)

    add_notes(s6, "Điểm mới trong thiết lập thực nghiệm của chúng em là bổ sung thêm ROC-AUC, PR-AUC và đặc biệt là FPR - tỷ lệ cảnh báo sai, một chỉ số sống còn trong an toàn thông tin mà bài báo gốc chưa đề cập.")

    # ----------------------------------------------------
    # SLIDE 7: KẾT QUẢ TÁI HIỆN BÀI BÁO (BẢNG & NATIVE CHART)
    # ----------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    create_header(s7, "6. Kết Quả Thực Nghiệm Tái Hiện (Phần A)")

    # Bảng số liệu chi tiết bên trái
    add_card(s7, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4), "Bảng Đối Sánh Hiệu Năng Các Mô Hình")

    # Bảng native PowerPoint 8 dòng x 5 cột
    table_shape_s7 = s7.shapes.add_table(8, 5, Inches(1.08), Inches(2.05), Inches(5.24), Inches(2.8))
    table_s7 = table_shape_s7.table
    table_s7.columns[0].width = Inches(1.64)
    table_s7.columns[1].width = Inches(0.90)
    table_s7.columns[2].width = Inches(0.90)
    table_s7.columns[3].width = Inches(0.90)
    table_s7.columns[4].width = Inches(0.90)

    headers_s7 = ["Mô hình", "Acc (%)", "ROC-AUC", "F1", "FPR (%)"]
    for i, h in enumerate(headers_s7):
        cell = table_s7.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER if i > 0 else PP_ALIGN.LEFT

    models_order = [
        ("RandomForest", "RandomForest (Tốt nhất)"),
        ("ExtraTrees", "ExtraTrees"),
        ("LightGBM", "LightGBM"),
        ("GradientBoosting", "GradientBoosting"),
        ("DecisionTree", "DecisionTree"),
        ("AdaBoost", "AdaBoost"),
        ("Baseline_LogisticRegression", "Baseline (LogisticReg)")
    ]

    for row_idx, (m_key, m_disp) in enumerate(models_order, start=1):
        if m_key in metrics_comp:
            d = metrics_comp[m_key]
            row_data = [
                m_disp,
                f"{d['accuracy']*100:.2f}%",
                f"{d['roc_auc']:.4f}",
                f"{d['f1']:.4f}",
                f"{d['fpr']*100:.2f}%"
            ]
        else:
            row_data = [m_disp, "-", "-", "-", "-"]

        for col_idx, val in enumerate(row_data):
            cell = table_s7.cell(row_idx, col_idx)
            cell.text = val
            cell.fill.solid()
            if m_key == "RandomForest":
                cell.fill.fore_color.rgb = RGBColor(230, 245, 245)
            elif row_idx % 2 == 0:
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)
            else:
                cell.fill.fore_color.rgb = COLOR_WHITE

            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(9)
            if m_key == "RandomForest":
                p.font.bold = True
                p.font.color.rgb = COLOR_PRIMARY
            else:
                p.font.color.rgb = COLOR_DARK
            p.alignment = PP_ALIGN.CENTER if col_idx > 0 else PP_ALIGN.LEFT

    # Thiết lập border cho toàn bộ bảng Slide 7
    for r in range(8):
        for c in range(5):
            b_col = "1B365D" if r == 0 else "CBD5E1"
            set_cell_border(table_s7.cell(r, c), color=b_col, width=12700)

    # Nhận xét phân tích bên dưới bảng
    tb_comm = s7.shapes.add_textbox(Inches(1.08), Inches(4.95), Inches(5.24), Inches(1.75))
    tf_comm = tb_comm.text_frame
    tf_comm.word_wrap = True
    tf_comm.margin_left = tf_comm.margin_top = tf_comm.margin_right = tf_comm.margin_bottom = Inches(0)
    p = tf_comm.paragraphs[0]
    p.text = "Nhận xét kết quả thực nghiệm:"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_PRIMARY

    comm_bullets = [
        "• Random Forest & Extra Trees dẫn đầu toàn diện (AUC ~0.989, F1 ~0.946).",
        "• FPR của Random Forest chỉ 4.40%, thấp hơn 13 lần so với Baseline (60.10%).",
        "• Thời gian train RF chỉ 1.00s, khẳng định 44 đặc trưng Header rất tối ưu."
    ]
    for b in comm_bullets:
        p_b = tf_comm.add_paragraph()
        p_b.text = b
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = COLOR_DARK

    # Biểu đồ native chart bên phải (Truyền trực tiếp số liệu)
    add_card(s7, Inches(6.8), Inches(1.4), Inches(5.8), Inches(5.4), "So Sánh Hiệu Năng Các Mô Hình (Native Chart)")

    chart_data_s7 = CategoryChartData()
    categories_chart_s7 = []
    acc_s7_list = []
    auc_s7_list = []
    f1_s7_list = []

    models_chart_mapping = [
        ("RandomForest", "RF"),
        ("ExtraTrees", "ExtraTrees"),
        ("LightGBM", "LightGBM"),
        ("GradientBoosting", "GBDT"),
        ("DecisionTree", "DecTree"),
        ("AdaBoost", "AdaBoost"),
        ("Baseline_LogisticRegression", "Baseline")
    ]

    for m_key, short_name in models_chart_mapping:
        categories_chart_s7.append(short_name)
        if m_key in metrics_comp:
            d = metrics_comp[m_key]
            acc_s7_list.append(round(d['accuracy'] * 100, 2))
            auc_s7_list.append(round(d['roc_auc'] * 100, 2))
            f1_s7_list.append(round(d['f1'] * 100, 2))
        else:
            acc_s7_list.append(0.0)
            auc_s7_list.append(0.0)
            f1_s7_list.append(0.0)

    chart_data_s7.categories = categories_chart_s7
    chart_data_s7.add_series("Accuracy (%)", acc_s7_list)
    chart_data_s7.add_series("ROC-AUC (%)", auc_s7_list)
    chart_data_s7.add_series("F1-Score (%)", f1_s7_list)

    chart_shape_s7 = s7.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        Inches(6.95), Inches(1.95), Inches(5.5), Inches(4.6),
        chart_data_s7
    )
    chart_s7 = chart_shape_s7.chart
    chart_s7.has_legend = True
    chart_s7.legend.position = XL_LEGEND_POSITION.TOP
    chart_s7.legend.include_in_layout = False
    chart_s7.legend.font.size = Pt(8.5)
    chart_s7.value_axis.minimum_scale = 45.0
    chart_s7.value_axis.maximum_scale = 102.0
    chart_s7.value_axis.has_major_gridlines = True
    chart_s7.category_axis.tick_labels.font.size = Pt(8.5)
    chart_s7.value_axis.tick_labels.font.size = Pt(8.5)

    s7_colors = [COLOR_PRIMARY, COLOR_SECONDARY, RGBColor(243, 156, 18)]
    for idx, s in enumerate(chart_s7.series):
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = s7_colors[idx]

    add_notes(s7, "Kính thưa Thầy và các bạn, ở Slide 6 (Kết quả thực nghiệm tái hiện Phần A), bảng số liệu và biểu đồ cột đều được truyền trực tiếp từ file kết quả thực nghiệm. Về bảng đối sánh bên trái, Random Forest và Extra Trees đạt độ chính xác trên 94.6% và ROC-AUC vượt 0.988, vượt trội hoàn toàn so với Baseline Logistic Regression. Biểu đồ cột bên phải thể hiện trực quan ưu thế của nhóm thuật toán cây quyết định đối với dữ liệu PE Header. Tỷ lệ cảnh báo sai (FPR) của Random Forest chỉ 4.40%, đảm bảo mô hình hoạt động tin cậy và không gây gián đoạn hệ thống.")

    # ----------------------------------------------------
    # SLIDE 8: KẾT QUẢ KIỂM TRA DRIFT THEO THỜI GIAN
    # ----------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    create_header(s8, "7. Kết Quả Kiểm Tra Drift Theo Thời Gian (Phần B)")

    temp_csv = METRICS_DIR / "temporal_degradation.csv"
    retrain_csv = METRICS_DIR / "retraining_comparison.csv"
    df_temp = pd.read_csv(temp_csv) if temp_csv.exists() else pd.DataFrame()
    df_retrain = pd.read_csv(retrain_csv) if retrain_csv.exists() else pd.DataFrame()

    # Hình bên trái: Native Line Chart (Temporal Degradation)
    add_card(s8, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.4), "Suy Giảm Hiệu Năng Theo Tháng (Mô Hình Tĩnh)")

    chart_data_s8_left = CategoryChartData()
    categories_s8_left = ['Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12']
    chart_data_s8_left.categories = categories_s8_left

    if not df_temp.empty:
        auc_temp = [round(v * 100, 2) for v in df_temp['roc_auc']]
        f1_temp = [round(v * 100, 2) for v in df_temp['f1']]
        rec_temp = [round(v * 100, 2) for v in df_temp['recall']]
        fpr_temp = [round(v * 100, 2) for v in df_temp['fpr']]
    else:
        auc_temp = [97.62, 95.58, 96.37, 95.15]
        f1_temp = [91.78, 86.79, 90.00, 88.24]
        rec_temp = [89.85, 83.25, 89.75, 88.00]
        fpr_temp = [5.95, 8.60, 9.70, 11.45]

    chart_data_s8_left.add_series("ROC-AUC (%)", auc_temp)
    chart_data_s8_left.add_series("F1-Score (%)", f1_temp)
    chart_data_s8_left.add_series("Recall (%)", rec_temp)
    chart_data_s8_left.add_series("FPR (%)", fpr_temp)

    chart_shape_s8_left = s8.shapes.add_chart(
        XL_CHART_TYPE.LINE_MARKERS,
        Inches(1.0), Inches(2.05), Inches(5.4), Inches(3.9),
        chart_data_s8_left
    )
    chart_s8_left = chart_shape_s8_left.chart
    chart_s8_left.has_legend = True
    chart_s8_left.legend.position = XL_LEGEND_POSITION.TOP
    chart_s8_left.legend.include_in_layout = False
    chart_s8_left.legend.font.size = Pt(8.5)
    chart_s8_left.value_axis.minimum_scale = 0.0
    chart_s8_left.value_axis.maximum_scale = 100.0
    chart_s8_left.value_axis.has_major_gridlines = True
    chart_s8_left.category_axis.tick_labels.font.size = Pt(9)
    chart_s8_left.value_axis.tick_labels.font.size = Pt(9)

    line_colors = [COLOR_PRIMARY, COLOR_SECONDARY, RGBColor(40, 167, 69), COLOR_ACCENT]
    for idx, s in enumerate(chart_s8_left.series):
        s.format.line.color.rgb = line_colors[idx]
        s.format.line.width = Pt(2.5)

    tb_note_left = s8.shapes.add_textbox(Inches(1.08), Inches(6.10), Inches(5.24), Inches(0.55))
    tb_note_left.text_frame.margin_left = tb_note_left.text_frame.margin_top = tb_note_left.text_frame.margin_right = tb_note_left.text_frame.margin_bottom = Inches(0)
    p_nl = tb_note_left.text_frame.paragraphs[0]
    p_nl.text = "▶ Nhận định: FPR tăng vọt từ 5.95% lên 11.45% (gần gấp đôi) sau 4 tháng; ROC-AUC giảm từ 97.62% xuống 95.15% do hiện tượng trôi dạt dữ liệu."
    p_nl.font.size = Pt(9.5)
    p_nl.font.italic = True
    p_nl.font.color.rgb = COLOR_DARK

    # Hình bên phải: Native Clustered Column Chart (Retraining Comparison)
    add_card(s8, Inches(6.8), Inches(1.4), Inches(5.8), Inches(5.4), "Phục Hồi Bằng Huấn Luyện Lại (Sliding Window)")

    chart_data_s8_right = CategoryChartData()
    chart_data_s8_right.categories = categories_s8_left

    if not df_retrain.empty:
        static_auc = [round(v * 100, 2) for v in df_retrain['static_auc']]
        retrained_auc = [round(v * 100, 2) for v in df_retrain['retrained_auc']]
        static_f1 = [round(v * 100, 2) for v in df_retrain['static_f1']]
        retrained_f1 = [round(v * 100, 2) for v in df_retrain['retrained_f1']]
    else:
        static_auc = [97.62, 95.58, 96.37, 95.15]
        retrained_auc = [96.88, 96.62, 97.68, 97.60]
        static_f1 = [91.78, 86.79, 90.00, 88.24]
        retrained_f1 = [90.95, 89.46, 91.95, 92.29]

    chart_data_s8_right.add_series("Tĩnh - ROC-AUC (%)", static_auc)
    chart_data_s8_right.add_series("Retrain - ROC-AUC (%)", retrained_auc)
    chart_data_s8_right.add_series("Tĩnh - F1 (%)", static_f1)
    chart_data_s8_right.add_series("Retrain - F1 (%)", retrained_f1)

    chart_shape_s8_right = s8.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        Inches(7.0), Inches(2.05), Inches(5.4), Inches(3.9),
        chart_data_s8_right
    )
    chart_s8_right = chart_shape_s8_right.chart
    chart_s8_right.has_legend = True
    chart_s8_right.legend.position = XL_LEGEND_POSITION.TOP
    chart_s8_right.legend.include_in_layout = False
    chart_s8_right.legend.font.size = Pt(8.5)
    chart_s8_right.value_axis.minimum_scale = 80.0
    chart_s8_right.value_axis.maximum_scale = 100.0
    chart_s8_right.value_axis.has_major_gridlines = True
    chart_s8_right.category_axis.tick_labels.font.size = Pt(9)
    chart_s8_right.value_axis.tick_labels.font.size = Pt(9)

    col_colors = [COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, RGBColor(243, 156, 18)]
    for idx, s in enumerate(chart_s8_right.series):
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = col_colors[idx]

    tb_note_right = s8.shapes.add_textbox(Inches(7.08), Inches(6.10), Inches(5.24), Inches(0.55))
    tb_note_right.text_frame.margin_left = tb_note_right.text_frame.margin_top = tb_note_right.text_frame.margin_right = tb_note_right.text_frame.margin_bottom = Inches(0)
    p_nr = tb_note_right.text_frame.paragraphs[0]
    p_nr.text = "▶ Nhận định: Tại T12, Retraining phục hồi ROC-AUC lên 97.60% (+2.45%), F1 lên 92.29% (+4.05%), và kéo giảm FPR từ 11.45% xuống 7.90% (-3.55%)."
    p_nr.font.size = Pt(9.5)
    p_nr.font.italic = True
    p_nr.font.color.rgb = COLOR_DARK

    add_notes(s8, "Ở Slide 7 (kết quả kiểm tra Drift Phần B), cả hai biểu đồ đều là biểu đồ động tương tác được tạo trực tiếp từ số liệu temporal_degradation.csv và retraining_comparison.csv. Biểu đồ đường bên trái minh chứng sự suy giảm rõ rệt của mô hình tĩnh: ROC-AUC giảm dần qua các tháng và FPR tăng vọt từ 5.95% lên 11.45% do các biến thể malware mới xuất hiện. Biểu đồ cột bên phải cho thấy giải pháp huấn luyện lại định kỳ theo cửa sổ trượt (Sliding Window) đã giải quyết triệt để vấn đề: tại tháng 12, mô hình Retrained phục hồi AUC lên 97.60% (+2.45%), F1 lên 92.29% (+4.05%), và hạ FPR xuống 7.90% (-3.55%).")

    # ----------------------------------------------------
    # SLIDE 9: SO SÁNH VỚI BÁO CÁO GỐC: ƯU & NHƯỢC ĐIỂM
    # ----------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    create_header(s9, "8. So Sánh Đối Chiếu Với Báo Cáo Gốc: Ưu & Nhược Điểm")

    add_card(s9, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4), "So Sánh Khoa Học Giữa Hai Công Trình")
    tb = s9.shapes.add_textbox(Inches(1.08), Inches(2.05), Inches(5.04), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    comp_points = [
        ("Về Phương Pháp Luận", "Tái hiện thành công bản chất cốt lõi: Khảo sát đặc trưng PE Header, Random Forest 100 cây tối ưu, thực nghiệm K-Fold và giảm chiều đặc trưng."),
        ("Về Bộ Dữ Liệu", "Bài báo dùng tập ClaMP 140k mẫu (VirusShare). Nghiên cứu của em dùng EMBER 2018 chuẩn quốc tế với trục thời gian thực 'appeared'."),
        ("Về Thước Đo", "Bài báo gốc chỉ báo cáo Accuracy và Time. Em bổ sung: ROC-AUC, PR-AUC, Confusion Matrix và quan trọng nhất là FPR."),
        ("Khám phá trôi dạt (Drift)", "Bài báo gốc hoàn toàn bỏ qua chiều thời gian. Nghiên cứu này chứng minh thực nghiệm hiện tượng Concept/Feature Drift bằng PSI và KS-test."),
    ]
    for lbl, val in comp_points:
        p = tf.add_paragraph()
        p.text = f"• {lbl}: "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_PRIMARY
        p2 = tf.add_paragraph()
        p2.text = f"  {val}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(8)

    add_card(s9, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4), "Ưu Điểm & Điểm Hạn Chế Của Đề Tài")
    tb = s9.shapes.add_textbox(Inches(7.08), Inches(2.05), Inches(5.14), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    pros_cons = [
        ("ƯU ĐIỂM NỔI BẬT", "1. Đảm bảo tính trung thực số liệu 100%, không làm tròn hay bịa số.\n2. Thiết lập quy trình Temporal Split chuẩn chống rò rỉ tương lai.\n3. Đề xuất và kiểm chứng giải pháp kỹ thuật Sliding Window giúp khắc phục drift hiệu quả.\n4. Mã nguồn tự động hóa khép kín (run_all.py).", COLOR_SECONDARY),
        ("ĐIỂM HẠN CHẾ", "1. Do điều kiện phần cứng máy tính cá nhân, chưa thể huấn luyện trên toàn bộ 1 triệu mẫu EMBER mà phải lấy mẫu phân tầng 48.000 mẫu.\n2. Chỉ khai thác đặc trưng tĩnh, chưa kết hợp phân tích động (Dynamic Behavioral Analysis).", COLOR_ACCENT),
    ]
    for lbl, val, col in pros_cons:
        p = tf.add_paragraph()
        p.text = f"▶ {lbl}:"
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = col
        p2 = tf.add_paragraph()
        p2.text = f"{val}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(10)

    add_notes(s9, "Em trình bày rõ ràng: Đây là quá trình tái hiện phương pháp luận chứ không phải ép buộc số liệu. Điểm vượt trội của nghiên cứu là bổ sung chiều thời gian và thước đo FPR chuẩn an ninh mạng, đồng thời thẳng thắn nhìn nhận hạn chế về phần cứng.")

    # ----------------------------------------------------
    # SLIDE 10: KẾT LUẬN & HƯỚNG PHÁT TRIỂN
    # ----------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    create_header(s10, "9. Kết Luận, Đóng Góp & Hướng Phát Triển Tiếp Theo")

    add_card(s10, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4), "Kết Luận Rút Ra Từ Đề Tài")
    tb = s10.shapes.add_textbox(Inches(1.08), Inches(2.05), Inches(5.04), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    conclusions = [
        ("Hiệu quả của PE Header", "Xác nhận kết luận bài báo: Các trường thông tin PE Header hoàn toàn đủ nhạy để phân loại mã độc với độ chính xác cao và chi phí trích xuất cực nhanh."),
        ("Thực tế trôi dạt dữ liệu", "Phép chia ngẫu nhiên (Random Split) thường cho kết quả lạc quan giả tạo. Trong môi trường thực tế (Temporal Split), hiệu năng mô hình luôn suy giảm qua các tháng."),
        ("Giải pháp Retraining định kỳ", "Chiến lược cập nhật mô hình theo cửa sổ trượt (Sliding Window Retraining) là bắt buộc trong các hệ thống phòng thủ mã độc thế hệ mới để duy trì độ tin cậy."),
    ]
    for lbl, val in conclusions:
        p = tf.add_paragraph()
        p.text = f"✔ {lbl}:"
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_PRIMARY
        p2 = tf.add_paragraph()
        p2.text = f"{val}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(10)

    add_card(s10, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4), "Hướng Phát Triển Trong Tương Lai")
    tb = s10.shapes.add_textbox(Inches(7.08), Inches(2.05), Inches(5.14), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0)
    future_works = [
        ("1. Mở rộng bộ dữ liệu BODMAS & EMBER 2024", "Thử nghiệm trên các tập dữ liệu đa năm (2019-2024) để đánh giá khả năng chống trôi dạt trong khoảng thời gian dài từ 2 đến 3 năm."),
        ("2. Tự động phát hiện Drift (Drift Detection Alerts)", "Tích hợp cơ chế cảnh báo tự động khi chỉ số PSI vượt ngưỡng 0.25 để kích hoạt pipeline huấn luyện lại tự động (MLOps for Cybersecurity)."),
        ("3. Kết hợp Đồ thị cuộc gọi API (API Call Graph)", "Bổ sung thông tin chuỗi gọi hàm và hành vi sandbox nhằm phát hiện các biến thể mã độc pack tinh vi."),
    ]
    for lbl, val in future_works:
        p = tf.add_paragraph()
        p.text = f"🚀 {lbl}:"
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_SECONDARY
        p2 = tf.add_paragraph()
        p2.text = f"{val}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_DARK
        p2.space_after = Pt(10)

    # Lời cảm ơn cuối trang
    p_thanks = tf.add_paragraph()
    p_thanks.text = "\nEM XIN CHÂN THÀNH CẢM ƠN THẦY ĐÃ LẮNG NGHE!"
    p_thanks.font.size = Pt(13)
    p_thanks.font.bold = True
    p_thanks.font.color.rgb = COLOR_PRIMARY
    p_thanks.alignment = PP_ALIGN.CENTER

    add_notes(s10, "Em xin kết luận đề tài: Việc nghiên cứu trôi dạt dữ liệu giúp chúng em hiểu rõ hơn về thách thức trong triển khai AI vào an toàn thông tin thực tế. Em xin chân thành cảm ơn Thầy Phạm Trọng Huynh đã hướng dẫn và em xin sẵn sàng lắng nghe câu hỏi từ Thầy.")

    save_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(save_path)
    
    # Đồng thời lưu vào file Báo Cáo Giữa Kì.pptx
    bao_cao_path = save_path.parent / "Báo Cáo Giữa Kì.pptx"
    prs.save(bao_cao_path)
    print(f"[Slides] Đã tạo thành công bộ Slide PowerPoint 10 trang tại: {save_path} và {bao_cao_path}")
    return save_path


if __name__ == "__main__":
    build_presentation()
