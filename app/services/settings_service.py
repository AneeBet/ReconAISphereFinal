from uuid import UUID

from app.repositories.audit_repository import (
    AuditRepository,
)

from app.repositories.settings_repository import (
    SettingsRepository,
)

from app.schemas.settings import (
    AISettingsResponse,
    UpdateAISettingsRequest,
)

from app.services.audit_service import (
    AuditService,
)


class SettingsService:

    def __init__(
        self,
        repository: SettingsRepository
    ):

        self.repository = repository

        self.audit = AuditService(

            AuditRepository(

                repository.db

            )

        )

    def get_settings(

        self,

    ):

        settings = {

            item.setting_key: item.setting_value

            for item in self.repository.get_all()

        }

        return AISettingsResponse(

            matching_confidence_threshold=float(

                settings.get(

                    "matching_confidence_threshold",

                    80

                )

            ),

            amount_tolerance=float(

                settings.get(

                    "amount_tolerance",

                    0.01

                )

            ),

            date_tolerance_days=int(

                settings.get(

                    "date_tolerance_days",

                    1

                )

            ),

            exchange_rate_source=settings.get(

                "exchange_rate_source",

                "ECB"

            )

        )

    def save_settings(

        self,

        request: UpdateAISettingsRequest,

        user_id: UUID

    ):

        self.repository.upsert(

            "matching_confidence_threshold",

            str(

                request.matching_confidence_threshold

            ),

            user_id

        )

        self.repository.upsert(

            "amount_tolerance",

            str(

                request.amount_tolerance

            ),

            user_id

        )

        self.repository.upsert(

            "date_tolerance_days",

            str(

                request.date_tolerance_days

            ),

            user_id

        )

        self.repository.upsert(

            "exchange_rate_source",

            request.exchange_rate_source,

            user_id

        )

        self.audit.log(

            user_id=user_id,

            entity_type="SystemSettings",

            entity_id="AI",

            action="UPDATE",

            new_value={

                "matching_confidence_threshold": request.matching_confidence_threshold,

                "amount_tolerance": request.amount_tolerance,

                "date_tolerance_days": request.date_tolerance_days,

                "exchange_rate_source": request.exchange_rate_source,

            }

        )

        return self.get_settings()

