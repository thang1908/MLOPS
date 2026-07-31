# -*- coding: utf-8 -*-

import csv
from pathlib import Path
# -*- coding: utf-8 -*-
# Batch 1: Thẻ xe & V-SmartParking (24 cases)

# -*- coding: utf-8 -*-
# Batch 8a: Khác (Other) - part 1 (18 cases)

batch8a = [
{
"feedback": "CD báo căn 3202 mở cửa chiên rán, mùi thức ăn bay khắp hành lang, đề nghị BQL nhắc nhở hộ đó đóng cửa khi nấu ăn.\n1102 chị Lan",
"sentiment": "Tiêu cực", "cause_group": "Khác", "severity": "Thấp",
"journey": "Sinh sống", "nps": None, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Ngắn", "tone": "Ghi chú tổng đài, khách quan"
},
{
"feedback": "Kính gửi Ban Quản lý, tôi phát hiện vết nứt dài khoảng 40cm chạy dọc theo góc tường phòng khách nhà tôi, xuất hiện khoảng 2 tuần nay và có dấu hiệu lan rộng thêm. Tôi lo ngại đây có thể là vấn đề kết cấu chứ không đơn thuần là nứt sơn bề mặt. Đề nghị bộ phận kỹ thuật xuống khảo sát và đánh giá mức độ, đồng thời cho biết đây có thuộc diện bảo hành công trình hay không vì căn hộ tôi mới nhận bàn giao được 8 tháng.",
"sentiment": "Tiêu cực", "cause_group": "Khác", "severity": "Nghiêm trọng",
"journey": "Nhận nhà", "nps": 3, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Trung bình", "length_cat": "Dài", "tone": "Trang trọng, lo lắng về kết cấu"
},
{
"feedback": "CD báo căn trên thi công gây ồn liên tục, CD đã báo rất nhiều lần rồi, căn đó cứ thi công vào sáng sớm, đến giờ vẫn còn tiếng khoan đục. CD yêu cầu bên AN và BQL lên làm việc lại, nếu không giải quyết được CD sẽ báo lên chính quyền địa phương.\n2290",
"sentiment": "Tiêu cực", "cause_group": "Khác", "severity": "Trung bình",
"journey": "Sinh sống", "nps": None, "csat": 1, "ces": 1, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Trung bình", "tone": "Ghi chú tổng đài, có đe doạ leo thang"
},
{
"feedback": "Phí dịch vụ quản lý tháng này của căn hộ tôi tăng thêm 8% so với tháng trước mà không thấy có thông báo điều chỉnh biểu phí nào gửi đến cư dân trước đó. Tôi đề nghị Ban Quản lý cung cấp văn bản chính thức về căn cứ điều chỉnh phí, thời điểm áp dụng và có thông báo rộng rãi hơn cho toàn bộ cư dân trong các lần điều chỉnh sau.",
"sentiment": "Tiêu cực", "cause_group": "Khác", "severity": "Trung bình",
"journey": "Sinh sống", "nps": 3, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Trung bình", "length_cat": "Trung bình", "tone": "Trang trọng, yêu cầu minh bạch"
},
{
"feedback": "Khách hàng vừa làm việc với CSKH toà L2, không hài lòng sau nhiều lần trao đổi về thái độ và kỹ năng xử lý của nhân viên, hẹn gặp trực tiếp nhưng bạn CSKH liên tục xem đồng hồ và nói phải về sớm đón con giữa buổi làm việc. KH đề nghị trưởng bộ phận trực tiếp làm việc lại và xem xét luân chuyển nhân sự phụ trách toà.",
"sentiment": "Tiêu cực", "cause_group": "Khác", "severity": "Trung bình",
"journey": "Sinh sống", "nps": 2, "csat": 1, "ces": None, "needs_review": "Không",
"difficulty": "Trung bình", "length_cat": "Trung bình", "tone": "Ghi chú tổng đài, bức xúc về thái độ nhân viên"
},
{
"feedback": "Mảng cỏ và bồn hoa trước sảnh toà nhà em được chăm sóc rất đẹp, tuần nào cũng thấy đội làm vườn cắt tỉa gọn gàng, đi ngang qua thấy thích mắt hẳn.",
"sentiment": "Tích cực", "cause_group": "Khác", "severity": "Thấp",
"journey": "Sinh sống", "nps": 9, "csat": 5, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Ngắn", "tone": "Vui vẻ, khen ngợi"
},
{
"feedback": "Bình chữa cháy đặt ở hành lang tầng 9 toà nhà em nhìn có vẻ cũ, kim đồng hồ áp suất chỉ về vạch đỏ chứ không phải vạch xanh như bình thường, không biết có còn dùng được không, mong kỹ thuật kiểm tra thay mới nếu cần vì đây là vấn đề an toàn cháy nổ.",
"sentiment": "Tiêu cực", "cause_group": "Khác", "severity": "Nghiêm trọng",
"journey": "Sinh sống", "nps": None, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Trung bình", "tone": "Lo lắng, nhấn mạnh an toàn PCCC"
},
{
"feedback": "cho hỏi lịch thu gom rác của tòa mình là mấy giờ vậy ạ, em hay đi làm sớm nên muốn canh giờ mang rác xuống cho đúng",
"sentiment": "Trung tính", "cause_group": "Khác", "severity": "Thấp",
"journey": "Dùng tiện ích + Dịch vụ số", "nps": None, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Ngắn", "tone": "Lịch sự, hỏi thông tin"
},
{
"feedback": "Ồn quá",
"sentiment": "Tiêu cực", "cause_group": "Khác", "severity": "Trung bình",
"journey": None, "nps": None, "csat": None, "ces": None, "needs_review": "Có",
"difficulty": "Khó", "length_cat": "Ngắn", "tone": "Cực ngắn, không rõ nguồn ồn hay vị trí"
},
{
"feedback": "Khu vực bể cá cảnh sinh thái ở sảnh chờ dạo này có mùi hơi khó chịu, nước có vẻ không được thay thường xuyên, không biết BQL có lịch vệ sinh định kỳ khu vực này không ạ.",
"sentiment": "Trung tính", "cause_group": "Khác", "severity": "Thấp",
"journey": "Sinh sống", "nps": None, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Ngắn", "tone": "Nhận xét nhẹ nhàng"
},
{
"feedback": "Kính gửi Ban Quản lý. Tôi là chủ sở hữu căn hộ, hiện đang làm thủ tục cho thuê lại căn hộ và cần xin xác nhận tình trạng cư trú cùng bản sao sổ hồng có đóng dấu treo của Ban Quản lý để bổ sung hồ sơ công chứng hợp đồng thuê. Xin hỏi thủ tục này cần chuẩn bị giấy tờ gì và thời gian xử lý thông thường là bao lâu?",
"sentiment": "Trung tính", "cause_group": "Khác", "severity": "Thấp",
"journey": "Dùng tiện ích + Dịch vụ số", "nps": None, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Trung bình", "tone": "Trang trọng, hỏi thủ tục hành chính"
},
{
"feedback": "Cầu trượt ở khu vui chơi trẻ em cạnh hồ điều hoà có một thanh chắn bị gỉ sét và lỏng ốc, con em chơi hôm qua suýt bị vấp vào đó, em thấy khá nguy hiểm cho trẻ nhỏ nên báo gấp để BQL kiểm tra sửa chữa hoặc rào chắn tạm khu vực đó lại trước khi có tai nạn xảy ra.",
"sentiment": "Tiêu cực", "cause_group": "Khác", "severity": "Nghiêm trọng",
"journey": "Dùng tiện ích + Dịch vụ số", "nps": None, "csat": 1, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Trung bình", "tone": "Lo lắng, cảnh báo an toàn trẻ em"
},
{
"feedback": "nhà em nuôi 1 bé mèo, tuần trước dắt xuống sân chơi thì bị bảo vệ nhắc là chó mèo phải có rọ mõm hoặc bế trên tay khi ra khu vực chung, e ko biết quy định này áp dụng cho cả mèo luôn à hay chỉ chó thôi ạ",
"sentiment": "Trung tính", "cause_group": "Khác", "severity": "Thấp",
"journey": "Dùng tiện ích + Dịch vụ số", "nps": None, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Trung bình", "length_cat": "Ngắn", "tone": "Teencode nhẹ, thắc mắc quy định"
},
{
"feedback": "Nước máy nhà em sáng nay chảy ra hơi đục và có mùi clo nồng hơn bình thường, không biết có phải do đường ống đang bảo trì không, mong được thông báo tình hình để gia đình chủ động dùng nước đóng chai tạm thời nếu cần.",
"sentiment": "Trung tính", "cause_group": "Khác", "severity": "Trung bình",
"journey": "Sinh sống", "nps": None, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Ngắn", "tone": "Lo lắng nhẹ, cần thông tin"
},
{
"feedback": "căn bị mất điện, mới nhận bàn giao tuần trước",
"sentiment": "Trung tính", "cause_group": "Khác", "severity": "Trung bình",
"journey": "Nhận nhà", "nps": None, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Ngắn", "tone": "Ngắn gọn, báo sự cố"
},
{
"feedback": "Tôi thực sự cảm ơn Ban Quản lý và đội vệ sinh môi trường vì trong suốt hơn 2 năm sinh sống ở đây, khu vực công cộng lúc nào cũng sạch sẽ, thùng rác được thu gom đúng giờ, không hề có mùi hôi như một số khu đô thị khác tôi từng ở trước đây. Đây là một trong những lý do chính khiến gia đình tôi rất hài lòng và có ý định gắn bó lâu dài tại đây.",
"sentiment": "Tích cực", "cause_group": "Khác", "severity": "Thấp",
"journey": "Sinh sống", "nps": 10, "csat": 5, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Dài", "tone": "Trang trọng, rất hài lòng và gắn bó"
},
{
"feedback": "Muỗi ở khu vực hồ điều hoà dạo này nhiều quá, tối ra ngồi ghế đá là bị đốt liên tục, BQL có kế hoạch phun thuốc diệt muỗi định kỳ không ạ hay chỉ phun khi có phản ánh thôi?",
"sentiment": "Trung tính", "cause_group": "Khác", "severity": "Thấp",
"journey": "Sinh sống", "nps": None, "csat": None, "ces": None, "needs_review": "Không",
"difficulty": "Dễ", "length_cat": "Ngắn", "tone": "Than phiền nhẹ, hỏi thông tin"
},
{
"feedback": "Chất lượng dịch vụ",
"sentiment": "Trung tính", "cause_group": "Khác", "severity": "Trung bình",
"journey": None, "nps": None, "csat": None, "ces": None, "needs_review": "Có",
"difficulty": "Khó", "length_cat": "Ngắn", "tone": "Không rõ nội dung cụ thể"
},
]

def export_to_csv(data: list[dict], output_file: str) -> None:
    """
    Chuyển danh sách dictionary thành file CSV.

    Args:
        data: Danh sách dữ liệu cần xuất.
        output_file: Tên hoặc đường dẫn file CSV.
    """
    if not data:
        raise ValueError("Danh sách dữ liệu đang trống.")

    output_path = Path(output_file)

    # Tạo thư mục cha nếu chưa tồn tại
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Giữ nguyên thứ tự cột theo dictionary đầu tiên
    fieldnames = list(data[0].keys())

    with output_path.open(
        mode="w",
        encoding="utf-8-sig",  # Giúp Excel đọc đúng tiếng Việt
        newline=""
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_MINIMAL
        )

        writer.writeheader()

        for row in data:
            # Chuyển None thành chuỗi rỗng
            cleaned_row = {
                key: "" if value is None else value
                for key, value in row.items()
            }
            writer.writerow(cleaned_row)

    print(f"Đã xuất {len(data)} dòng dữ liệu.")
    print(f"File CSV: {output_path.resolve()}")


def export_to_excel(data: list[dict], output_file: str = "output/batch.xlsx") -> None:
    """
    Xuất trực tiếp danh sách dictionary thành file Excel (.xlsx).
    """
    import pandas as pd
    if not data:
        raise ValueError("Danh sách dữ liệu đang trống.")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(data)
    df.fillna("", inplace=True)
    df.to_excel(output_path, index=False, engine="openpyxl")

    print(f"Đã xuất {len(data)} dòng dữ liệu ra file Excel: {output_path.resolve()}")


def merge_all_to_excel(output_dir: str = "output", output_excel: str = "combined_all_batches.xlsx") -> None:
    """
    Gộp tất cả các file CSV/Excel trong thư mục output thành 1 file Excel (.xlsx).
    """
    import pandas as pd
    dir_path = Path(output_dir)
    excel_path = dir_path / output_excel

    csv_files = sorted(dir_path.glob("*.csv"))
    if not csv_files:
        print(f"Không tìm thấy file CSV nào trong {dir_path.resolve()}")
        return

    dfs = []
    for f in csv_files:
        df = pd.read_csv(f, encoding="utf-8-sig")
        dfs.append(df)
        print(f" - Đã đọc {len(df)} dòng từ {f.name}")

    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df.to_excel(excel_path, index=False, engine="openpyxl")
    print(f"==> Đã gộp tổng cộng {len(merged_df)} dòng vào file Excel: {excel_path.resolve()}")


if __name__ == "__main__":
    # Gộp tất cả các file trong thư mục output sang 1 file .xlsx
    merge_all_to_excel(output_dir="output", output_excel="combined_all_batches.xlsx")