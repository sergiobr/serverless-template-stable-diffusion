# This file is used to verify your http server acts as expected
# Run it with `python3 test.py``
import argparse
import datetime
import json
import logging
import os
import sys
import time
from uuid import uuid4

import requests

# model_inputs = {'prompt': 'realistic field of grass'}
model_inputs = {
    'enable_animation_mode': True,
    'settings': './runSettings_Template.txt',
    'model': 'v1-5-pruned-emaonly.ckpt'
}

res = requests.post('http://localhost:8000/', json=model_inputs)

call_inputs = {
    "test_url": "http://localhost:8000/"
    # "MODEL_ID": "CompVis/stable-diffusion-v1-4"
}


# print(res.json())

# Deforum
# python run.py --enable_animation_mode --settings "./runSettings_Template.txt" --model "v1-5-pruned-emaonly.ckpt"

# runinference(
#        {
#            "modelInputs": {
#				'enable_animation_mode': True,
#				'settings': './runSettings_Template.txt',
#				'model': 'v1-5-pruned-emaonly.ckpt'
#			},
#            "callInputs": {
#                #"train": "dreambooth",
#                #"MODEL_ID": "CompVis/stable-diffusion-v1-4"
#            },
#        },
#    )

# def main(args, extraCallInputs, extraModelInputs):
# runinference(args, extraCallInputs, extraModelInputs)


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_url", required=False, type=str)
    # parser.add_argument("--xmfe", required=False, action="store_true")

    parser.add_argument("--banana", required=False, action="store_true")
    parser.add_argument("--runpod", required=False, action="store_true")

    """" 
    parser.add_argument(
        "--xmfe",
        required=False,
        default=None,
        type=lambda x: bool(distutils.util.strtobool(x)),
    )
    parser.add_argument("--call-arg", action="append", type=str)
    parser.add_argument("--model-arg", action="append", type=str)
    """
    parser.add_argument(
        "--settings",
        type=str,
        default="./examples/runSettings_Animation.txt",
        help="Settings file",
    )

    parser.add_argument(
        "--enable_animation_mode",
        default=False,
        action='store_true',
        help="Enable animation mode settings",
    )

    parser.add_argument(
        "--model",
        default="v1-5-pruned-emaonly.ckpt",
        help="Model .ckpt file",
        type=str,
        required=False
    )

    # parser.add_argument("--scheduler", required=False, type=str)
    # args = parser.parse_known_args()
    opt = parser.parse_args(args)
    print("opt", opt)

    import json

    # Read settings files
    def load_file_args(path):
        with open(path, "r") as f:
            loaded_args = json.load(f)  # , ensure_ascii=False, indent=4)
        return loaded_args

    master_args = load_file_args(opt.settings)

    # call_inputs = {}
    # model_inputs = {}

    # runinference(args, "", True)

    # def runinference(args, BANANA_API_URL="https://api.banana.dev", TEST_URL=True):
    inputs = {
        "modelInputs": model_inputs,
        "callInputs": call_inputs,
    }
    #inputs.get("callInputs").update(extraCallInputs)
    #inputs.get("modelInputs").update(extraModelInputs)

    print("Running inference: ")

    inputs_to_log = {
        "modelInputs": inputs["modelInputs"].copy(),
        "callInputs": inputs["callInputs"].copy(),
    }
    model_inputs_to_log = inputs_to_log["modelInputs"]

    # for key in ["init_image", "image"]:
    #    if key in model_inputs_to_log:
    #        model_inputs_to_log[key] = "[image]"

    # instance_images = model_inputs_to_log.get("instance_images", None)
    # if instance_images:
    #    model_inputs_to_log["instance_images"] = f"[Array({len(instance_images)})]"

    print(json.dumps(inputs_to_log, indent=4))
    print()

    start = time.time()

    if opt.banana:
        BANANA_API_KEY = os.getenv("BANANA_API_KEY")
        BANANA_MODEL_KEY = os.getenv("BANANA_MODEL_KEY")
        BANANA_API_URL = os.getenv("BANANA_API_URL", "https://api.banana.dev")

        if BANANA_MODEL_KEY is None or BANANA_API_KEY is None:
            print("Error: BANANA_API_KEY or BANANA_MODEL_KEY not set, aborting...")
            sys.exit(1)

        payload = {
            "id": str(uuid4()),
            "created": int(time.time()),
            "apiKey": BANANA_API_KEY,
            "modelKey": BANANA_MODEL_KEY,
            "modelInputs": inputs,
            "startOnly": False,
        }
        response = requests.post(f"{BANANA_API_URL}/start/v4/", json=payload)
        result = response.json()
        callID = result.get("callID")

        if not result.get("finished", None):
            while result.get(
                    "message", None
            ) != "success" and not "error" in result.get("message", None):
                secondsSinceStart = time.time() - start
                print(str(datetime.datetime.now()) + f": t+{secondsSinceStart:.1f}s")
                print(json.dumps(result, indent=4))
                payload = {
                    "id": str(uuid4()),
                    "created": int(time.time()),
                    "longPoll": True,
                    "apiKey": BANANA_API_KEY,
                    "callID": callID,
                }
                response = requests.post(f"{BANANA_API_URL}/check/v4/", json=payload)
                result = response.json()

        modelOutputs = result.get("modelOutputs", None)
        if modelOutputs is None:
            finish = time.time() - start
            print(f"Request took {finish:.1f}s")
            print(result)
            return
        result = modelOutputs[0]
    elif opt.runpod:
        RUNPOD_API_URL = "https://api.runpod.ai/v1/"
        RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
        RUNPOD_MODEL_KEY = os.getenv("RUNPOD_MODEL_KEY")
        if not (RUNPOD_API_KEY and RUNPOD_MODEL_KEY):
            print("Error: RUNPOD_API_KEY or RUNPOD_MODEL_KEY not set, aborting...")
            sys.exit(1)

        url_base = RUNPOD_API_URL + RUNPOD_MODEL_KEY

        payload = {
            "input": inputs,
        }
        print(url_base + "/run")
        response = requests.post(
            url_base + "/run",
            json=payload,
            headers={"Authorization": "Bearer " + RUNPOD_API_KEY},
        )

        if response.status_code != 200:
            print("Unexpected HTTP response code: " + str(response.status_code))
            sys.exit(1)

        print(response)
        result = response.json()
        print(result)

        id = result["id"]

        while result["status"] != "COMPLETED":
            time.sleep(1)
            response = requests.get(
                f"{url_base}/status/{id}",
                headers={"Authorization": "Bearer " + RUNPOD_API_KEY},
            )
            result = response.json()

        result = result["output"]

    else:
        test_url = opt.test_url = "http://localhost:8000"
        response = requests.post(test_url, json=inputs)
        print("response ===> ", response)
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError as error:
            print(error)
            print(response.text)
            sys.exit(1)

    finish = time.time() - start
    print("result ===> ", result)
    timings = None #result.get("$timings")

    if timings:
        timings_str = json.dumps(
            dict(
                map(
                    lambda item: (
                        item[0],
                        f"{item[1] / 1000 / 60:.1f}m"
                        if item[1] > 60000
                        else f"{item[1] / 1000:.1f}s"
                        if item[1] > 1000
                        else str(item[1]) + "ms",
                    ),
                    timings.items(),
                )
            )
        ).replace('"', "")[1:-1]
        print(f"Request took {finish:.1f}s ({timings_str})")
    else:
        print(f"Request took {finish:.1f}s")

    if result:
        if (
                result.get("images_base64", None) is None
                and result.get("image_base64", None) is None
        ):
            error = result.get("$error", None)
            if error:
                code = error.get("code", None)
                name = error.get("name", None)
                message = error.get("message", None)
                stack = error.get("stack", None)
                if code and name and message and stack:
                    print()
                    title = f"Exception {code} on container:"
                    print(title)
                    print("-" * len(title))
                    print(f'{name}("{message}")')  # stack includes it.
                    print(stack)
                    return

            print(json.dumps(result, indent=4))
            print()
            return result

if __name__ == "__main__":
    print("Starting...")
    logging.basicConfig(level=logging.INFO)
    logging.log(logging.INFO, "Starting...")
    logging.log(logging.INFO,"sys.argv: " + str(sys.argv))

    main(sys.argv[1:])
