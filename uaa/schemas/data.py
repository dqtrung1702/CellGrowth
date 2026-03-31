from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from config import Config


class DataSetByUserRequest(BaseModel):
    UserId: int
    model_config = ConfigDict(extra="allow")


class DatasetByPermissionRequest(BaseModel):
    PermissionId: int
    model_config = ConfigDict(extra="allow")


class PermissionInfoRequest(BaseModel):
    ids: List[int] = Field(default_factory=list)
    model_config = ConfigDict(extra="allow")


class AddPermissionRequest(BaseModel):
    Code: str
    PermissionType: str = "ROLE"
    Description: Optional[str] = None
    UrlList: List[dict | int | str] = Field(default_factory=list)
    DataSets: List[dict | int | str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class UpdatePermissionRequest(BaseModel):
    PermissionId: int
    Description: Optional[str] = None
    PermissionType: Optional[str] = None
    UrlList: List[dict | int | str] = Field(default_factory=list)
    DataSets: List[dict | int | str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class DeletePermissionRequest(BaseModel):
    id: int
    model_config = ConfigDict(extra="allow")


class PermissionListRequest(BaseModel):
    page: int = Field(default=Config.DEFAULT_PAGE, ge=1)
    page_size: int = Field(default=Config.DEFAULT_PAGE_SIZE, ge=1, le=Config.MAX_PAGE_SIZE)
    Code: Optional[str] = None
    PermissionType: Optional[str | list] = None

    model_config = ConfigDict(extra="allow")


class DataPermissionListRequest(BaseModel):
    page: int = Field(default=Config.DEFAULT_PAGE, ge=1)
    page_size: int = Field(default=Config.DEFAULT_PAGE_SIZE, ge=1, le=Config.MAX_PAGE_SIZE)
    Code: Optional[str] = None

    model_config = ConfigDict(extra="allow")
