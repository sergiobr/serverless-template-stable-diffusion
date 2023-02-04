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

    return mp4_path, gif_path
