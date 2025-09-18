import os
import io
import requests
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

app = Flask(__name__)

# আপনার ImageBB API key
IMAGEBB_API_KEY = os.environ.get("IMAGEBB_API_KEY", "c4d637336a678591f3844f1c56304d31")

@app.route("/api/bkash", methods=["GET"])
def generate_bkash():
    # Query Parameters
    number = request.args.get("number", "01811111111")
    transactionId = request.args.get("transaction", "730MGQG6GH")
    amount = int(request.args.get("amount", 10000))

    totalWithExtra = amount + 10

    # Date & Time
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    dayMonthYear = now.strftime("%d/%m/%y")

    # Background image (ss.jpg আপনার repo তে থাকতে হবে)
    background = Image.open("zeron.jpg").convert("RGBA")
    draw = ImageDraw.Draw(background)

    # Fonts (repo তে roboto.ttf, roboto2.ttf রাখতে হবে)
    font1 = ImageFont.truetype("roboto.ttf", 55)
    font2 = ImageFont.truetype("roboto2.ttf", 60)
    font_small = ImageFont.truetype("roboto2.ttf", 47)

    color = (90, 90, 90)

    # Text positions
    draw.text((400, 850), number, fill=color, font=font1)
    draw.text((400, 950), number, fill=color, font=font2)

    # Right align transactionId
    text_w, _ = draw.textsize(transactionId, font=font2)
    image_w = background.size[0]
    draw.text((image_w - 384 - text_w, 1430), transactionId, fill=color, font=font2)

    draw.text((175, 1880), f"{amount} +10.39", fill=color, font=font1)
    draw.text((170, 1768), str(totalWithExtra), fill=color, font=font2)

    draw.text((135, 1421), time_str, fill=color, font=font1)
    draw.text((439, 1420), dayMonthYear, fill=color, font=font1)

    draw.text((50, 109), time_str, fill=color, font=font_small)

    # Save to buffer
    img_bytes = io.BytesIO()
    background.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Upload to ImageBB
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": IMAGEBB_API_KEY},
        files={"image": img_bytes}
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
        return jsonify({"error": "Image upload failed", "details": response.text}), 500


@app.route("/")
def home():
    return jsonify({"message": "BKash API Running ✅", "by": "@DevZeron"})


if __name__ == "__main__":
    app.run(debug=True)
