from http.client import responses
from time import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from utils.logger import Logger


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger: Logger = Logger(level=Logger.LoggingLevelEnum.INFO.value)
        request.state.logger = logger

        start_time: int = int(round(time() * 1000))
        response: Response = await call_next(request)
        end_time: int = int(round(time() * 1000))

        logger.log_info(
            (
                f" {request.method}:{request.url}"
                f" | {responses[response.status_code]}"
                f" | {start_time}"
                f" | {end_time}"
            )
        )
        return response
