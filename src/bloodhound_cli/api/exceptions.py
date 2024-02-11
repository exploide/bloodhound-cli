class ApiException(Exception):
    """Exception subclass used to indicate a problem while communicating with the API."""

    response = None
    """Instance of requests.models.Response containing the response that causes a problem."""

    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response
