import httpx
from enum import Enum
from pydantic import BaseModel
from abc import ABC, abstractmethod
from pydantic import BaseModel, RootModel, field_validator
from typing import List

from log import get_logger

logger = get_logger()


class PlatformStatusEnum(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PlatformFailureReasonEnum(str, Enum):
    INPUT_VALIDATION_ERROR = "INPUT_VALIDATION_ERROR"
    SERVER_ERROR = "SERVER_ERROR"


class PlatformSchemaTypeEnum(str, Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"


class PlatformFieldTypeEnum(str, Enum):
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    FILE = "FILE"


class PlatformServiceExecutionValues(BaseModel):
    schema_type: PlatformSchemaTypeEnum
    field_name: str
    field_type: PlatformFieldTypeEnum
    default_value: str | float | bool | None = None
    value: str | float | bool | None = None


class PlatformServiceExecutionValuesList(
    RootModel[List[PlatformServiceExecutionValues]]
):

    @field_validator("root")
    @classmethod
    def validate_list(cls, values):
        if len(values) == 0:
            raise ValueError("List must not be empty")
        if len(values) > 50:
            raise ValueError("List too long")
        return values


class PlatformStatusReportPayload(BaseModel):
    log: str | None = None
    status: PlatformStatusEnum | None = None
    failure_reason: PlatformFailureReasonEnum | None = None

    def validate(self):
        if not self.log and not self.status:
            raise ValueError("At least one of log or status must be provided")

        if self.status == PlatformStatusEnum.FAILED and self.failure_reason is None:
            raise ValueError("failure_reason must be provided when status is FAILED")

        if self.status != PlatformStatusEnum.FAILED and self.failure_reason is not None:
            raise ValueError("failure_reason must be None when status is not FAILED")


class BasePlatformAgent(ABC):
    def __init__(
        self, platform_host: str, platform_preshared_key: str, serviceexecution_id: str
    ):
        self.platform_host = platform_host
        self.platform_preshared_key = platform_preshared_key
        self.serviceexecution_id = serviceexecution_id
        self.client = httpx.Client(
            base_url=self.platform_host,
            headers={"PersoLiveServer-Preshared-Key": self.platform_preshared_key},
        )

    def report_log(self, message: str):
        logger.info(message)
        payload = PlatformStatusReportPayload(log=message)
        payload.validate()
        response = self.client.post(
            f"/api/services/v1/executions/{self.serviceexecution_id}/update_status/",
            json=payload.model_dump(exclude_none=True),
        )
        response.raise_for_status()

    def update_status(
        self,
        status: PlatformStatusEnum,
        failure_reason: PlatformFailureReasonEnum | None = None,
    ):
        payload = PlatformStatusReportPayload(
            status=status, failure_reason=failure_reason
        )
        payload.validate()
        response = self.client.post(
            f"/api/services/v1/executions/{self.serviceexecution_id}/update_status/",
            json=payload.model_dump(exclude_none=True),
        )
        response.raise_for_status()

    def get_values(self) -> dict[str, PlatformServiceExecutionValues]:
        response = self.client.get(
            f"/api/services/v1/executions/{self.serviceexecution_id}/get_values/",
        )
        response.raise_for_status()

        values_list = PlatformServiceExecutionValuesList.model_validate(
            response.json()
        ).root

        values_dict = {v.field_name: v for v in values_list}

        return values_dict

    @abstractmethod
    def execute_task(
        self,
        input_values: dict[str, str | float | bool | None],
    ) -> dict[str, str | float | bool | None]:
        raise NotImplementedError()

    def start(self):
        self.values = self.get_values()

        input_values = {}

        for value in self.values.values():
            if value.schema_type == PlatformSchemaTypeEnum.INPUT:
                input_values[value.field_name] = value

        self.report_log("Task execution started.")
        try:
            response = self.execute_task(input_values=input_values)
        except TypeError as e:
            # execute_task does not accept input_values
            raise
        except Exception as e:
            self.report_log(f"Task execution failed: {e}")
            raise
        self.report_log("Task execution completed.")

        response_keys = set(response.keys())

        output_keys = set(
            [
                v.field_name
                for v in self.values.values()
                if v.schema_type == PlatformSchemaTypeEnum.OUTPUT
            ]
        )

        for field_name in response.keys():
            if field_name not in output_keys:
                raise ValueError(
                    f"Field name '{field_name}' not found in output keys: {', '.join(output_keys)}."
                )

        required_output_keys = set(
            [
                v.field_name
                for v in self.values.values()
                if v.schema_type == PlatformSchemaTypeEnum.OUTPUT
                and v.default_value is None
            ]
        )

        missing_outputs = required_output_keys - response_keys

        if missing_outputs:
            raise ValueError(
                f"Output of execute_task() missing required output fields: {', '.join(missing_outputs)}"
            )

        for field_name, value in response.items():
            self.send_output(field_name, value)

    def send_output(self, field_name: str, value: str | float | bool | None):
        if not getattr(self, "values", None):
            raise ValueError("Inputs not prepared. Call prepare_task() first.")

        if field_name not in self.values:
            raise ValueError(f"Field name '{field_name}' not found in values.")

        field: PlatformServiceExecutionValues = self.values[field_name]

        if field.schema_type != PlatformSchemaTypeEnum.OUTPUT:
            raise ValueError(f"Field name '{field_name}' is not an output field.")

        if field.field_type == PlatformFieldTypeEnum.STRING:
            if not isinstance(value, str):
                raise ValueError(f"Value for field '{field_name}' must be a string.")
        elif field.field_type == PlatformFieldTypeEnum.NUMBER:
            if not isinstance(value, (int, float)):
                raise ValueError(f"Value for field '{field_name}' must be a number.")
        elif field.field_type == PlatformFieldTypeEnum.BOOLEAN:
            if not isinstance(value, bool):
                raise ValueError(f"Value for field '{field_name}' must be a boolean.")
        elif field.field_type == PlatformFieldTypeEnum.FILE:
            if not isinstance(value, str):
                raise ValueError(f"Value for field '{field_name}' must be a file path.")
            try:
                with open(value, "rb") as f:
                    pass
            except FileNotFoundError:
                raise ValueError(f"File '{value}' for field '{field_name}' not found.")

        base_url = f"/api/services/v1/executions/{self.serviceexecution_id}/upload_output/{field_name}/"

        if field.field_type == PlatformFieldTypeEnum.FILE:
            with open(value, "rb") as f:
                response = self.client.post(base_url, files={"value": f})
        else:
            json_payload = {}
            if field.field_type == PlatformFieldTypeEnum.STRING:
                json_payload["string"] = value
            elif field.field_type == PlatformFieldTypeEnum.NUMBER:
                json_payload["number"] = value
            elif field.field_type == PlatformFieldTypeEnum.BOOLEAN:
                json_payload["boolean"] = value

            response = self.client.post(base_url, json=json_payload)

        response.raise_for_status()
