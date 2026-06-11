from pydantic import BaseModel
from typing import Optional


class JobOut(BaseModel):
    id: str
    filename: str
    status: str
    row_count_raw: Optional[int]
    row_count_clean: Optional[int]

    class Config:
        orm_mode = True
