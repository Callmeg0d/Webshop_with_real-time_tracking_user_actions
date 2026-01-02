from fastapi import HTTPException, status


class ShopException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class CannotMakeOrderWithoutAddress(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Для заказа необходимо указать адрес доставки"


class CannotMakeOrderWithoutItems(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Для заказа необходимо иметь товары в корзине"


class NotEnoughProductsInStock(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Для заказа недостаточно товара на складе"


class NotEnoughBalanceToMakeOrder(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Недостаточно баланса пользователя для оформления заказа"


class UserIsNotPresentException(ShopException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден"

