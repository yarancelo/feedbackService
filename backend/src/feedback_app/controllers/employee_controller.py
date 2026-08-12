"""Employee directory endpoints (author picker source)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from feedback_app.core.dependencies import get_bitrix_client, get_current_admin, get_db, get_manual_author_service
from feedback_app.core.logging import get_logger
from feedback_app.integrations.bitrix_client import BitrixClient
from feedback_app.models.user import User
from feedback_app.schemas.employee import EmployeeOut
from feedback_app.services import employee_service
from feedback_app.services.manual_author_service import ManualAuthorService

logger = get_logger(__name__)
router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeOut])
def list_employees(client: BitrixClient = Depends(get_bitrix_client), manual: ManualAuthorService = Depends(get_manual_author_service)) -> list[EmployeeOut]:
    """Public: directory for the author dropdown (cached, from Bitrix or stub)."""
    employees = employee_service.list_employees(client)
    from feedback_app.integrations.bitrix_client import Employee
    employees.extend(Employee(bitrix_id=f"manual:{author.id}", full_name=author.full_name, position=author.position, company=author.company, department=author.department) for author in manual.list())
    return [EmployeeOut.model_validate(e) for e in employees]


@router.post("/sync", response_model=list[EmployeeOut])
def sync_employees(
    client: BitrixClient = Depends(get_bitrix_client),
    _admin: User = Depends(get_current_admin),
) -> list[EmployeeOut]:
    """Admin: force a refresh from Bitrix now."""
    logger.info("Admin triggered employee directory sync")
    employees = employee_service.list_employees(client, force=True)
    return [EmployeeOut.model_validate(e) for e in employees]
