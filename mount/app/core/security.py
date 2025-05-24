from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer()


BearerToken = Annotated[HTTPAuthorizationCredentials, Depends(security)]