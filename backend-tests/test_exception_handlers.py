import pytest
from fastapi import FastAPI

from app.exceptions.handlers import register_exception_handlers


@pytest.mark.anyio
async def test_register_exception_handlers_returns_internal_error_response():
    app = FastAPI()
    register_exception_handlers(app)
    handler = app.exception_handlers[Exception]

    response = await handler(None, RuntimeError("boom"))

    assert response.status_code == 500
    assert response.body == (
        b'{"success":false,"message":"Internal Server Error","detail":"boom"}'
    )
