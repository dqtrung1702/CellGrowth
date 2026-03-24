from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class URLByPermissionRequest(BaseModel):
    PermissionId: int
    model_config = ConfigDict(extra="allow")


class URLByPermissionListRequest(BaseModel):
    PermissionList: List[int | str] = []
    model_config = ConfigDict(extra="allow")


class PageByUserRequest(BaseModel):
    UserId: int
    model_config = ConfigDict(extra="allow")
