"""Minimal public employee search and admin directory synchronization."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from feedback_app.core.dependencies import get_bitrix_client, get_current_admin, get_db
from feedback_app.core.logging import get_logger
from feedback_app.integrations.bitrix_client import BitrixClient
from feedback_app.models.manual_author import ManualAuthor
from feedback_app.models.user import User
from feedback_app.schemas.employee import EmployeeOut, EmployeeSearchOut
from feedback_app.services import employee_service

logger = get_logger(__name__)
router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("/search", response_model=list[EmployeeSearchOut])
def search_employees(q: str = Query(min_length=3, max_length=100), client: BitrixClient = Depends(get_bitrix_client), db: Session = Depends(get_db)) -> list[EmployeeSearchOut]:
    needle = q.strip().lower()
    matches = [EmployeeSearchOut(bitrix_id=item.bitrix_id, full_name=item.full_name) for item in employee_service.list_employees(client) if needle in item.full_name.lower()][:8]
    if len(matches) < 8:
        matches.extend(EmployeeSearchOut(bitrix_id=f"manual:{item.id}", full_name=item.full_name) for item in db.query(ManualAuthor).filter_by(is_active=True).order_by(ManualAuthor.full_name) if needle in item.full_name.lower())
    return matches[:8]

@router.post("/sync", response_model=list[EmployeeOut])
def sync_employees(client: BitrixClient = Depends(get_bitrix_client), _admin: User = Depends(get_current_admin)) -> list[EmployeeOut]:
    logger.info("Admin triggered employee directory sync")
    return [EmployeeOut.model_validate(item) for item in employee_service.list_employees(client, force=True)]
