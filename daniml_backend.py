import os
import random
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from prompt_engine import generate_prompt

app = Flask(__name__, static_folder='static')
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

# Load prompt buckets
with open("prompt_buckets.json", "r") as f:
    prompt_buckets = json.load(f)

@app.route("/api/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        animal = data.get("animal", "alpaca")
        selected_style = data.get("style", None)
        alias = data.get("alias", "")

        lora_background = "<lora:daniml_V2:0.2>"
        lora_animal = f"<lora:daniml_V2_{animal}:0.6>"
        lora_style = ""

        if selected_style == "gangster":
            lora_style = "<lora:daniml_V2_gangsterV2:0.85>"
        elif selected_style == "crypto_nerd":
            lora_style = "<lora:daniml_V2_cryptonerdV2:0.85>"

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
            "batch_size": 3,
            "n_iter": 1,
            "save_images": False,
            "send_images": True,
            "alwayson_scripts": {
                "seed": {
                    "args": [random.randint(1000000, 9999999)]
                }
            }
        }

        print("🔗 Sending request to A1111:", "https://3003-2600-2b00-8e-e55-00-1.ngrok-free.app/sdapi/v1/txt2img")
        response = requests.post("https://3003-2600-2b00-8e-e55-00-1.ngrok-free.app/sdapi/v1/txt2img", json=payload)
        print("🧠 SD response status:", response.status_code)
        print("🧠 SD raw text:", response.text[:500])

        try:
            r = response.json()
        except Exception as e:
            print("🔥 Could not parse JSON from SD:", e)
            return jsonify({"error": "Stable Diffusion returned invalid response"}), 500

        image_data = [f"data:image/png;base64,{img}" for img in r.get('images', [])]

        return jsonify({
            "image": image_data,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "traits": result["traits"],
            "style": selected_style
        })

    except Exception as e:
        print("🔥 API crashed:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'deGenerate.html')

if __name__ == "__main__":
    app.run(debug=True)
