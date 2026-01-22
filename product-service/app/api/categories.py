from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from shared import get_logger

from app.dependencies import get_categories_service
from app.domain.entities.categories import CategoryItem
from app.schemas.categories import SCategoryResponse, SCategoryCreate
from app.services.category_service import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Категории"]
)

logger = get_logger(__name__)


@router.get("/", response_model=list[SCategoryResponse])
async def get_all_categories(
        category_service: CategoryService = Depends(get_categories_service)
):
    """Получить все категории."""
    logger.info("GET /categories/ request")
    try:
        categories = await category_service.get_all_categories()
        logger.info(f"Returned {len(categories)} categories")
        return categories
    except Exception as e:
        logger.error(f"Error fetching categories by API: {e}", exc_info=True)
        raise


@router.get("/{category_id}", response_model=SCategoryResponse)
async def get_category_by_id(
        category_id: int,
        category_service: CategoryService = Depends(get_categories_service)
):
    """Получить категорию по ID."""
    logger.info(f"GET /categories/{category_id} request")
    try:
        category = await category_service.get_category_by_id(category_id)
        if not category:
            logger.warning(f"Category {category_id} not found")
            raise HTTPException(status_code=404, detail="Category not found")
        logger.info(f"Category {category_id} returned successfully")
        return category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching category {category_id} by API: {e}", exc_info=True)
        raise


@router.get("/name/{name}", response_model=SCategoryResponse)
async def get_category_by_name(
        name: str,
        category_service: CategoryService = Depends(get_categories_service)
):
    """Получить категорию по названию."""
    logger.info(f"GET /categories/name/{name} request")
    try:
        category = await category_service.get_category_by_name(name)
        if not category:
            logger.warning(f"Category '{name}' not found")
            raise HTTPException(status_code=404, detail="Category not found")
        logger.info(f"Category '{name}' returned successfully")
        return category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching category by name '{name}' by API: {e}", exc_info=True)
        raise


@router.post("/", response_model=SCategoryResponse)
async def create_category(
        category_data: SCategoryCreate,
        category_service: CategoryService = Depends(get_categories_service)
):
    """Создать новую категорию."""
    logger.info(f"POST /categories/ request, name: {category_data.name}")
    try:
        category = CategoryItem(
            id=None,
            name=category_data.name,
            description=category_data.description
        )
        created = await category_service.create_category(category)
        logger.info(f"Category created by API: {created.name}")
        return created
    except IntegrityError as e:
        logger.error(f"Integrity error creating category by API: {e}", exc_info=True)
        raise HTTPException(status_code=409, detail="Category with this name already exists")
    except Exception as e:
        logger.error(f"Error creating category by API: {e}", exc_info=True)
        raise


