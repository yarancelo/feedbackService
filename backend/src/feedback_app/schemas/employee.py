"""Employee view schema (directory entry for the author picker)."""
from pydantic import BaseModel, ConfigDict


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bitrix_id: str
    full_name: str
    position: str | None = None
    company: str | None = None
    department: str | None = None

class EmployeeSearchOut(BaseModel):
    bitrix_id: str
    full_name: str
