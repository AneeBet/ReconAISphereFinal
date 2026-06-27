from datetime import UTC
from datetime import datetime

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.mappers.exception_mapper import (
    ExceptionMapper,
)

from app.models.exception import (
    ExceptionStatus,
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

        exception_id,

        user_id

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

        exception.assigned_to = str(

            user_id

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

        exception_id,

        resolution_notes

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

        exception.resolution_notes = resolution_notes

        exception.resolved_at = datetime.now(

            UTC

        )

        updated = self.repository.update(

            exception

        )

        self.audit.log(

            user_id=exception.assigned_to,

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

