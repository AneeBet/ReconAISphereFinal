import logging
import time

from starlette.middleware.base import (
    BaseHTTPMiddleware
)

from fastapi import Request


logger = logging.getLogger("reconai")


class RequestLoggingMiddleware(
    BaseHTTPMiddleware
):

    async def dispatch(
        self,
        request: Request,
        call_next
    ):

        start = time.time()

        response = await call_next(
            request
        )

        duration = round(
            (time.time() - start) * 1000,
            2
        )

        logger.info(

            "%s %s %s %sms",

            request.method,

            request.url.path,

            response.status_code,

            duration

        )

        return response
