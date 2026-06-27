import uuid

from app.models.payment_file import (
    PaymentFile,
    ProcessingStatus,
)

from app.parser.payment_parser import (
    PaymentParser,
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

        self.parser = PaymentParser()

        self.audit = AuditService(

            AuditRepository(

                repository.db

            )

        )

    async def upload(

        self,

        file,

        bank_id,

        user_id

    ):

        blob_name = (

            f"{uuid.uuid4()}_{file.filename}"

        )

        blob_url = self.storage.upload(

            blob_name,

            await file.read()

        )

        await file.seek(0)

        dataframe = await self.parser.parse(

            file

        )

        payment_file = PaymentFile(

            bank_id=bank_id,

            file_name=blob_name,

            original_name=file.filename,

            blob_url=blob_url,

            file_type=file.filename.split(".")[-1],

            checksum=str(uuid.uuid4()),

            uploaded_by_id=user_id,

            processing_status=ProcessingStatus.UPLOADED,

            total_records=len(dataframe),

            valid_records=len(dataframe),

            invalid_records=0

        )

        payment_file = self.repository.create(

            payment_file

        )

        self.audit.log(

            user_id=user_id,

            entity_type="PaymentFile",

            entity_id=payment_file.id,

            action="UPLOAD",

            new_value={

                "file_name": payment_file.original_name,

                "records": payment_file.total_records,

                "bank_id": str(bank_id)

            }

        )

        return payment_file

    def history(

        self

    ):

        return self.repository.get_all()

