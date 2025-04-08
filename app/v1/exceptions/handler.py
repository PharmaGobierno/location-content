import sys
import traceback
from functools import wraps

from fastapi import Request, Response, status
from presentation.errors import BaseError, DefaultError, NotFoundError
from presentation.helpers import add_errors_to_response, destructuring
from presentation.response import Response as APIResponse
from pydantic import ValidationError
from utils.logger import Logger


def exception_handler(response_status=status.HTTP_200_OK):
    """Decorator to handle resource exceptions"""

    def wrapper(func):
        """Exception handler for resource logic"""

        @wraps(func)
        async def wrapped_func(request: Request, response: Response, *args, **kwargs):
            logger: Logger = request.state.logger
            api_response = APIResponse(process_id=logger.process_id)
            try:
                api_response.status = response_status
                api_response.update_data(await func(request, response, *args, **kwargs))
            except BaseError as error:
                api_response.status = error.http_status
                api_response.add_error(error)
            except ValidationError as error:
                api_response.status = status.HTTP_400_BAD_REQUEST
                all_errors = destructuring(error.errors())
                logger.log_error(str(all_errors))  # logging pydantic validation errors
                add_errors_to_response(api_response, all_errors)
            except Exception as e:
                _, _, tb = sys.exc_info()
                logger.log_error(f"Unexpected Error! {type(e)} {str(e)}")
                logger.log_error(f"Traceback: {traceback.format_tb(tb)}")
                api_response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
                api_response.add_error(DefaultError())
            response.status_code = api_response.status
            return api_response.response

        return wrapped_func

    return wrapper
