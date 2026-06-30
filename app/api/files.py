from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import UploadFile

from sqlalchemy.orm import Session

from app.core.dependencies import (
    require_ops,
    require_viewer,
)

from app.db.session import (
    get_db,
)

from app.repositories.file_repository import (
    FileRepository,
)

from app.schemas.file import (
    PaymentFileResponse,
)

from app.services.file_service import (
    FileService,
)


router = APIRouter(

    prefix="/files",

    tags=["Upload"]

)


@router.post(

    "/upload-batch"

)
async def upload_batch(

    bank_id: UUID = Form(...),

    payment: UploadFile | None = File(None),

    bank: UploadFile | None = File(None),

    aml: UploadFile | None = File(None),

    fx: UploadFile | None = File(None),

    correspondent: UploadFile | None = File(None),

    settlement: UploadFile | None = File(None),

    current_user=Depends(
        require_ops
    ),

    db: Session = Depends(
        get_db
    )

):

    return await FileService(

        FileRepository(db)

    ).upload_batch(

        {
            "payment": payment,
            "bank": bank,
            "aml": aml,
            "fx": fx,
            "correspondent": correspondent,
            "settlement": settlement,
        },

        bank_id,

        current_user.id

    )


@router.get(

    "",

    response_model=list[PaymentFileResponse]

)
def history(

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return FileService(

        FileRepository(db)

    ).history()