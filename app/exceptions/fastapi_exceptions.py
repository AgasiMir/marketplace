from fastapi import HTTPException, status


class MarketplaceHTTPException(HTTPException):
    status_code = status.HTTP_418_IM_A_TEAPOT
    detail = "Error"

    def __init__(self):
        super().__init__(self.status_code, self.detail)


class CategoryNotFoundHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Category Not Found."


class UserAlreadyExistsHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User With Such Email or Username Already Exists."


class UserNotFoundHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User Not Found."


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


class AdminOnlyHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only administrators can perform this action."


class SellerOnlyHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only sellers can perform this action."


class ProductNotFoundHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Product Not Found."


class WrongSortByHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid sort_by Value."


class CurrentProductSellerHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only the seller of this current product can perform this action."


class NotEnoughRightsHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only the seller of this current product or admin can perform this action."


class FavoriteAlreadyExistsHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Favorite Already Exists."


class FavoriteNotFoundHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Favorite Not Found."


class FavoriteLimitExceededHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Favorite limit exceeded."


class ReviewNotFoundHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Review Not Found."


class OnlyAuthorOrAdminCanDeleteReviewHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only the author of this review or admin can perform this action."


class MinPriceMustBeLessThanMaxPriceHTTPException(MarketplaceHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "MinPrice Must Be Less Than MaxPrice."
