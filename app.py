import torch
from torch import autocast
import base64
from io import BytesIO
import os
import run as deforum


# Init is ran on server startup
# Load your model to GPU as a global variable here using the variable name "model"
def init():
    global model
    HF_AUTH_TOKEN = os.getenv("HF_AUTH_TOKEN")
    print("init")


# Inference is ran for every server call
# Reference your preloaded global model variable here.
def inference(model_inputs: dict) -> dict:
    global model

    # Parse out your arguments
    settings = model_inputs.get('settings', './examples/runSettings_StillImages.txt')
    enable_animation_mode = model_inputs.get('enable_animation_mode', False)
    model = model_inputs.get('model', 'v1-5-pruned-emaonly.ckpt')
    model_config = model_inputs.get('model_config', 'v1-inference.yaml')

    # If "seed" is not sent, we won't specify a seed in the call
    generator = None
    # if input_seed != None:
    #    generator = torch.Generator("cuda").manual_seed(input_seed)

    # if prompt == None:
    #    return {'message': "No prompt provided"}

    # Run the model
    with autocast("cuda"):
        mp4_path, gif_path = deforum.main(model_inputs)

    # run command on system and add the result output to a variable called link
    #link_mp4 = os.system(f"rclone link gdrive:/{mp4_path.replace('/root/')}")
    link_mp4 = os.popen(f"rclone link gdrive:/{mp4_path.replace('/root/gdrive/')}").read()

    if gif_path:
        link_gif = os.popen(f"rclone link gdrive:/{gif_path.replace('/root/gdrive/')}").read
    # create a variable result with a json object replacing variables with their values then return it
    result = {
        "mp4_path": link_mp4,
        "gif_path": link_gif,
    }
    return result
