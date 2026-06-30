from azure.storage.blob import BlobServiceClient

from app.core.config import settings


class AzureBlobStorage:

    def __init__(
        self
    ):

        self.client = BlobServiceClient.from_connection_string(

            settings.AZURE_STORAGE_CONNECTION_STRING

        )

        self.container = self.client.get_container_client(

            settings.AZURE_STORAGE_CONTAINER

        )

    def upload(

        self,

        file_name,

        data

    ):

        blob = self.container.get_blob_client(

            file_name

        )

        blob.upload_blob(

            data,

            overwrite=True

        )

        return blob.url

    def download(

        self,

        file_name

    ):

        blob = self.container.get_blob_client(

            file_name

        )

        return blob.download_blob().readall()
