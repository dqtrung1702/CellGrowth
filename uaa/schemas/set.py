from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SetListRequest(BaseModel):
    SetName: Optional[str] = None
    Services: Optional[str] = None
    SetCode: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class AddSetRequest(BaseModel):
    SetName: str
    Services: str
    SetCode: str

    model_config = ConfigDict(extra="allow")


class UpdateSetRequest(BaseModel):
    SetId: int
    SetName: Optional[str] = None
    Services: Optional[str] = None
    SetCode: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class DeleteSetRequest(BaseModel):
    SetId: Optional[int] = None
    id: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class DatasetBySetRequest(BaseModel):
    SetId: int
    model_config = ConfigDict(extra="allow")


class UpdateDatasetBySetRequest(BaseModel):
    SetId: int
    Data: List[dict] = []

    model_config = ConfigDict(extra="allow")
