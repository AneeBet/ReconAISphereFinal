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

    "/upload",

    response_model=PaymentFileResponse

)
async def upload(

    bank_id: UUID = Form(...),

    file: UploadFile = File(...),

    current_user=Depends(
        require_ops
    ),

    db: Session = Depends(
        get_db
    )

):

    return await FileService(

        FileRepository(db)

    ).upload(

        file,

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
