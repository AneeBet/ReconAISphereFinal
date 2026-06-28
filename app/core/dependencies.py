from uuid import UUID
from typing import Callable

import jwt

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import UserRole
from app.repositories.auth_repository import AuthRepository


security = HTTPBearer()


def get_current_user(

    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),

    db: Session = Depends(
        get_db
    )

):

    try:

        payload = jwt.decode(

            credentials.credentials,

            settings.JWT_SECRET,

            algorithms=[settings.JWT_ALGORITHM]

        )

    except Exception:

        raise HTTPException(

            status_code=401,

            detail="Invalid token."

        )

    repository = AuthRepository(db)

    user = repository.get_by_id(

        UUID(

            payload["sub"]

        )

    )

    if user is None:

        raise HTTPException(

            status_code=401,

            detail="User not found."

        )

    if not user.is_active:

        raise HTTPException(

            status_code=403,

            detail="User account is disabled."

        )

    return user


def require_roles(

    *roles: UserRole

) -> Callable:

    def dependency(

        current_user=Depends(

            get_current_user

        )

    ):

        if current_user.role not in roles:

            raise HTTPException(

                status_code=403,

                detail="You are not authorized to access this resource."

            )

        return current_user

    return dependency


require_admin = require_roles(

    UserRole.ADMIN

)

require_ops = require_roles(

    UserRole.ADMIN,

    UserRole.OPS

)

require_auditor = require_roles(

    UserRole.ADMIN,

    UserRole.AUDITOR,

    UserRole.OPS

)

require_viewer = require_roles(

    UserRole.ADMIN,

    UserRole.OPS,

    UserRole.AUDITOR,

    UserRole.VIEWER

)