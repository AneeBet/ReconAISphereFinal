from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.dependencies import (
    require_viewer,
)

from app.db.session import (
    get_db,
)

from app.repositories.transaction_repository import (
    TransactionRepository,
)

from app.schemas.transaction import (
    TransactionDetailResponse,
    TransactionSummary,
)

from app.services.transaction_service import (
    TransactionService,
)


router = APIRouter(

    prefix="/transactions",

    tags=["Transaction Explorer"]

)


@router.get(

    "",

    response_model=list[TransactionSummary]

)
def get_transactions(

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return TransactionService(

        TransactionRepository(db)

    ).get_transactions()


@router.get(

    "/{transaction_id}",

    response_model=TransactionDetailResponse

)
def get_transaction(

    transaction_id: UUID,

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return TransactionService(

        TransactionRepository(db)

    ).get_transaction(

        transaction_id

    )
