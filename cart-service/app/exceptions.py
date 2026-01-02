from fastapi import HTTPException, status


class ShopException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class CannotHaveLessThan1Product(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Невозможно иметь менее одного товара в корзине"


class NeedToHaveAProductToIncreaseItsQuantity(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Для увеличения количества товара, он должен находиться в корзине"

