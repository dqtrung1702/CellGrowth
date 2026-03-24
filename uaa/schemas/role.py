from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from config import Config


class RoleListRequest(BaseModel):
    page: int = Field(default=Config.DEFAULT_PAGE, ge=1)
    page_size: int = Field(default=Config.DEFAULT_PAGE_SIZE, ge=1, le=Config.MAX_PAGE_SIZE)
    Code: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class RoleInfoRequest(BaseModel):
    id: int
    model_config = ConfigDict(extra="allow")


class AddRoleRequest(BaseModel):
    Code: str
    Description: Optional[str] = None
    Permission: List[int] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class UpdateRoleRequest(BaseModel):
    RoleId: int
    Description: Optional[str] = None
    Permission: List[int] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class DeleteRoleRequest(BaseModel):
    id: int
    model_config = ConfigDict(extra="allow")


class PermissionByRoleRequest(BaseModel):
    id: int
    model_config = ConfigDict(extra="allow")


class UserByRoleRequest(BaseModel):
    id: int
    model_config = ConfigDict(extra="allow")


class RoleByUserRequest(BaseModel):
    id: Optional[int] = None
    UserId: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class RolePermissionListRequest(BaseModel):
    page: int = Field(default=Config.DEFAULT_PAGE, ge=1)
    page_size: int = Field(default=Config.DEFAULT_PAGE_SIZE, ge=1, le=Config.MAX_PAGE_SIZE)
    Code: Optional[str] = None
    PermissionType: Optional[str | list] = None
    PermissionTypes: Optional[str | list] = None

    model_config = ConfigDict(extra="allow")


class RoleByPermissionRequest(BaseModel):
    id: int
    model_config = ConfigDict(extra="allow")
