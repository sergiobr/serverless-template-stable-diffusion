# This file is used to verify your http server acts as expected
# Run it with `python3 test.py``

import requests
import base64
from io import BytesIO
from PIL import Image

#model_inputs = {'prompt': 'realistic field of grass'}
model_inputs = {
				'enable_animation_mode': True,
				'settings': './runSettings_Template.txt',
				'model': 'v1-5-pruned-emaonly.ckpt'
			   }

res = requests.post('http://localhost:8000/', json = model_inputs)

call_inputs = {}

#image_byte_string = res.json()["image_base64"]
print(res.json())
#image_encoded = image_byte_string.encode('utf-8')
#image_bytes = BytesIO(base64.b64decode(image_encoded))
#image = Image.open(image_bytes)
#image.save("output.jpg")

# Deforum 
# python run.py --enable_animation_mode --settings "./runSettings_Template.txt" --model "v1-5-pruned-emaonly.ckpt"

def runInference(args): #, extraCallInputs, extraModelInputs):
    #origInputs = all_tests.get(name)
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

    #for key in ["init_image", "image"]:
    #    if key in model_inputs_to_log:
    #        model_inputs_to_log[key] = "[image]"

    #instance_images = model_inputs_to_log.get("instance_images", None)
    #if instance_images:
    #    model_inputs_to_log["instance_images"] = f"[Array({len(instance_images)})]"

    print(json.dumps(inputs_to_log, indent=4))
    print()

    start = time.time()
    if args.get("banana", None):
        BANANA_API_KEY = os.getenv("BANANA_API_KEY")
        BANANA_MODEL_KEY = os.getenv("BANANA_MODEL_KEY")
        if BANANA_MODEL_KEY == None or BANANA_API_KEY == None:
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

        if result.get("finished", None) == False:
            while result.get(
                "message", None
            ) != "success" and not "error" in result.get("message", None):
                secondsSinceStart = time.time() - start
                print(str(datetime.datetime.now()) + f": t+{secondsSinceStart:.1f}s")
                print(json.dumps(result, indent=4))
                print
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
        if modelOutputs == None:
            finish = time.time() - start
            print(f"Request took {finish:.1f}s")
            print(result)
            return
        result = modelOutputs[0]
    elif args.get("runpod", None):
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
        test_url = args.get("test_url", None) or TEST_URL
        response = requests.post(test_url, json=inputs)
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError as error:
            print(error)
            print(response.text)
            sys.exit(1)

    finish = time.time() - start
    timings = result.get("$timings")

    if timings:
        timings_str = json.dumps(
            dict(
                map(
                    lambda item: (
                        item[0],
                        f"{item[1]/1000/60:.1f}m"
                        if item[1] > 60000
                        else f"{item[1]/1000:.1f}s"
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

    if (
        result.get("images_base64", None) == None
        and result.get("image_base64", None) == None
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
                # print(f'{name}("{message}")') - stack includes it.
                print(stack)
                return

        print(json.dumps(result, indent=4))
        print()
        return result

    #images_base64 = result.get("images_base64", None)
    #if images_base64:
        #for idx, image_byte_string in enumerate(images_base64):
            #images_base64[idx] = decode_and_save(image_byte_string, f"{name}_{idx}")
    #else:
        #result["image_base64"] = decode_and_save(result["image_base64"], name)

    print()
    print(json.dumps(result, indent=4))
    print()
    return result

#runInference(
#        {
#            "modelInputs": {#
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

def main(args, extraCallInputs, extraModelInputs):
	runInference(args, extraCallInputs, extraModelInputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--banana", required=False, action="store_true")
    parser.add_argument("--runpod", required=False, action="store_true")
    parser.add_argument(
        "--xmfe",
        required=False,
        default=None,
        type=lambda x: bool(distutils.util.strtobool(x)),
    )
    parser.add_argument("--scheduler", required=False, type=str)
    parser.add_argument("--call-arg", action="append", type=str)
    parser.add_argument("--model-arg", action="append", type=str)

    args, tests_to_run = parser.parse_known_args()

    call_inputs = {}
    model_inputs = {}

    if args.call_arg:
        for arg in args.call_arg:
            name, value = arg.split("=", 1)
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit():
                value = float(value)
            call_inputs.update({name: value})

    if args.model_arg:
        for arg in args.model_arg:
            name, value = arg.split("=", 1)
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit():
                value = float(value)
            model_inputs.update({name: value})

    if args.xmfe != None:
        call_inputs.update({"xformers_memory_efficient_attention": args.xmfe})
    if args.scheduler:
        call_inputs.update({"SCHEDULER": args.scheduler})

    #if len(tests_to_run) < 1:
    #    print(
    #        "Usage: python3 test.py [--banana] [--xmfe=1/0] [--scheduler=SomeScheduler] [all / test1] [test2] [etc]"
    #    )
    #    sys.exit()
    #elif len(tests_to_run) == 1 and (
    #    tests_to_run[0] == "ALL" or tests_to_run[0] == "all"
    #):
    #    tests_to_run = list(all_tests.keys())

    main(
        tests_to_run,
        vars(args),
        extraCallInputs=call_inputs,
        extraModelInputs=model_inputs,
    )
