class MarketplaceException(Exception):
    detail = "Unknown Exception."

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class CategoryNotFoundException(MarketplaceException):
    detail = "Category Not Found."


class UserAlreadyExistsException(MarketplaceException):
    detail = "User With Such Email Already Exists."


class UserNotFoundException(MarketplaceException):
    detail = "User Not Found."


class IncorrectCredentialsException(MarketplaceException):
    detail = "Incorrect Email Or Password."


class CredentialsException(MarketplaceException):
    detail = "Could not validate refresh token."


class ProductNotFoundException(MarketplaceException):
    detail = "Product Not Found."


class WrongSortByException(MarketplaceException):
    detail = "Invalid sort_by Value."


class CurrentProductSellerException(MarketplaceException):
    detail = "Only the seller of this current product can perform this action."


class NotEnoughRightsException(MarketplaceException):
    detail = "Only the seller of this current product or admin can perform this action."


class FavoriteAlreadyExistsException(MarketplaceException):
    detail = "Favorite Already Exists."


class FavoriteNotFoundException(MarketplaceException):
    detail = "Favorite Not Found."


class FavoriteLimitExceededException(MarketplaceException):
    detail = "Favorite limit exceeded."


class ReviewNotFoundException(MarketplaceException):
    detail = "Review Not Found."


class OnlyAuthorOrAdminCanDeleteReviewException(MarketplaceException):
    detail = "Only the author of this review or admin can perform this action."


class MinPriceMustBeLessThanMaxPriceException(MarketplaceException):
    detail = "MinPrice Must Be Less Than MaxPrice."


class CartItemNotFoundException(MarketplaceException):
    detail = "Cart Item Not Found."


class CartIsEmptyException(MarketplaceException):
    detail = "Cart Is Empty."


class ProductIsUnavailableException(MarketplaceException):
    def __init__(self, product_id: int):
        self.detail = f"Product with id {product_id} is unavailable."


class ProductIsOutOfStockException(MarketplaceException):
    def __init__(self, product_name: str):
        self.detail = f"Product {product_name!r} is out of stock."


class ProductWithNoPriceException(MarketplaceException):
    def __init__(self, product_name: str):
        self.detail = f"Product {product_name!r} has no price set."


class FailedToLoadOrderException(MarketplaceException):
    detail = "Failed To Load Created Order."


class OrderNotFoundException(MarketplaceException):
    detail = "Order Not Found."
