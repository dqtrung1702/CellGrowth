from pydantic import BaseModel, ConfigDict, Field
from config import Config


class Pagination(BaseModel):
    page: int = Field(default=Config.DEFAULT_PAGE, ge=1)
    page_size: int = Field(default=Config.DEFAULT_PAGE_SIZE, ge=1, le=Config.MAX_PAGE_SIZE)

    model_config = ConfigDict(extra="allow")
