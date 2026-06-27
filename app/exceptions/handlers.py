import logging

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger("reconai")


def register_exception_handlers(
    app: FastAPI
):

    @app.exception_handler(Exception)
    async def handle_exception(
        request: Request,
        exc: Exception
    ):

        logger.exception(exc)

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "message": "Internal Server Error",

                "detail": str(exc)

            }

        )
