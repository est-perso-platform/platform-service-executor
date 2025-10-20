# Platform Service Executor

This module is a base for implementing Perso Platform service executors.

## Development Steps

### Development Environment Setup

Create a `.env.local` file at the root of the project and reference `.env.base` file to setup your own environment.

Use Visual Studio Code to confirm debugging with your own environment variable file works.

### Creating your own `PlatformAgent` by subclassing `BasePlatformAgent`

The executor expects a `PlatformAgent` class at `src/platform_agent.py`. You should implement `PlatformAgent.execute_task()` function, that accepts `input_values: dict[str, str | float | bool | None]` and outputs a `dict[str, str | float | bool | None]`, as defined in the Platform service input schema.

#### Logging

There are two types of logging scheme available inside `PlatformAgent.execute_task()`, `logger.info()` and `PlatformAgent.report_log(self, message: str)`. 

Note that you should use `PlatformAgent.report_log(self, message: str)` to log messages that is visable to the user. If the log message contains information that should not be shown to the user, you should use `logger.info()`.

#### Reporting Status

If `PlatformAgent.execute_task()` is finished and all output values are returned, the executor will automatically report `PlatformStatusEnum.SUCCESS`.

However, if a task fails, you should report `PlatformStatusEnum.FAILED` with `failure_reason` using `PlatformAgent.update_status(status: PlatformStatusEnum, failure_reason: PlatformFailureReasonEnum | None = None)`. You should always report `failure_reason` when reporting failed status.

### Building and Pushing

Use the supplied Makefile to build and push the docker container.

```sh
make build IMAGE=persolive.azurecr.io/executor-speech-to-face-v2 TAG=v2
make push IMAGE=persolive.azurecr.io/executor-speech-to-face-v2 TAG=v2
```
