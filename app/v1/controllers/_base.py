from typing import Any, TypeVar

from pydantic import BaseModel
from utils.logger import Logger

BaseSchemaT = TypeVar("BaseSchemaT", bound=BaseModel)


class BaseController:
    def __init__(self, *, logger: Logger, verbose: bool = True) -> None:
        self.logger = logger
        self.verbose = verbose

    def schema_validation(self, schema: BaseSchemaT, data: Any) -> BaseSchemaT:
        self.logger.log_info(f"[input] {data}")
        parsed_model: BaseSchemaT = schema.model_validate(data)
        return parsed_model
