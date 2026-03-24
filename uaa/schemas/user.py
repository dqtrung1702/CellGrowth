from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from config import Config


class UserListRequest(BaseModel):
    page: int = Field(default=Config.DEFAULT_PAGE, ge=1)
    page_size: int = Field(default=Config.DEFAULT_PAGE_SIZE, ge=1, le=Config.MAX_PAGE_SIZE)
    UserName: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class UserInfoRequest(BaseModel):
    id: int

    model_config = ConfigDict(extra="allow")


class UpdateUserRequest(BaseModel):
    id: int
    UserLocked: Optional[bool] = None
    Password: Optional[str] = None
    NameDisplay: Optional[str] = None
    DataPermission: Optional[int | str | None] = None

    model_config = ConfigDict(extra="allow")


class UpdateUserRoleRequest(BaseModel):
    UserId: int
    RoleList: List[int] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")
