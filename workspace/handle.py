import json
import logging
import runpod
import requests
import time
import sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

BASE_URL = "http://127.0.0.1:3000"
# BASE_URL = "https://llama-cpp.lt-home-vm.xuyh0120.win"


def handle_request(r):
    r.raise_for_status()
    result = r.json()
    logging.info(json.dumps(result))
    return result


async def handler(event):
    try:
        logging.info(f"Handling event {event}")
        inp = event["input"]
        openai_route = inp.get("openai_route")
        if openai_route:
            r = requests.post(BASE_URL + openai_route, json=inp["openai_input"])
            # For some reason OpenAI endpoints doesn't work unless we return a generator
            yield handle_request(r)

        r = requests.post(BASE_URL + "/completion", json=inp)
        # For some reason OpenAI endpoints doesn't work unless we return a generator
        yield handle_request(r)

    except Exception as e:
        logging.exception(f"Failed to handle event {event}")
        # For some reason OpenAI endpoints doesn't work unless we return a generator
        yield {"error": repr(e)}


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
    runpod.serverless.start({"handler": handler, "return_aggregate_stream": True})
