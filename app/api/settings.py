from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.dependencies import (
    require_admin,
)

from app.db.session import (
    get_db,
)

from app.repositories.settings_repository import (
    SettingsRepository,
)

from app.schemas.settings import (
    AISettingsResponse,
    UpdateAISettingsRequest,
)

from app.services.settings_service import (
    SettingsService,
)


router = APIRouter(

    prefix="/settings",

    tags=["Settings"]

)


@router.get(

    "",

    response_model=AISettingsResponse

)
def get_settings(

    current_user=Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return SettingsService(

        SettingsRepository(db)

    ).get_settings()


@router.put(

    "",

    response_model=AISettingsResponse

)
def save_settings(

    request: UpdateAISettingsRequest,

    current_user=Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return SettingsService(

        SettingsRepository(db)

    ).save_settings(

        request

    )
