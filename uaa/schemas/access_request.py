from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from config import Config


class AccessRequestCreate(BaseModel):
    Type: Optional[str] = Field(default="ROLE")
    Roles: Optional[List[int]] = None
    DataPermissions: Optional[List[int]] = None
    Reason: Optional[str] = None
    TtlHours: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class AccessRequestApprove(BaseModel):
    Note: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class AccessRequestReject(BaseModel):
    Note: Optional[str] = None
    Reason: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class AccessRequestListQuery(BaseModel):
    status: Optional[str] = None
    type: Optional[str] = None
    requester: Optional[str] = None
    created_from: Optional[str] = None  # YYYY-MM-DD
    created_to: Optional[str] = None    # YYYY-MM-DD
    page: int = Field(default=Config.DEFAULT_PAGE, ge=1)
    page_size: int = Field(default=Config.DEFAULT_PAGE_SIZE, ge=1, le=Config.MAX_PAGE_SIZE)

    model_config = ConfigDict(extra="allow")
