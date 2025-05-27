from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io
import datetime

app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    animal = data.get("animal", "Unknown")
    traits = data.get("traits", [])
    author = data.get("author", "Unknown")

    # Create a blank placeholder image
    img = Image.new("RGB", (512, 512), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    # Add wallet watermark
    watermark_text = f"{author}"
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = (img.width - text_width - 10, img.height - text_height - 10)
    draw.text(position, watermark_text, fill=(255, 255, 255), font=font)


   # Save and return the image as a proper PNG response
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return send_file(
        buf,
        mimetype='image/png',
        as_attachment=False
)


if __name__ == "__main__":
    app.run(debug=True)