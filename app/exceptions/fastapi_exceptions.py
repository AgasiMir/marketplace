from fastapi import HTTPException, status


class MarketplaceHTTPException(HTTPException):
    status_code = status.HTTP_418_IM_A_TEAPOT
    detail = "Error"

    def __init__(self):
        super().__init__(self.status_code, self.detail)


class CategoryNotFoundHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Category Not Found"


class CategoryAlreadyHTTPExistsException(MarketplaceHTTPException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, wallet_name: str):
        self.detail = f"Category {wallet_name!r} Already Exists"


class UserAlreadyHTTPExistsException(MarketplaceHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User With Such Email Already Exists"


class IncorrectCredentialsHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect email or password"
    headers = {"WWW-Authenticate": "Bearer"}


class CredentialsHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not validate token"
    headers = {"WWW-Authenticate": "Bearer"}


class JWTExpiredSignatureException(MarketplaceHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has expired"
    headers = {"WWW-Authenticate": "Bearer"}
