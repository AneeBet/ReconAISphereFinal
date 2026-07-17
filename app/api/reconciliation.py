from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.dependencies import (
    require_ops,
)

from app.db.session import (
    get_db,
)

from app.repositories.reconciliation_repository import (
    ReconciliationRepository,
)

from app.schemas.reconciliation import (
    ReconciliationItem,
)

from app.services.reconciliation_service import (
    ReconciliationService,
)


router = APIRouter(

    prefix="/reconciliation",

    tags=["Reconciliation"]

)


@router.post(

    "/run"

)
def run_reconciliation(

    current_user=Depends(
        require_ops
    ),

    db: Session = Depends(
        get_db
    )

):

    return ReconciliationService(

        ReconciliationRepository(db)

    ).run(

        current_user.id

    )


@router.get(

    "/results",

    response_model=list[ReconciliationItem]

)
def get_results(

    current_user=Depends(
        require_ops
    ),

    db: Session = Depends(
        get_db
    )

):

    return ReconciliationService(

        ReconciliationRepository(db)

    ).results()