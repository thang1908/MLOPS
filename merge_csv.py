# -*- coding: utf-8 -*-

import csv
from pathlib import Path

def merge_csv_files(output_dir: str = "output", merged_file_name: str = "combined_all_batches.csv") -> None:
    """
    Nối tất cả các file CSV trong thư mục output thành 1 file duy nhất.

    Args:
        output_dir: Đường dẫn thư mục chứa các file CSV cần nối.
        merged_file_name: Tên file kết quả sau khi nối.
    """
    dir_path = Path(output_dir)
    merged_path = dir_path / merged_file_name

    if not dir_path.exists():
        print(f"Thư mục '{dir_path.resolve()}' không tồn tại.")
        return

    # Lấy danh sách tất cả các file .csv ngoại trừ file đầu ra bị trùng
    csv_files = sorted([
        f for f in dir_path.glob("*.csv") 
        if f.name != merged_file_name
    ])

    if not csv_files:
        print(f"Không tìm thấy file CSV nào trong '{dir_path.resolve()}'.")
        return

    print(f"Tìm thấy {len(csv_files)} file CSV cần nối:")
    for f in csv_files:
        print(f" - {f.name}")

    header = None
    total_rows = 0

    with merged_path.open("w", encoding="utf-8-sig", newline="") as outfile:
        writer = None

        for csv_file in csv_files:
            with csv_file.open("r", encoding="utf-8-sig", newline="") as infile:
                reader = csv.reader(infile)
                file_header = next(reader, None)

                if file_header is None:
                    continue  # File rỗng

                # Đặt header từ file đầu tiên
                if header is None:
                    header = file_header
                    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(header)
                
                rows = list(reader)
                writer.writerows(rows)
                total_rows += len(rows)
                print(f"   + Nối {len(rows)} dòng từ {csv_file.name}")

    print("-" * 50)
    print(f"Đã gộp thành công tổng cộng {total_rows} dòng dữ liệu.")
    print(f"File kết quả: {merged_path.resolve()}")


if __name__ == "__main__":
    merge_csv_files(output_dir="output", merged_file_name="combined_all_batches.csv")
