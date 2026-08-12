import uuid

from fastapi import APIRouter, Depends, status

from feedback_app.core.dependencies import get_category_service, get_current_admin
from feedback_app.models.user import User
from feedback_app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from feedback_app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(service: CategoryService = Depends(get_category_service)) -> list[CategoryOut]:
    return service.list(active_only=True)


@router.get("/manage", response_model=list[CategoryOut])
def list_all_categories(_admin: User = Depends(get_current_admin), service: CategoryService = Depends(get_category_service)) -> list[CategoryOut]:
    return service.list()


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, _admin: User = Depends(get_current_admin), service: CategoryService = Depends(get_category_service)) -> CategoryOut:
    return service.create(payload)


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(category_id: uuid.UUID, payload: CategoryUpdate, _admin: User = Depends(get_current_admin), service: CategoryService = Depends(get_category_service)) -> CategoryOut:
    return service.update(category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: uuid.UUID, _admin: User = Depends(get_current_admin), service: CategoryService = Depends(get_category_service)) -> None:
    service.delete(category_id)
