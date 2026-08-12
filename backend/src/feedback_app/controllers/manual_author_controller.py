import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from feedback_app.core.dependencies import get_current_admin, get_db
from feedback_app.models.manual_author import ManualAuthor
from feedback_app.models.user import User
from feedback_app.schemas.employee import EmployeeOut

router = APIRouter(prefix='/manual-authors', tags=['manual-authors'])
@router.get('', response_model=list[EmployeeOut])
def list_manual(_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return [EmployeeOut(bitrix_id=f'manual:{item.id}', full_name=item.full_name, department=item.department, company=item.company, position=item.position) for item in db.query(ManualAuthor).filter_by(is_active=True).order_by(ManualAuthor.full_name)]
@router.post('', response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_manual(payload: dict, _admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    full_name = str(payload.get('full_name') or '').strip()
    if not full_name: raise HTTPException(422, 'Укажите ФИО.')
    item = db.query(ManualAuthor).filter_by(full_name=full_name).first()
    if item is None:
        item = ManualAuthor(full_name=full_name, department=payload.get('department'), company=payload.get('company'), position=payload.get('position'))
        db.add(item); db.flush(); db.refresh(item)
    return EmployeeOut(bitrix_id=f'manual:{item.id}', full_name=item.full_name, department=item.department, company=item.company, position=item.position)
@router.patch('/{author_id}', response_model=EmployeeOut)
def edit_manual(author_id: uuid.UUID, payload: dict, _admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    item = db.get(ManualAuthor, author_id)
    if item is None: raise HTTPException(404, 'Автор не найден.')
    for field in ('full_name','department','company','position'):
        if field in payload: setattr(item, field, str(payload[field]).strip() or None)
    if not item.full_name: raise HTTPException(422, 'Укажите ФИО.')
    db.flush(); db.refresh(item)
    return EmployeeOut(bitrix_id=f'manual:{item.id}', full_name=item.full_name, department=item.department, company=item.company, position=item.position)

@router.delete('/{author_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_manual(author_id: uuid.UUID, _admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Hide a manually confirmed author from the selectable local directory."""
    item = db.get(ManualAuthor, author_id)
    if item is None:
        raise HTTPException(404, 'Автор не найден.')
    item.is_active = False
    db.flush()
