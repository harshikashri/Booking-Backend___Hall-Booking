from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class FacilityCreate(BaseModel):
    name: str


class FacilityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime