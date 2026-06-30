import csv
import io
import os
import urllib.request
import json
from PIL import Image, ImageDraw, ImageFont

SHEET_ID = "1o6ii8ybMhqMdOY4AwW54Z6bplhO4MgXEYvRZO8xhVZo"
GID = "2102406431"
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

def fetch_leaderboard():
    with urllib.request.urlopen(CSV_URL) as r:
        content = r.read().decode("utf-8")
    reader = csv.reader(io.StringIO(content))
    rows = []
    for row in reader:
        if len(row) >= 4 and row[1].strip().isdigit():
            rank = row[1].strip()
            name = row[2].strip()
            earnings = row[3].strip()
            rows.append((rank, name, earnings))
    return rows

def make_image(entries):
    W, H = 600, 120 + len(entries) * 110 + 80
    img = Image.new("RGB", (W, H), color="#1a1a2e")
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_rank = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_earn = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except:
        font_title = font_header = font_rank = font_name = font_earn = ImageFont.load_default()

    draw.text((60, 30), "LEADERBOARD", fill="#FFFFFF", font=font_title)
    draw.line([(60, 85), (420, 85)], fill="#c8a84b", width=3)
    draw.text((110, 100), "CHATTER", fill="#888888", font=font_header)
    draw.text((360, 100), "EARNINGS", fill="#888888", font=font_header)

    rank_colors = ["#c8a84b", "#FFFFFF", "#cd7f32"]
    name_colors = ["#c8a84b", "#FFFFFF", "#FFFFFF"]

    for i, (rank, name, earnings) in enumerate(entries):
        y = 140 + i * 110
        row_color = "#16213e" if i % 2 == 0 else "#0f3460"
        draw.rounded_rectangle([(50, y), (550, y + 80)], radius=10, fill=row_color)
        rc = rank_colors[i] if i < len(rank_colors) else "#FFFFFF"
        nc = name_colors[i] if i < len(name_colors) else "#FFFFFF"
        draw.text((75, y + 22), rank, fill=rc, font=font_rank)
        draw.text((130, y + 24), name, fill=nc, font=font_name)
        draw.text((360, y + 24), earnings, fill="#FFFFFF", font=font_earn)

    draw.text((60, H - 50), "Auto-sorted by earnings", fill="#555555", font=font_header)
    path = "/tmp/leaderboard.png"
    img.save(path)
    return path

def send_photo(path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(path, "rb") as f:
        photo_data = f.read()
    boundary = "boundary123"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
        f"{CHAT_ID}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="photo"; filename="leaderboard.png"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + photo_data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read())
        print("Sent:", result.get("ok"))

entries = fetch_leaderboard()
print("Entries:", entries)
img_path = make_image(entries)
send_photo(img_path)
