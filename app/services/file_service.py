import uuid

import pandas as pd

from app.models.bank_transaction import (
    BankTransaction,
)

from app.models.payment_file import (
    PaymentFile,
    ProcessingStatus,
)

from app.models.payment_transaction import (
    PaymentStatus,
    PaymentTransaction,
)

from app.models.transaction_leg import (
    LegStage,
    LegStatus,
    TransactionLeg,
)

from app.parser.normalizer import (
    Normalizer,
)

from app.repositories.audit_repository import (
    AuditRepository,
)

from app.repositories.file_repository import (
    FileRepository,
)

from app.services.audit_service import (
    AuditService,
)

from app.storage.azure_blob_storage import (
    AzureBlobStorage,
)


class FileService:

    def __init__(
        self,
        repository: FileRepository
    ):

        self.repository = repository

        self.storage = AzureBlobStorage()

        self.audit = AuditService(

            AuditRepository(

                repository.db

            )

        )

    def history(

        self

    ):

        return self.repository.get_all()

    async def upload_batch(
        self,
        files: dict,
        bank_id,
        user_id
    ):
        """Ingest any subset of {payment, bank, aml, fx, correspondent,
        settlement} in one call. Each is stored to blob and normalized."""

        summary = {"ingested": {}}

        stage_map = {
            "aml": LegStage.AML,
            "fx": LegStage.FX,
            "correspondent": LegStage.CORRESPONDENT,
            "settlement": LegStage.SETTLEMENT,
        }

        for kind, upload in files.items():

            if upload is None:
                continue

            contents = await upload.read()

            blob_name = f"{uuid.uuid4()}_{upload.filename}"
            blob_url = self.storage.upload(f"{kind}/{blob_name}", contents)

            rows = Normalizer.rows(contents, upload.filename)

            if kind == "payment":
                self.repository.save_payment_transactions([
                    self._build_payment_transaction(None, bank_id, r)
                    for r in rows
                ])
            elif kind == "bank":
                self.repository.save_bank_transactions([
                    self._build_bank_transaction(bank_id, r) for r in rows
                ])
            else:
                self.repository.save_legs([
                    self._build_leg(stage_map[kind], r) for r in rows
                ])

            self.repository.create(
                PaymentFile(
                    bank_id=bank_id,
                    file_name=blob_name,
                    original_name=upload.filename,
                    blob_url=blob_url,
                    file_type=kind.upper(),
                    checksum=str(uuid.uuid4()),
                    uploaded_by_id=user_id,
                    processing_status=ProcessingStatus.COMPLETED,
                    total_records=len(rows),
                    valid_records=len(rows),
                    invalid_records=0
                )
            )

            summary["ingested"][kind] = len(rows)

        self.audit.log(
            user_id=user_id,
            entity_type="PaymentFile",
            entity_id=bank_id,
            action="BATCH_UPLOAD",
            new_value=summary["ingested"]
        )

        return summary

    def _build_leg(self, stage, row):
        status = str(row.get("status", "PASS")).upper()
        if status not in LegStatus.__members__:
            status = "PASS"
        return TransactionLeg(
            end_to_end_id=str(row.get("end_to_end_id", "")),
            stage=stage,
            status=LegStatus[status],
            detail=str(row.get("detail", "")) or None,
            event_time=self._to_date(row.get("event_time"))
        )

    def _build_payment_transaction(
        self,
        payment_file_id,
        bank_id,
        row
    ):

        return PaymentTransaction(

            payment_file_id=payment_file_id,

            bank_id=bank_id,

            transaction_reference=str(row["transaction_reference"]),

            end_to_end_id=str(row["end_to_end_id"]),

            sender_account=str(row.get("sender_account", "")),

            receiver_account=str(row.get("receiver_account", "")),

            sender_name=str(row.get("sender_name", "")),

            receiver_name=str(row.get("receiver_name", "")),

            amount=float(row["amount"]),

            currency=str(row["currency"]),

            fx_rate=self._optional_float(row.get("fx_rate")),

            payment_date=self._to_date(row["payment_date"]),

            settlement_date=self._to_date(row.get("settlement_date")),

            payment_type=str(row.get("payment_type", "CROSS_BORDER")),

            status=PaymentStatus.PENDING

        )

    def _build_bank_transaction(
        self,
        bank_id,
        row
    ):

        return BankTransaction(

            bank_id=bank_id,

            transaction_reference=str(row["transaction_reference"]),

            end_to_end_id=str(row["end_to_end_id"]),

            sender_account=str(row.get("sender_account", "")),

            receiver_account=str(row.get("receiver_account", "")),

            sender_name=str(row.get("sender_name", "")),

            receiver_name=str(row.get("receiver_name", "")),

            amount=float(row["amount"]),

            currency=str(row["currency"]),

            fx_rate=self._optional_float(row.get("fx_rate")),

            payment_date=self._to_date(row["payment_date"]),

            settlement_date=self._to_date(row.get("settlement_date")),

            payment_type=str(row.get("payment_type", "CROSS_BORDER")),

            status=str(row.get("status", "SETTLED"))

        )

    @staticmethod
    def _optional_float(value):

        if value is None or pd.isna(value):

            return None

        return float(value)

    @staticmethod
    def _to_date(value):

        if value is None or pd.isna(value):

            return None

        return pd.to_datetime(value).to_pydatetime()
