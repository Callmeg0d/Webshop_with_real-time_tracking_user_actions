from fastapi import HTTPException, status


class ShopException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(ShopException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorrectEmailOrPasswordException(ShopException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный логин или пароль"


class IncorrectTokenFormatException(ShopException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"


class TokenAbsentException(ShopException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class TokenExpiredException(ShopException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек"


class UserIsNotPresentException(ShopException):
    status_code = status.HTTP_401_UNAUTHORIZED


class CannotAddDataToDatabase(ShopException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Не удалось добавить запись"


class CannotMakeOrderWithoutAddress(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Для заказа необходимо указать адрес доставки"


class CannotMakeOrderWithoutItems(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Для заказа необходимо иметь товары в коризне"


class NotEnoughProductsInStock(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Для заказа недостаточно товара на складе"


class CannotHaveLessThan1Product(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Невозможно иметь менее одного товара в корзине"


class NeedToHaveAProductToIncreaseItsQuantity(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Для увеличения количества товара, он должен находиться в корзине"


class CannotFindProductWithThisId(ShopException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Товара с таким id не существует"

class NotEnoughBalanceToMakeOrder(ShopException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Недостаточно баланса пользователя для оформления заказа"

