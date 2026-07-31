# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

def merge_csv_to_excel(output_dir: str = "output", output_excel_name: str = "combined_all_batches.xlsx") -> None:
    """
    Đọc tất cả các file CSV trong thư mục output và gộp thành 1 file Excel (.xlsx) duy nhất.

    Args:
        output_dir: Đường dẫn thư mục chứa các file CSV cần gộp.
        output_excel_name: Tên file Excel đầu ra (.xlsx).
    """
    dir_path = Path(output_dir)
    excel_path = dir_path / output_excel_name

    if not dir_path.exists():
        print(f"Thư mục '{dir_path.resolve()}' không tồn tại.")
        return

    csv_files = sorted(dir_path.glob("*.csv"))

    if not csv_files:
        print(f"Không tìm thấy file CSV nào trong '{dir_path.resolve()}'.")
        return

    print(f"Tìm thấy {len(csv_files)} file CSV cần gộp:")

    dfs = []
    total_rows = 0

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding="utf-8-sig")
        except Exception:
            df = pd.read_csv(csv_file, encoding="utf-8")

        dfs.append(df)
        total_rows += len(df)
        print(f"   + Đọc {len(df)} dòng từ {csv_file.name}")

    merged_df = pd.concat(dfs, ignore_index=True)

    # Tạo thư mục nếu chưa tồn tại
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    # Xuất dữ liệu ra file Excel
    merged_df.to_excel(excel_path, index=False, engine="openpyxl")

    print("-" * 50)
    print(f"Đã gộp thành công tổng cộng {total_rows} dòng dữ liệu.")
    print(f"File Excel kết quả: {excel_path.resolve()}")


if __name__ == "__main__":
    merge_csv_to_excel(output_dir="output", output_excel_name="combined_all_batches.xlsx")
