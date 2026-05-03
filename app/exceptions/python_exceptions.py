class MarketplaceException(Exception):
    detail = "Unknown Exception"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class CategoryNotFoundException(MarketplaceException):
    detail = "Category Not Found"


class UserAlreadyExistsException(MarketplaceException):
    detail = "User With Such Email Already Exists"


class IncorrectCredentialsException(MarketplaceException):
    detail = "Incorrect Email Or Password"


class CredentialsException(MarketplaceException):
    detail = "Could not validate refresh token"
