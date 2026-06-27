from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    CurrentUserResponse
)

from app.repositories.auth_repository import (
    AuthRepository
)

from app.services.auth_service import (
    AuthService
)

from app.core.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    service = AuthService(
        AuthRepository(db)
    )

    return service.login(
        request
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse
)
def current_user(
    current_user=Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    service = AuthService(
        AuthRepository(db)
    )

    return service.current_user(
        current_user.id
    )
