from platform_agent import PlatformAgent
from signal_handler import handle_signals
from argument_parser import parse_arguments
import socket
from log import get_logger

logger = get_logger()


def main():
    args = parse_arguments()

    # initialize platform agent
    platform_agent = PlatformAgent(
        platform_host=args.platform_host,
        platform_preshared_key=args.platform_preshared_key,
        serviceexecution_id=args.serviceexecution_id,
    )

    logger.debug("Platform agent initialized.")

    handle_signals(platform_agent, args.timeout)

    platform_agent.report_log(
        f"Starting {platform_agent.service_name} at worker {socket.gethostname()}."
    )

    platform_agent.start()


if __name__ == "__main__":
    main()
