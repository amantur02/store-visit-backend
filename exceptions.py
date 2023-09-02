class StoreVisitHTTPException(Exception):
    default_message = "Default HTTP Exception for store visit"
    error_code = "UndefinedHTTPError"
    status_code = 400

    def __init__(self, message: str = None, status_code: int = None):
        self.message = message if message else self.default_message
        self.status_code = status_code if status_code else self.status_code


class StoreVisitException(Exception):
    default_message = "Something went wrong"
    error_code = "ErrorCodeNotDefined"

    def __init__(self, message=None):
        self.message = message if message else self.default_message
        self.error_code = self.error_code


class NotFoundException(StoreVisitException):
    message = "Not found"
    error_code = "NotFoundError"


class AuthenticationError(StoreVisitException):
    default_message = "Wrong login or password"
    error_code = "AuthenticationError"


class AlreadyExistsException(StoreVisitException):
    message = "Already Exists"
    error_code = "DataAlreadyExistsError"
