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

from app.repositories.ai_repository import (
    AIRepository,
)

from app.schemas.ai import (
    AIQuestionRequest,
    AIChatResponse,
    AIInsightResponse,
    ConversationHistoryResponse,
)

from app.services.ai_service import (
    AIService,
)


router = APIRouter(

    prefix="/ai",

    tags=["AI Copilot"]

)


@router.post(

    "/chat",

    response_model=AIChatResponse

)
def chat(

    request: AIQuestionRequest,

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return AIService(

        AIRepository(db)

    ).chat(

        current_user.id,

        request.question

    )


@router.get(

    "/history",

    response_model=ConversationHistoryResponse

)
def history(

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return AIService(

        AIRepository(db)

    ).history(

        current_user.id

    )


@router.post(

    "/explain/{case_id}",

    response_model=AIInsightResponse

)
def explain(

    case_id: UUID,

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return AIService(

        AIRepository(db)

    ).explain(

        case_id

    )


@router.post(

    "/recommend/{case_id}",

    response_model=AIInsightResponse

)
def recommend(

    case_id: UUID,

    current_user=Depends(
        require_viewer
    ),

    db: Session = Depends(
        get_db
    )

):

    return AIService(

        AIRepository(db)

    ).recommend(

        case_id

    )
