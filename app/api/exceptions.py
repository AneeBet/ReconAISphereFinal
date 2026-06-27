from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.dependencies import (
    require_auditor,
    require_ops,
)

from app.db.session import (
    get_db,
)

from app.repositories.exception_repository import (
    ExceptionRepository,
)

from app.schemas.exception import (
    AssignExceptionRequest,
    ExceptionSummary,
    ResolveExceptionRequest,
)

from app.services.exception_service import (
    ExceptionService,
)


router = APIRouter(

    prefix="/exceptions",

    tags=["Exception Workspace"]

)


@router.get(

    "",

    response_model=list[ExceptionSummary]

)
def get_exceptions(

    current_user=Depends(
        require_auditor
    ),

    db: Session = Depends(
        get_db
    )

):

    return ExceptionService(

        ExceptionRepository(db)

    ).get_all()


@router.put(

    "/{exception_id}/assign"

)
def assign_exception(

    exception_id: UUID,

    request: AssignExceptionRequest,

    current_user=Depends(
        require_ops
    ),

    db: Session = Depends(
        get_db
    )

):

    return ExceptionService(

        ExceptionRepository(db)

    ).assign(

        exception_id,

        request.user_id

    )


@router.put(

    "/{exception_id}/status"

)
def update_status(

    exception_id: UUID,

    request: ResolveExceptionRequest,

    current_user=Depends(
        require_ops
    ),

    db: Session = Depends(
        get_db
    )

):

    return ExceptionService(

        ExceptionRepository(db)

    ).update_status(

        exception_id,

        request.resolution_notes

    )
