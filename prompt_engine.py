
import json
import random
from pathlib import Path

# Load style config
CONFIG_PATH = Path(__file__).parent / "style_config.json"
with open(CONFIG_PATH) as f:
    STYLE_CONFIG = json.load(f)

def generate_prompt(animal: str, background_buckets: list[str], override_style: str = None) -> dict:
    # Choose style (use override if valid)
    style = override_style if override_style in STYLE_CONFIG else random.choice(list(STYLE_CONFIG.keys()))
    style_data = STYLE_CONFIG[style]

    # Required traits
    traits = list(style_data.get("core_traits", []))

    # Optional traits (0–3 randomly)
    optional = style_data.get("optional_traits", [])
    traits += random.sample(optional, k=random.randint(0, min(3, len(optional))))

    # Deduplicate traits
    traits = list(set(traits))

    # Background (one of your trained templates)
    background = random.choice(background_buckets)

    # Construct LoRA tokens
    loras = []
    if style_data.get("lora_tag"):
        loras.append(f"<lora:{style_data['lora_tag']}:{style_data['lora_weight']}>")
    loras.append("<lora:daniml_V2:0.2>")
    loras.append(f"<lora:daniml_V2_{animal.lower()}:0.6>")

    # Build final positive prompt
    traits_str = ", ".join(traits)
    prompt = f"{' '.join(loras)} stylized anthropomorphic {animal.lower()}, {traits_str}, {background}"

    # Consistent negative prompt
    negative = "two, double, multiple, duplicate, extra character, second animal, twin, copy, tail"

    return {
        "prompt": prompt,
        "negative_prompt": negative,
        "style": style,
        "traits": traits
    }
