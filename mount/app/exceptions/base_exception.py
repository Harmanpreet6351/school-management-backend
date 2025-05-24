from pydantic import BaseModel

class AppBaseException(Exception):
    def __init__(self, status_code: int, error_code: str, detail: str):
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail


class HTTPExceptionResponseModel(BaseModel):
    code: str
    detail: str
