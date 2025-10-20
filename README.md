# Platform Service Executor

This module is a base for implementing Perso Platform Service executors.

## Development Steps

### 1. Development Environment Setup

Clone this repository to make it easy to merge future updates of the Platform Service Executor.

Create a `.env.local` file at the root of the project and reference `.env.base` file to setup your own environment.

```
.env.local

SERVICEEXECUTION_ID=pse-1234
PLATFORM_HOST=https://stage-platform.perso.ai
PLATFORM_PRESHARED_KEY=plspsk-1234
TIMEOUT=60
```

Use Visual Studio Code to confirm debugging (`F5`) with your own environment variable file works.

### 2. Creating your own `PlatformAgent` by subclassing `BasePlatformAgent`

The executor expects a `PlatformAgent` class subclassing `BasePlatformAgent` at `src/platform_agent.py`.

You should specify `PlatformAgent.service_name`. It should match the service name specified in the Platform Service.

You should implement `PlatformAgent.execute_task(input_values: dict[str, str | float | bool | None])` function that accepts `input_values: dict[str, str | float | bool | None]` and outputs a `dict[str, str | float | bool | None]`, as defined in the Platform Service input schema. If outputting a file, specify the location of the file.

```python
class PlatformAgent(BasePlatformAgent):
    service_name = "speech-to-face-v1"

    def input_values(self, input_values: dict[str, str | float | bool | None]):
        return {
            "output_string": "Hello World",
            "output_number": 123,
            "output_file": "/tmp/output.mp4",
        }
```

### 3. Logging

There are two types of logging scheme available inside `PlatformAgent.execute_task()`, `logger.info()` and `PlatformAgent.report_log(self, message: str)`. 

you should use `PlatformAgent.report_log(message: str)` to log messages that is visable to the user.

Note that if the log message contains information that should not be shown to the user, you should use `logger.info()`.

```python
class PlatformAgent(BasePlatformAgent):
    service_name = "speech-to-face-v1"

    def input_values(self, input_values: dict[str, str | float | bool | None]):
        self.report_log(f"Starting {self.service_name}")

        logger.info("Using Elevenlabs API Key: sk_1234")
```



### 4. Reporting Status

If `PlatformAgent.execute_task()` is finished and all output values are returned, the executor will automatically report `PlatformStatusEnum.SUCCESS`.

However, if a task fails, you should report `PlatformStatusEnum.FAILED` with `failure_reason` using `PlatformAgent.update_status(status: PlatformStatusEnum, failure_reason: PlatformFailureReasonEnum | None = None)`. You should always report `failure_reason` when reporting failed status. It is best to report verbose failure reason using `PlatformAgent.report_log(message: str)`.


```python
class PlatformAgent(BasePlatformAgent):
    service_name = "speech-to-face-v1"

    def input_values(self, input_values: dict[str, str | float | bool | None]):
        try:
            result = 1 / 0
        except ZeroDivisionError:
            self.report_log("Error occured while calculating numbers.")
            self.update_status(status=PlatformStatusEnum.FAILED, failure_reason=PlatformFailureReasonEnum.SERVER_ERROR)
```


### 5. Building and Pushing

Use the supplied Makefile to build and push the docker container.

```sh
make build IMAGE=persolive.azurecr.io/executor-speech-to-face-v2 TAG=v2
make push IMAGE=persolive.azurecr.io/executor-speech-to-face-v2 TAG=v2
```
