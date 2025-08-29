import csv, os, re, time, requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ─── Config ──────────────────────────────────────────────────────────────────
TEMPLATE_PATH = "template.png"
CSV_PATH = "our_team_details.csv"
OUTPUT_DIR = "output"

# Picnie
PICNIE_API_KEY = "$U63b6a6bf2d13775853e1dba410ffb4cb"
PICNIE_UPLOAD_URL = "https://picnie.com/api/v1/upload-asset"

# Font files
FONT_NAME_PATH = os.path.join(os.path.dirname(__file__), "Fonts", "ARIALBD.TTF")
FONT_ADDRESS_PATH = os.path.join(os.path.dirname(__file__), "Fonts", "ARIAL.TTF")
FONT_ROLE_PATH = os.path.join(os.path.dirname(__file__), "Fonts", "ARIAL.TTF")
#FONT_NAME_PATH = "arialbd.ttf"
#FONT_ADDRESS_PATH = "arial.ttf"
#FONT_ROLE_PATH = "arial.ttf"
SIZE_NAME, SIZE_ADDRESS, SIZE_ROLE = 36, 30, 28

# Photo placement
PHOTO_W, PHOTO_H = 364, 369
PHOTO_X, PHOTO_Y = 652, 362
LINE_SPACING, TEXT_MARGIN = 8, 15

# WhatsApp API
API_URL = "https://app.d4digitalsolutions.com/send-media"
API_KEY = "w96Yx9YgUxaIfFQPKJNr2HmPTSpIjC"
SENDER_NUMBER = "919150281224"

# Groups (IDs only, no @g.us)
GROUP_IDS = [
    "120363314164316321","120363202664832172","120363183272810504",
    "919445298001-1532168871","919788864442-1632333227","919842694845-1422978468",
    "919942904575-1570156592","919842118542-1487664244","120363198539639457",
    "917010153530-1573039790","919894744499-1626851462","919360399990-1606973063",
]

GROUP_CAPTION = (
    "நீண்ட நீண்ட காலம்  நீடு வாழவேண்டும். இனிய பிறந்த நாள் வாழ்த்துகள்\n\n"
    "https://rotasmart.club/greetings/b/\n\n"
    "Greetings from\nRtn.PHF.PP.SRINIVASAN RAMDOSS \nDistrict Chairman-Greetings\n2025-26"
)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def format_today():
    n = datetime.now()
    return f"{n.month:02d}/{n.day:02d}/{n.year}"

def normalize_date(s: str) -> str:
    parts = s.strip().split("/")
    if len(parts) == 3:
        return f"{int(parts[0])}/{int(parts[1])}/{parts[2]}"
    return s.strip()

def digits_only(s: str) -> str:
    d = re.sub(r"\D", "", s or "")
    if len(d) > 10:  # keep last 10 (India)
        d = d[-10:]
    return d

def download_image(url, dest_path):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(r.content)

def draw_multiline_centered(draw, lines, x_center, y_start, fonts, spacing):
    y = y_start
    for line, font in zip(lines, fonts):
        w, h = draw.textlength(line, font=font), draw.textbbox((0,0), line, font=font)[3] - draw.textbbox((0,0), line, font=font)[1]
        draw.text((x_center - w/2, y), line, font=font, fill="black")
        y += h + spacing

def upload_to_picnie(image_path):
    with open(image_path, "rb") as f:
        r = requests.post(PICNIE_UPLOAD_URL, headers={"Authorization": PICNIE_API_KEY}, files={"image": f}, timeout=45)
    print("Upload Status Code:", r.status_code)
    print("Upload Response:", r.text)
    r.raise_for_status()
    return r.json().get("image_url", "")

def send_whatsapp_message(phone_digits, image_url, name):
    caption = (
        f"Dear *Rtn.{name}*, \n\n"
        "Wishing you a very special BIRTHDAY and a wonderful year ahead! "
        "Many more happy returns of the day!! \n\n"
        "Rtn.PHF.PP.SRINIVASAN RAMDOSS \n"
        "+91 98940 45150 \n"
        "District Chairman-Greetings\n"
        "2025-26"
    )
    data = {
        "api_key": API_KEY,
        "sender": SENDER_NUMBER,
        "number": f"91{phone_digits}",       # expects 10 digits
        "media_type": "image",
        "caption": caption,
        "url": image_url,
    }
    r = requests.post(API_URL, data=data, timeout=45)
    r.raise_for_status()
    print(f"✅ WhatsApp DM sent to {name}")
    return True

def send_group_media(group_id, image_url, caption):
    data = {
        "api_key": API_KEY,
        "sender": SENDER_NUMBER,
        "number": f"{group_id}@g.us",
        "media_type": "image",
        "caption": caption,
        "url": image_url,
    }
    r = requests.post(API_URL, data=data, timeout=45)
    r.raise_for_status()
    return True

def delete_files_in_directory(directory_path):
        """Deletes all files within a specified directory."""
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    delete_files_in_directory(OUTPUT_DIR)

    font_name = ImageFont.truetype(FONT_NAME_PATH, SIZE_NAME)
    font_address = ImageFont.truetype(FONT_ADDRESS_PATH, SIZE_ADDRESS)
    font_role = ImageFont.truetype(FONT_ROLE_PATH, SIZE_ROLE)

    today = format_today()
    print(f"Looking for birthdays on {today}…")

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if normalize_date(row["Date"]) != normalize_date(today):
                continue

            name  = row["Name"].strip()
            club  = row["Address"].strip()
            role  = row["Roll"].strip()
            img_url = row["image"].strip()
            wa = digits_only(row.get("WhatsApp","")) or digits_only(row.get("Phone",""))
            #wa = digits_only(row.get("WhatsApp",""))
            if not wa:
                print(f"⚠️ No WhatsApp/Phone for {name}; skipping DM.")
            safe_name = name.replace(" ", "_")
            tmp_profile = os.path.join(OUTPUT_DIR, f"{safe_name}_profile.jpg")

            # profile photo
            try:
                if not img_url or "rotary-logo.png" in img_url:
                    tmp_profile = "noImage.jpg"
                else:
                    download_image(img_url, tmp_profile)
            except Exception as e:
                print(f"❌ Image download failed for {name}: {e}")
                tmp_profile = "noImage.jpg"

            # compose card
            try:
                base = Image.open(TEMPLATE_PATH).convert("RGB")
                draw = ImageDraw.Draw(base)

                pimg = Image.open(tmp_profile).convert("RGBA")
                pimg = pimg.resize((PHOTO_W, PHOTO_H), Image.Resampling.LANCZOS)
                alpha = pimg.getchannel("A") if pimg.mode == "RGBA" else None
                base.paste(pimg, (PHOTO_X, PHOTO_Y), mask=alpha)

                Xc = PHOTO_X + PHOTO_W // 2
                Ys = PHOTO_Y + PHOTO_H + TEXT_MARGIN
                lines = [name.upper(), club.upper(), role.upper()]
                fonts = [font_name, font_address, font_role]
                draw_multiline_centered(draw, lines, Xc, Ys, fonts, LINE_SPACING)

                out_path = os.path.join(OUTPUT_DIR, f"{safe_name}_birthday.jpg")
                base.save(out_path)
                print(f"✅ Created image: {out_path}")

                # upload
                out_url = upload_to_picnie(out_path)
                if not out_url:
                    print(f"❌ Upload failed for {name}"); continue

                # DM individual
                if wa:
                    try:
                        send_whatsapp_message(wa, out_url, name)
                        send_whatsapp_message("9789365651", out_url, name)

                    except Exception as e:
                        print(f"❌ DM failed for {name}: {e}")

                # Post to groups
                for gid in GROUP_IDS:
                    try:
                        #gid=gid+789456
                        send_group_media(gid, out_url, GROUP_CAPTION)
                        print(f"✅ Group sent: {gid}")
                        time.sleep(0.5)  # mild rate-limit cushion
                    except Exception as e:
                        print(f"❌ Group send failed ({gid}): {e}")

            except Exception as e:
                print(f"❌ Failed for {name}: {e}")

    print("🎉 All done!")

if __name__ == "__main__":
    main()
