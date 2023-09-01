class StoreVisitHTTPException(Exception):
    default_message = "Default HTTP Exception for bank"
    error_code = "UndefinedHTTPError"
    status_code = 400

    def __init__(self, message: str = None, status_code: int = None):
        self.message = message if message else self.default_message
        self.status_code = status_code if status_code else self.status_code
