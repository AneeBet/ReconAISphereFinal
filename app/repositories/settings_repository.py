from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.system_setting import (
    SystemSetting,
)


class SettingsRepository:

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def get_all(
        self
    ):

        return list(

            self.db.scalars(

                select(SystemSetting)

            ).all()

        )

    def get_by_key(
        self,
        key: str
    ) -> SystemSetting | None:

        return self.db.scalar(

            select(SystemSetting)

            .where(

                SystemSetting.setting_key == key

            )

        )

    def save(
        self,
        setting: SystemSetting
    ):

        self.db.add(setting)

        self.db.commit()

        self.db.refresh(setting)

        return setting

    def upsert(

        self,

        key: str,

        value: str,

        updated_by_id

    ):

        setting = self.get_by_key(

            key

        )

        if setting is None:

            setting = SystemSetting(

                setting_key=key,

                setting_value=value,

                updated_by_id=updated_by_id

            )

        else:

            setting.setting_value = value

            setting.updated_by_id = updated_by_id

        return self.save(

            setting

        )

