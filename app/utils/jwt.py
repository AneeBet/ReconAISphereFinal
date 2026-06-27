from datetime import UTC, datetime, timedelta
import uuid

import jwt

from app.core.config import settings


def create_access_token(user) -> str:

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "org": str(user.organization_id),
        "jti": str(uuid.uuid4()),
        "exp": datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(user) -> str:

    payload = {
        "sub": str(user.id),
        "jti": str(uuid.uuid4()),
        "exp": datetime.now(UTC) + timedelta(days=30),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
