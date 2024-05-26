import json
import logging
import runpod
import requests
import time
import sys

from unittest.mock import patch

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

BASE_URL = "http://127.0.0.1:3000"
# BASE_URL = "https://llama-cpp.lt-home-vm.xuyh0120.win"


def handle_request(r):
    r.raise_for_status()
    result = r.json()
    logging.debug(json.dumps(result))
    return result


async def handler(event):
    result = None
    try:
        logging.debug(f"Handling event {event}")
        inp = event["input"]
        openai_route = inp.get("openai_route")
        if openai_route:
            r = requests.post(BASE_URL + openai_route, json=inp["openai_input"])
            # For some reason OpenAI endpoints doesn't work unless we return a generator
            result = handle_request(r)
        else:
            r = requests.post(BASE_URL + "/completion", json=inp)
            # For some reason OpenAI endpoints doesn't work unless we return a generator
            result = handle_request(r)

    except Exception as e:
        logging.exception(f"Failed to handle event {event}")
        # For some reason OpenAI endpoints doesn't work unless we return a generator
        result = {"error": repr(e)}

    yield result


if __name__ == "__main__":
    while True:
        logging.info(f"Waiting for llama.cpp to start")
        try:
            r = requests.get(
                BASE_URL,
                timeout=120,
            )
            break
        except Exception as e:
            logging.info(f"llama.cpp is not ready: {repr(e)}")
            time.sleep(0.5)

    logging.info("Starting serverless handler")
    with patch("runpod.serverless.modules.rp_local.sys.exit") as mock:
        mock.side_effect = lambda exit_code: (
            sys.exit(exit_code)
            if exit_code != 0
            else logging.info("Ignoring sys.exit from serverless handler")
        )
        runpod.serverless.start({"handler": handler, "return_aggregate_stream": True})

    logging.info(
        "Serverless handler exited, waiting indefinitely to not consume GPU resources"
    )
    while True:
        time.sleep(1)
