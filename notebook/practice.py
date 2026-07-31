from __future__ import annotations

from datetime import datetime
from typing import Any

from prefect import flow, task
from prefect.logging import get_run_logger


@task(
    name="crawl-facebook-page",
    retries=2,
    retry_delay_seconds=2,
)
def crawl_page(
    page_number: int,
    fail_page: int = 0,
) -> list[dict[str, Any]]:
    """
    Giả lập crawl một trang dữ liệu.

    fail_page = 0:
        Không page nào lỗi.

    fail_page = 2:
        Page 2 luôn lỗi để kiểm tra retry.
    """
    logger = get_run_logger()

    logger.info(
        "Bắt đầu crawl page_number=%s",
        page_number,
    )

    if page_number == fail_page:
        raise ConnectionError(
            f"Giả lập mất kết nối tại page {page_number}"
        )

    posts = [
        {
            "post_id": f"page-{page_number}-post-1",
            "page_number": page_number,
            "content": f"Phản ánh ngập nước từ page {page_number}",
        },
        {
            "post_id": f"page-{page_number}-post-2",
            "page_number": page_number,
            "content": f"Phản ánh tiếng ồn từ page {page_number}",
        },
    ]

    logger.info(
        "Crawl page %s thành công: %s bài viết",
        page_number,
        len(posts),
    )

    return posts


@task(name="save-crawl-summary")
def save_summary(
    summary: dict[str, Any],
) -> None:
    """
    Hiện tại chỉ giả lập lưu kết quả.

    Sau này có thể thay bằng PostgreSQL.
    """
    logger = get_run_logger()
    logger.info("Lưu kết quả: %s", summary)


@flow(
    name="facebook-resident-feedback",
    log_prints=True,
)
def crawler_pipeline(
    page_count: int = 3,
    fail_page: int = 0,
) -> dict[str, Any]:
    """
    Crawl nhiều Facebook page và tổng hợp kết quả.

    Args:
        page_count:
            Số page dữ liệu cần crawl.

        fail_page:
            Page được chọn để giả lập lỗi.
            Giá trị 0 nghĩa là không giả lập lỗi.
    """
    logger = get_run_logger()

    if page_count <= 0:
        raise ValueError(
            "page_count phải lớn hơn 0"
        )

    if fail_page < 0:
        raise ValueError(
            "fail_page không được nhỏ hơn 0"
        )

    all_posts: list[dict[str, Any]] = []
    failed_pages: list[dict[str, Any]] = []

    for page_number in range(1, page_count + 1):
        # Lấy State để một page lỗi không làm flow dừng ngay.
        state = crawl_page(
            page_number=page_number,
            fail_page=fail_page,
            return_state=True,
        )

        if state.is_completed():
            posts = state.result()
            all_posts.extend(posts)

        else:
            error = state.result(
                raise_on_failure=False
            )

            failed_pages.append(
                {
                    "page_number": page_number,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                }
            )

            logger.error(
                "Page %s thất bại, tiếp tục page tiếp theo",
                page_number,
            )

    summary = {
        "run_time": datetime.now().isoformat(
            timespec="seconds"
        ),
        "requested_pages": page_count,
        "successful_pages": page_count - len(failed_pages),
        "failed_pages": len(failed_pages),
        "posts_collected": len(all_posts),
        "failures": failed_pages,
    }

    save_summary(summary)

    logger.info(
        "Pipeline hoàn thành: %s",
        summary,
    )

    return summary


if __name__ == "__main__":
    crawler_pipeline.serve(
        name="facebook-crawler-local",

        # Chạy tự động mỗi 60 giây.
        interval=60,

        # Parameters mặc định của scheduled run.
        parameters={
            "page_count": 3,
            "fail_page": 0,
        },

        tags=[
            "crawler",
            "facebook",
            "lab",
        ],

        description=(
            "Lab Prefect deployment cho pipeline "
            "Facebook resident feedback crawler."
        ),

        # Khi nhấn Ctrl+C, schedule được pause.
        pause_on_shutdown=True,
    )