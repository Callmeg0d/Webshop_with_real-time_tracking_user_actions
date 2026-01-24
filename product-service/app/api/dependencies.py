from fastapi import Query

from app.schemas.products import Pagination, SortEnum


def pagination_params(
    page: int = Query(default=1, ge=1, le=50),
    per_page: int = Query(default=10, ge=1, le=50),
    order: SortEnum = Query(default=SortEnum.DESC),
) -> Pagination:
    return Pagination(page=page, per_page=per_page, order=order)
