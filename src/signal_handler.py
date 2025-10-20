from base_platform_agent import BasePlatformAgent
import signal
import os

from log import get_logger

logger = get_logger()


def handle_signals(platform_agent: BasePlatformAgent, timeout: int):

    # setup shutdown signal handler
    def handle_shutdown_signal(signum, frame):
        platform_agent.report_log(
            f"Received shutdown signal: '{signal.strsignal(signum)}'. Exiting."
        )
        exit(1)

    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)

    logger.debug("Shutdown signal handlers set for SIGINT and SIGTERM.")

    # setup timer signal
    def timeout_handler(signum, frame):
        platform_agent.report_log(f"Execution timed out after {timeout} seconds.")
        os.kill(os.getpid(), signal.SIGTERM)

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    logger.debug(f"Signal alarm set for {timeout} seconds.")
