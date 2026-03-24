from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from config import Config


class LoginRequest(BaseModel):
    UserName: str
    Password: str

    model_config = ConfigDict(extra="allow")


class RegisterRequest(BaseModel):
    UserName: str
    Password: str
    NameDisplay: Optional[str] = ""
    Roles: List[int] = Field(default_factory=list)
    RoleCodes: List[str] = Field(default_factory=list)
    DataPermissions: List[int] = Field(default_factory=list)
    DataPermissionCodes: List[str] = Field(default_factory=list)
    SetIds: List[int] = Field(default_factory=list)
    Reason: Optional[str] = None
    TtlHours: Optional[int] = None

    model_config = ConfigDict(extra="allow")
