from app.models.audit_log import AuditLog

from app.repositories.audit_repository import (
    AuditRepository,
)

from app.schemas.audit import (
    AuditLogItem,
    AuditLogResponse,
)


class AuditService:

    def __init__(
        self,
        repository: AuditRepository
    ):
        self.repository = repository


    def log(

        self,

        user_id,

        entity_type: str,

        entity_id: str,

        action: str,

        old_value=None,

        new_value=None,

        ip_address=None

    ):

        audit = AuditLog(

            user_id=user_id,

            entity_type=entity_type,

            entity_id=str(entity_id),

            action=action,

            old_value=old_value,

            new_value=new_value,

            ip_address=ip_address

        )

        return self.repository.create(
            audit
        )


    def get_logs(
        self
    ):

        logs = self.repository.get_logs()

        return AuditLogResponse(

            total_records=len(logs),

            logs=[

                AuditLogItem(

                    timestamp=log.created_at,

                    user=(

                        f"{log.user.first_name} {log.user.last_name}"

                        if log.user

                        else "System"

                    ),

                    action=log.action,

                    entity=log.entity_type,

                    entity_id=log.entity_id,

                    ip_address=log.ip_address,

                    details=f"{log.entity_type} {log.action}"

                )

                for log in logs

            ]

        )

