from fastapi import HTTPException, status


class ShopException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class CannotFindProductWithThisId(ShopException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Товара с таким id не существует"

