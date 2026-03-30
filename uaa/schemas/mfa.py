from typing import Optional

from pydantic import BaseModel, ConfigDict


class EnrollTOTPRequest(BaseModel):
    UserId: Optional[int] = None
    model_config = ConfigDict(extra="allow")


class VerifyTOTPRequest(BaseModel):
    UserId: Optional[int] = None
    Code: str
    model_config = ConfigDict(extra="allow")


class DisableTOTPRequest(BaseModel):
    UserId: Optional[int] = None
    model_config = ConfigDict(extra="allow")
