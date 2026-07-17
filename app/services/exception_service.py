from datetime import UTC
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.mappers.exception_mapper import (
    ExceptionMapper,
)

from app.models.exception import (
    ExceptionStatus,
)

from app.models.investigation_case import (
    CaseStatus,
)

from app.repositories.audit_repository import (
    AuditRepository,
)

from app.repositories.exception_repository import (
    ExceptionRepository,
)

from app.services.audit_service import (
    AuditService,
)


class ExceptionService:

    def __init__(
        self,
        repository: ExceptionRepository
    ):

        self.repository = repository

        self.audit = AuditService(

            AuditRepository(

                repository.db

            )

        )

    def get_all(
        self
    ):

        return [

            ExceptionMapper.to_summary(

                exception

            )

            for exception in

            self.repository.get_all()

        ]

    def assign(

        self,

        exception_id: UUID,

        user_id: UUID

    ):

        exception = self.repository.get_by_id(

            exception_id

        )

        if exception is None:

            raise HTTPException(

                status_code=HTTP_404_NOT_FOUND,

                detail="Exception not found."

            )

        old_value = {

            "assigned_to": exception.assigned_to

        }

        # Update exception owner
        exception.assigned_to = str(user_id)

        # Keep investigation case in sync
        if exception.investigation_case is not None:

            exception.investigation_case.owner_id = user_id

            exception.investigation_case.status = (
                CaseStatus.ASSIGNED
            )

        updated = self.repository.update(

            exception

        )

        self.audit.log(

            user_id=user_id,

            entity_type="Exception",

            entity_id=exception.id,

            action="ASSIGN",

            old_value=old_value,

            new_value={

                "assigned_to": exception.assigned_to

            }

        )

        return updated

    def update_status(

        self,

        exception_id: UUID,

        resolution_notes: str

    ):

        exception = self.repository.get_by_id(

            exception_id

        )

        if exception is None:

            raise HTTPException(

                status_code=HTTP_404_NOT_FOUND,

                detail="Exception not found."

            )

        old_value = {

            "status": exception.status.value

        }

        exception.status = ExceptionStatus.RESOLVED

        if exception.investigation_case:

            exception.investigation_case.status = CaseStatus.RESOLVED

            exception.investigation_case.closed_at = datetime.now(UTC)

        exception.resolution_notes = resolution_notes

        exception.resolved_at = datetime.now(

            UTC

        )

        # Keep linked investigation case in sync
        if exception.investigation_case is not None:

            exception.investigation_case.status = (
                CaseStatus.RESOLVED
            )

            exception.investigation_case.closed_at = (
                exception.resolved_at
            )

        updated = self.repository.update(

            exception

        )

        self.audit.log(

            user_id=UUID(exception.assigned_to),

            entity_type="Exception",

            entity_id=exception.id,

            action="RESOLVE",

            old_value=old_value,

            new_value={

                "status": exception.status.value,

                "resolution_notes": resolution_notes

            }

        )

        return updated