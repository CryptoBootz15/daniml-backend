import os
import random
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from prompt_engine import generate_prompt

app = Flask(__name__, static_folder='static')
CORS(app)

# Load prompt buckets (backgrounds)
with open("prompt_buckets.json", "r") as f:
    prompt_buckets = json.load(f)

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    animal = data.get("animal", "alpaca")
    selected_style = data.get("style", None)
    alias = data.get("alias", "")

    # Default LoRAs
    lora_background = "<lora:daniml_V2:0.2>"
    lora_animal = f"<lora:daniml_V2_{animal}:0.6>"
    lora_style = ""

    # Determine LoRA for style
    if selected_style:
        if selected_style == "gangster":
            lora_style = "<lora:daniml_V2_gangsterV2:0.85>"
        elif selected_style == "crypto_nerd":
            # Make sure to upload the 'crypto_nerd' LoRA
            lora_style = "<lora:daniml_V2_cryptonerdV2:0.85>"  # Replace with the actual LoRA name for crypto nerd
        else:
            lora_style = ""  # No style LoRA or another default style

    # Use the modular prompt engine with the chosen LoRAs and optional user-selected style
    result = generate_prompt(animal, prompt_buckets, override_style=selected_style)
    prompt = f"{lora_background} {lora_animal} {lora_style} {result['prompt']}"
    negative_prompt = result["negative_prompt"]

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 30,
        "cfg_scale": 7,
        "width": 768,
        "height": 768,
        "sampler_name": "DPM++ 2M",
        "batch_size": 3,  # Generate 3 images
        "n_iter": 1,  # Only one iteration needed to generate the batch
        "save_images": False,
        "send_images": True,
        "alwayson_scripts": {
            "seed": {
                "args": [random.randint(1000000, 9999999)]
            }
        }
    }

    # Make the request to the image generation API
    response = requests.post("https://fa0f-2600-2b00-8e-e55-00-1.ngrok-free.app/sdapi/v1/txt2img", json=payload)
    r = response.json()
    
    # Debugging log to print out what Stable Diffusion is returning
    print("Generated Images:", r.get('images'))

    # Ensure that images are in base64 format and return them
    if 'images' in r:
        # Return the images as base64 strings
        image_data = [f"data:image/png;base64,{img}" for img in r['images']]
    else:
        image_data = None

    # Return the generated images and other data as a response
    return jsonify({
        "image": image_data,  # Return all three images in an array
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "traits": result["traits"],
        "style": selected_style
    })

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'deGenerate.html')

if __name__ == "__main__":
    app.run(debug=True)
