from fastapi import APIRouter, Depends, HTTPException

from app.domain.entities.categories import CategoryItem
from app.schemas.categories import SCategoryResponse, SCategoryCreate
from app.services.category_service import CategoryService
from app.dependencies import get_categories_service

router = APIRouter(
    prefix="/categories",
    tags=["Категории"]
)


@router.get("/", response_model=list[SCategoryResponse])
async def get_all_categories(
        category_service: CategoryService = Depends(get_categories_service)
):
    """Получить все категории."""
    return await category_service.get_all_categories()


@router.get("/id/{category_id}", response_model=SCategoryResponse)
async def get_category_by_id(
        category_id: int,
        category_service: CategoryService = Depends(get_categories_service)
):
    """Получить категорию по ID."""
    category = await category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/name/{name}", response_model=SCategoryResponse)
async def get_category_by_name(
        name: str,
        category_service: CategoryService = Depends(get_categories_service)
):
    """Получить категорию по названию."""
    category = await category_service.get_category_by_name(name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=SCategoryResponse)
async def create_category(
        category_data: SCategoryCreate,
        category_service: CategoryService = Depends(get_categories_service)
):
    """Создать новую категорию."""
    category = CategoryItem(
        id=None,
        name=category_data.name,
        description=category_data.description
    )
    return await category_service.create_category(category)