from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: Optional[int] = None
    total_row: Optional[List[dict]] = Field(default=None, description="Giữ cấu trúc hiện tại: [{\"sum\": total}]")


class ResponseEnvelope(BaseModel, Generic[T]):
    """
    Chuẩn chung cho API:
    - status: OK/FAIL
    - message: mô tả lỗi/note
    - data: dữ liệu trả về (List hoặc object)
    - meta: thông tin phân trang / tổng
    """
    status: str = Field(default="OK", examples=["OK", "FAIL"])
    message: Optional[str] = None
    data: Optional[T] = None
    meta: Optional[PaginationMeta] = None
    actions: Optional[list] = Field(default=None, description="Dùng cho các thao tác approve/cancel, nếu có")

    class Config:
        populate_by_name = True
        extra = "allow"
