from argparse import ArgumentParser, Namespace
import os
import json
from log import get_logger

logger = get_logger()


def parse_arguments():
    # Parse Arguments in the order of:
    # JSON Input File > Command Line Args > Environment Variables > Defaults

    arguments = {
        "serviceexecution_id": None,
        "platform_host": "https://platform.perso.ai",
        "platform_preshared_key": None,
        "timeout": 60,
        "json_input_file": "/input/inputs.json",
    }

    arguments = {
        "serviceexecution_id": "pse-dde2ab8f62bd1c5349546afa705786a5",
        "platform_host": "http://localhost:8000",
        "platform_preshared_key": "plspsk-84997c5004f8dc85792a875f55c9147f",
        "timeout": 60,
        "json_input_file": "/input/inputs.json",
    }

    if serviceexecution_id := os.getenv("SERVICEEXECUTION_ID"):
        arguments["serviceexecution_id"] = serviceexecution_id
    if platform_host := os.getenv("PLATFORM_HOST"):
        arguments["platform_host"] = platform_host
    if platform_preshared_key := os.getenv("PLATFORM_PRESHARED_KEY"):
        arguments["platform_preshared_key"] = platform_preshared_key
    if timeout := os.getenv("TIMEOUT"):
        arguments["timeout"] = int(timeout)
    if json_input_file := os.getenv("JSON_INPUT_FILE"):
        arguments["json_input_file"] = json_input_file

    parser = ArgumentParser()
    parser.add_argument(
        "--serviceexecution_id",
        type=str,
        required=False,
        help="Service Execution ID",
    )
    parser.add_argument(
        "--platform-host",
        type=str,
        required=False,
        help="Platform host URL",
    )
    parser.add_argument(
        "--platform-preshared-key",
        type=str,
        required=False,
        help="Platform preshared key for authentication",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        required=False,
        help="Timeout for the execution in seconds",
    )
    parser.add_argument(
        "--json-input-file",
        type=str,
        required=False,
        help="Path to JSON file containing inputs for the task",
    )

    args = parser.parse_args()

    if args.serviceexecution_id:
        arguments["serviceexecution_id"] = args.serviceexecution_id
    if args.platform_host:
        arguments["platform_host"] = args.platform_host
    if args.platform_preshared_key:
        arguments["platform_preshared_key"] = args.platform_preshared_key
    if args.timeout:
        arguments["timeout"] = args.timeout

    if args.json_input_file:
        arguments["json_input_file"] = args.json_input_file

    try:
        with open(arguments["json_input_file"], "r") as f:
            json_inputs = json.load(f)
            for key in [
                "serviceexecution_id",
                "platform_host",
                "platform_preshared_key",
                "timeout",
            ]:
                if key in json_inputs:
                    arguments[key] = json_inputs[key]
    except FileNotFoundError:
        logger.debug(
            f"JSON input file '{arguments['json_input_file']}' not found. Skipping."
        )

    arguments.pop("json_input_file")

    for key in [
        "serviceexecution_id",
        "platform_host",
        "platform_preshared_key",
        "timeout",
    ]:
        if arguments[key] is None:
            raise ValueError(f"Argument '{key}' is required but not provided.")

    logger.debug("Resolved Config:")
    for key, value in arguments.items():
        logger.debug(f"    {key}: {value}")

    return Namespace(**arguments)
