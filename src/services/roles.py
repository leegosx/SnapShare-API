from typing import List

from fastapi import Request, Depends, HTTPException, status

from src.services.auth_service import auth_service


class Roles:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request, user=Depends(auth_service.get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not authorizated to perform this action')