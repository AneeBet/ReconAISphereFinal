from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.dependencies import (
    require_auditor,
)

from app.db.session import (
    get_db,
)

from app.repositories.audit_repository import (
    AuditRepository,
)

from app.schemas.audit import (
    AuditLogResponse,
)

from app.services.audit_service import (
    AuditService,
)


router = APIRouter(

    prefix="/audit",

    tags=["Audit"]

)


@router.get(

    "",

    response_model=AuditLogResponse

)
def audit_logs(

    current_user=Depends(
        require_auditor
    ),

    db: Session = Depends(
        get_db
    )

):

    return AuditService(

        AuditRepository(db)

    ).get_logs()
