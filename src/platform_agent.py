from base_platform_agent import (
    BasePlatformAgent,
    PlatformStatusEnum,
    PlatformFailureReasonEnum,
)


from log import get_logger

logger = get_logger()


class PlatformAgent(BasePlatformAgent):
    service_name = ""

    def execute_task(
        self,
        input_values: dict[str, str | float | bool | None],
    ) -> dict[str, str | float | bool | None]:
        # your task execution logic here
        return {}
