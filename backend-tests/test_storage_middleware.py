import asyncio
from types import SimpleNamespace

from app.middleware.logging import RequestLoggingMiddleware
from app.storage.azure_blob_storage import AzureBlobStorage


def test_azure_blob_storage_upload_and_download(monkeypatch):
    uploaded = {}

    class FakeBlob:
        url = "https://fake.blob/container/file.txt"

        def upload_blob(self, data, overwrite=True):
            uploaded["data"] = data
            uploaded["overwrite"] = overwrite

        def download_blob(self):
            return SimpleNamespace(readall=lambda: b"downloaded-content")

    class FakeContainer:
        def get_blob_client(self, file_name):
            uploaded["file_name"] = file_name
            return FakeBlob()

    class FakeClient:
        def get_container_client(self, container_name):
            uploaded["container_name"] = container_name
            return FakeContainer()

    monkeypatch.setattr(
        "app.storage.azure_blob_storage.BlobServiceClient",
        SimpleNamespace(from_connection_string=lambda conn: FakeClient()),
    )

    storage = AzureBlobStorage()

    assert storage.upload("file.txt", b"payload-data") == "https://fake.blob/container/file.txt"
    assert uploaded["data"] == b"payload-data"
    assert uploaded["overwrite"] is True
    assert uploaded["file_name"] == "file.txt"
    assert uploaded["container_name"] == "test-container"

    assert storage.download("file.txt") == b"downloaded-content"


def test_request_logging_middleware_dispatch_logs_and_returns_response(monkeypatch):
    request = SimpleNamespace(
        method="GET",
        url=SimpleNamespace(path="/api/test"),
    )
    response = SimpleNamespace(status_code=201)
    log_args = {}

    async def fake_call_next(request_arg):
        assert request_arg is request
        return response

    counter = {"calls": 0}

    def fake_time():
        counter["calls"] += 1
        return 1.0 if counter["calls"] == 1 else 1.05

    def fake_info(msg, *args):
        log_args["msg"] = msg
        log_args["args"] = args

    monkeypatch.setattr("app.middleware.logging.time.time", fake_time)
    monkeypatch.setattr("app.middleware.logging.logger.info", fake_info)

    middleware = object.__new__(RequestLoggingMiddleware)
    result = asyncio.run(middleware.dispatch(request, fake_call_next))

    assert result is response
    assert log_args["msg"] == "%s %s %s %sms"
    assert log_args["args"][0] == "GET"
    assert log_args["args"][1] == "/api/test"
    assert log_args["args"][2] == 201
    assert log_args["args"][3] == 50.0
