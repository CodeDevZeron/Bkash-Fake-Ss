import os
import io
import requests
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import traceback

app = Flask(__name__)

# ImgBB API Key (Vercel এ সেট করতে হবে)
IMAGEBB_API_KEY = os.environ.get("IMAGEBB_API_KEY", None)

@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({
        "error": str(e),
        "trace": traceback.format_exc()
    }), 500

@app.route("/api/bkash", methods=["GET"])
def generate_bkash():
    # Params
    number = request.args.get("number", "01811111111")
    transactionId = request.args.get("transaction", "730MGQG6GH")
    amount = int(request.args.get("amount", 10000))
    totalWithExtra = amount + 10

    # Date & Time
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    dayMonthYear = now.strftime("%d/%m/%y")

    # File paths
    base_dir = os.path.dirname(__file__)
    bg_path = os.path.join(base_dir, "zeron.jpg")
    font1_path = os.path.join(base_dir, "roboto.ttf")
    font2_path = os.path.join(base_dir, "roboto2.ttf")

    # Load background
    background = Image.open(bg_path).convert("RGBA")
    draw = ImageDraw.Draw(background)

    # Fonts
    font1 = ImageFont.truetype(font1_path, 55)
    font2 = ImageFont.truetype(font2_path, 60)
    font_small = ImageFont.truetype(font2_path, 47)

    color = (90, 90, 90)

    # Texts
    draw.text((400, 850), number, fill=color, font=font1)
    draw.text((400, 950), number, fill=color, font=font2)

    text_w, _ = draw.textsize(transactionId, font=font2)
    image_w = background.size[0]
    draw.text((image_w - 384 - text_w, 1430), transactionId, fill=color, font=font2)

    draw.text((175, 1880), f"{amount} +10.39", fill=color, font=font1)
    draw.text((170, 1768), str(totalWithExtra), fill=color, font=font2)

    draw.text((135, 1421), time_str, fill=color, font=font1)
    draw.text((439, 1420), dayMonthYear, fill=color, font=font1)
    draw.text((50, 109), time_str, fill=color, font=font_small)

    # Save buffer
    img_bytes = io.BytesIO()
    background.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    if not IMAGEBB_API_KEY:
        return jsonify({"error": "IMAGEBB_API_KEY not set in environment"}), 500

    # Upload to ImgBB
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": IMAGEBB_API_KEY},
        files={"image": ("bkash.png", img_bytes, "image/png")}
    )

    if response.status_code == 200:
        img_url = response.json()["data"]["url"]
        return jsonify({
            "API By": "@DevZeron",
            "Image": img_url,
            "number": number,
            "transactionId": transactionId,
            "amount": amount,
            "totalWithExtra": totalWithExtra,
            "time": time_str,
            "date": dayMonthYear
        })
    else:
        return jsonify({
            "error": "Image upload failed",
            "details": response.text
        }), 500

@app.route("/")
def home():
    return jsonify({"message": "BKash API Running ✅", "by": "@DevZeron"})
