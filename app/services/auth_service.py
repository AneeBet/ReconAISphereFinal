from uuid import UUID

from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.repositories.auth_repository import (
    AuthRepository,
)

from app.repositories.audit_repository import (
    AuditRepository,
)

from app.schemas.auth import (
    LoginRequest,
)

from app.services.audit_service import (
    AuditService,
)

from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
)

from app.utils.password import (
    verify_password,
)


class AuthService:

    def __init__(
        self,
        repository: AuthRepository
    ):

        self.repository = repository

        self.audit = AuditService(

            AuditRepository(

                repository.db

            )

        )

    def login(
        self,
        request: LoginRequest
    ):

        user = self.repository.get_by_email(

            request.email

        )

        if (

            user is None

            or

            not verify_password(

                request.password,

                user.password_hash

            )

        ):

            raise HTTPException(

                status_code=HTTP_401_UNAUTHORIZED,

                detail="Invalid email or password."

            )

        self.repository.update_last_login(

            user

        )

        self.audit.log(

            user_id=user.id,

            entity_type="User",

            entity_id=user.id,

            action="LOGIN"

        )

        return {

            "access_token": create_access_token(
                user
            ),

            "refresh_token": create_refresh_token(
                user
            ),

            "token_type": "Bearer"

        }

    def current_user(
        self,
        user_id: UUID
    ):

        user = self.repository.get_by_id(

            user_id

        )

        if user is None:

            raise HTTPException(

                status_code=HTTP_401_UNAUTHORIZED,

                detail="User not found."

            )

        return user

