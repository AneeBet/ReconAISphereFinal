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

from app.repositories.investigation_repository import (
    InvestigationRepository,
)

from app.schemas.investigation import (
    InvestigationCaseSummary,
    InvestigationCaseResponse,
    CaseComment,
    CaseAttachment,
)

from app.models.investigation_case import (
    CaseStatus,
)

from app.services.investigation_service import (
    InvestigationService,
)


router = APIRouter(

    prefix="/cases",

    tags=["Investigation"]

)


@router.get(

    "",

    response_model=list[InvestigationCaseSummary]

)
def get_cases(

    current_user=Depends(
        require_auditor
    ),

    db: Session = Depends(
        get_db
    )

):

    return InvestigationService(

        InvestigationRepository(db)

    ).get_all()


@router.get(

    "/{case_id}",

    response_model=InvestigationCaseResponse

)
def get_case(

    case_id: UUID,

    current_user=Depends(
        require_auditor
    ),

    db: Session = Depends(
        get_db
    )

):

    return InvestigationService(

        InvestigationRepository(db)

    ).get_case(

        case_id

    )


@router.put(

    "/{case_id}/status"

)
def update_status(

    case_id: UUID,

    status: CaseStatus,

    current_user=Depends(
        require_ops
    ),

    db: Session = Depends(
        get_db
    )

):

    return InvestigationService(

        InvestigationRepository(db)

    ).update_status(

        case_id,

        status

    )


@router.post(

    "/{case_id}/comments",

    response_model=CaseComment

)
def add_comment(

    case_id: UUID,

    comment: str,

    current_user=Depends(
        require_ops
    ),

    db: Session = Depends(
        get_db
    )

):

    return InvestigationService(

        InvestigationRepository(db)

    ).add_comment(

        case_id,

        current_user.id,

        comment

    )


@router.post(

    "/{case_id}/attachments",

    response_model=CaseAttachment

)
def add_attachment(

    case_id: UUID,

    file_name: str,

    blob_url: str,

    current_user=Depends(
        require_ops
    ),

    db: Session = Depends(
        get_db
    )

):

    return InvestigationService(

        InvestigationRepository(db)

    ).add_attachment(

        case_id,

        current_user.id,

        file_name,

        blob_url

    )