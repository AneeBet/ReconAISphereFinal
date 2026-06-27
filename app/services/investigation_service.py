from datetime import UTC
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.agents.exception.factory import (
    ExceptionAnalysisAgentFactory,
)

from app.agents.recommendation.factory import (
    RecommendationAgentFactory,
)

from app.mappers.investigation_mapper import (
    InvestigationMapper,
)

from app.models.attachment import (
    Attachment,
)

from app.models.comment import (
    Comment,
)

from app.models.investigation_case import (
    CaseStatus,
)

from app.repositories.audit_repository import (
    AuditRepository,
)

from app.repositories.investigation_repository import (
    InvestigationRepository,
)

from app.services.audit_service import (
    AuditService,
)


class InvestigationService:

    def __init__(
        self,
        repository: InvestigationRepository
    ):

        self.repository = repository

        self.audit = AuditService(

            AuditRepository(

                repository.db

            )

        )

        self.exception_agent = (

            ExceptionAnalysisAgentFactory.create()

        )

        self.recommendation_agent = (

            RecommendationAgentFactory.create()

        )

    def get_all(

        self

    ):

        return [

            InvestigationMapper.to_response(

                case

            ).overview

            for case in self.repository.get_all()

        ]

    def get_case(

        self,

        case_id: UUID

    ):

        case = self.repository.get_case(

            case_id

        )

        if case is None:

            raise HTTPException(

                status_code=HTTP_404_NOT_FOUND,

                detail="Investigation case not found."

            )

        return InvestigationMapper.to_response(

            case

        )

    def update_status(

        self,

        case_id: UUID,

        status: CaseStatus

    ):

        case = self.repository.get_case(

            case_id

        )

        if case is None:

            raise HTTPException(

                status_code=HTTP_404_NOT_FOUND,

                detail="Investigation case not found."

            )

        old_value = {

            "status": case.status.value

        }

        case.status = status

        if status in (

            CaseStatus.RESOLVED,

            CaseStatus.CLOSED,

        ):

            case.closed_at = datetime.now(

                UTC

            )

        updated = self.repository.update(

            case

        )

        self.audit.log(

            user_id=case.owner_id,

            entity_type="InvestigationCase",

            entity_id=case.id,

            action="STATUS_CHANGED",

            old_value=old_value,

            new_value={

                "status": status.value

            }

        )

        return updated

    def add_comment(

        self,

        case_id: UUID,

        user_id: UUID,

        comment: str

    ):

        case = self.repository.get_case(

            case_id

        )

        if case is None:

            raise HTTPException(

                status_code=HTTP_404_NOT_FOUND,

                detail="Investigation case not found."

            )

        entity = Comment(

            case_id=case_id,

            user_id=user_id,

            comment=comment

        )

        entity = self.repository.add_comment(

            entity

        )

        self.audit.log(

            user_id=user_id,

            entity_type="InvestigationCase",

            entity_id=case_id,

            action="COMMENT_ADDED"

        )

        return entity

    def add_attachment(

        self,

        case_id: UUID,

        user_id: UUID,

        file_name: str,

        blob_url: str

    ):

        case = self.repository.get_case(

            case_id

        )

        if case is None:

            raise HTTPException(

                status_code=HTTP_404_NOT_FOUND,

                detail="Investigation case not found."

            )

        entity = Attachment(

            case_id=case_id,

            uploaded_by_id=user_id,

            file_name=file_name,

            blob_url=blob_url

        )

        entity = self.repository.add_attachment(

            entity

        )

        self.audit.log(

            user_id=user_id,

            entity_type="InvestigationCase",

            entity_id=case_id,

            action="ATTACHMENT_ADDED",

            new_value={

                "file_name": file_name

            }

        )

        return entity

    def ai_explanation(

        self,

        case_id: UUID

    ):

        case = self.repository.get_case(

            case_id

        )

        if case is None:

            raise HTTPException(

                status_code=HTTP_404_NOT_FOUND,

                detail="Investigation case not found."

            )

        reconciliation = (

            case.exception.reconciliation_result

        )

        self.audit.log(

            user_id=case.owner_id,

            entity_type="InvestigationCase",

            entity_id=case.id,

            action="AI_EXPLANATION"

        )

        return self.exception_agent.analyze(

            reconciliation,

            reconciliation.payment_transaction,

            reconciliation.bank_transaction

        )

    def ai_recommendation(

        self,

        case_id: UUID

    ):

        case = self.repository.get_case(

            case_id

        )

        if case is None:

            raise HTTPException(

                status_code=HTTP_404_NOT_FOUND,

                detail="Investigation case not found."

            )

        self.audit.log(

            user_id=case.owner_id,

            entity_type="InvestigationCase",

            entity_id=case.id,

            action="AI_RECOMMENDATION"

        )

        return self.recommendation_agent.recommend(

            case

        )

