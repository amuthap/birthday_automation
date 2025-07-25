import csv
import os
import requests
import base64
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Picnie API configuration
PICNIE_API_KEY = "$U63b6a6bf2d13775853e1dba410ffb4cb"  # API key with $ prefix
PICNIE_API_URL = "https://picnie.com/api/v1/remove-background"

# ─── Configuration ────────────────────────────────────────────────────────────
TEMPLATE_PATH = "template.png"  # Path to your template image
CSV_PATH      = "our_team_details.csv"
IMAGES_DIR    = "images"
OUTPUT_DIR    = "output"

# Font files (adjust these if needed)
FONT_NAME_PATH    = "arialbd.ttf"
FONT_ADDRESS_PATH = "arial.ttf"
FONT_ROLE_PATH    = "arial.ttf"

# Font sizes
SIZE_NAME    = 36
SIZE_ADDRESS = 30
SIZE_ROLE    = 28

# Profile‐photo size & position (matches your template)
PHOTO_W, PHOTO_H = 364, 369
PHOTO_X, PHOTO_Y = 652, 362

# Spacing
LINE_SPACING   = 8
TEXT_MARGIN    = 15  # gap between bottom of photo and top of text

# ─── Helpers ──────────────────────────────────────────────────────────────────
def format_today():
    now = datetime.now()
    return f"{now.month:02d}/{now.day:02d}/{now.year}"

def download_image(url, dest_path):
    resp = requests.get(url)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(resp.content)

def draw_multiline_centered(draw, lines, x_center, y_start, fonts, spacing):
    y = y_start
    for line, font in zip(lines, fonts):
        bbox = draw.textbbox((0,0), line, font=font)
        w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text((x_center - w/2, y), line, font=font, fill="black")
        y += h + spacing

def upload_to_picnie(image_path):

    url = 'https://picnie.com/api/v1/upload-asset'
    api_key = PICNIE_API_KEY  # Replace with your actual API key
    file_path = image_path  # Ensure this path is correct and the file exists

    headers = {
        'Authorization': api_key
    }

    files = {
        'image': open(file_path, 'rb')
    }

    response = requests.post(url, headers=headers, files=files)

    # Print the response
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
    response_data = response.json()  # Convert the response text to a dictionary

    # Extract image_url
    image_url = response_data.get('image_url')
    print("Image URL:", image_url)

    return image_url

def remove_background_picnie(image_path):
    """Remove background from image using Picnie API"""
    print(f"Using API Key: {PICNIE_API_KEY}")
    
    # First create a project if we don't have one
    project_id = 2542
    if not project_id:
        print("❌ Failed to create Picnie project")
        return None
    
    # Upload the image to get a URL
    image_url = upload_to_picnie(image_path)
    if not image_url:
        print("❌ Failed to upload image to Picnie")
        return None
    
    # Now remove the background
    headers = {
        'Authorization': PICNIE_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'image_url': image_url,
        'project_id': project_id
    }
    
    
    response = requests.post(PICNIE_API_URL, headers=headers, json=data)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
    response_data = response.json()  # Convert the response text to a dictionary

    # Extract image_url
    image_url = response_data.get('image_url')
    print("Image URL:", image_url)
    return image_url

def create_picnie_image(path, size, radius=30):
    print ("insdie create picnie_image",path)
    url = 'https://picnie.com/api/v1/create-image'
    api_key = PICNIE_API_KEY  # Replace with your actual API key

    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    data = {
        "project_id": 2542,
        "template_id": 6017,
        "template_name": "user_226/project_251/RO.png",
        "type": "image",
        "output_image_quality": "High",
        "output_image_format": "png",
        "details": [
            {
                "name": "background_image",
                "image_url": "https://picnie.s3.ap-south-1.amazonaws.com/user_226/project_2542/rm_bg_687f05b6f1518.png"
                
            },
            {
                "name": "Title_0",
                "text": "@reallygreatsite"
            },
            {
                "name": "Title_1",
                "text": "One step at a time, Youll get there"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    # Parse the response
    if response.status_code == 200:
        result = response.json()
        print("Response Body:", result,"\n", result.get('url', 'Image URL not found'))
        
        # Extract image URL if available
        image_url = result.get('url')
        if image_url:
            print("Crom create image Generated Image URL:", image_url)
        else:
            print("from create image Image URL not found in response.")
    else:
        print("from create image Request failed with status code: {response.status_code}")
        print("from create image Response Body:", response.text)


def create_rounded_image(path, size, radius=30):
    # First try to remove background
    img = Image.open(path).convert("RGB")
    img_no_bg = remove_background_picnie(path)
    
    # If background removal failed, use original image
    if img_no_bg is None:
        img_no_bg = img
    
    # Resize and apply rounding
    img_no_bg = img_no_bg.resize(size)
    mask = Image.new("L", size, 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle((0,0,*size), radius=radius, fill=255)
    rounded = ImageOps.fit(img_no_bg, size, centering=(0.5,0.5))
    rounded.putalpha(mask)
    return rounded

# ─── Main ────────────────────────────────────────────────────────────────────
def send_whatsapp_message(phone, image_path, name):
    API_URL = "https://app.d4digitalsolutions.com/send-media"
    API_KEY = "RuHmTiiVT3u3OpD1DVfz6dlLJvMnPH"
    SENDER_NUMBER = "919042092105"
    
    # Format the caption with proper name and message
    caption = (
        f"Dear *Rtn.{name}*, \n\n"
        "Wishing you a very special BIRTHDAY and a wonderful year ahead! "
        "Many more happy returns of the day!! \n\n"
        "Rtn.PHF.PP.SRINIVASAN RAMDOSS \n"
        "District Chairman-Greetings\n"
        "2025-26"
    )
    
    # Use a public image URL for WhatsApp API (local file paths will not work)
    # For now, use a static image URL as in your PHP example
    public_image_url = "https://rotasmart.club/greetings/images/Srini_BDay.jpg"
    data = {
        'api_key': API_KEY,
        'sender': SENDER_NUMBER,
        'number': f"91{phone}",
        'media_type': 'image',
        'caption': caption,
        'url': image_path if image_path.startswith("http") else public_image_url
    }
    
    try:
        response = requests.post(API_URL, data=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"✅ WhatsApp message sent successfully to {name}")
        return True
    except Exception as e:
        print(f"❌ Failed to send WhatsApp message to {name}: {e}")
        return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load fonts
    font_name    = ImageFont.truetype(FONT_NAME_PATH, SIZE_NAME)
    font_address = ImageFont.truetype(FONT_ADDRESS_PATH, SIZE_ADDRESS)
    font_role    = ImageFont.truetype(FONT_ROLE_PATH, SIZE_ROLE)

    today = format_today()
    def normalize_date(date_str):
        parts = date_str.strip().split('/')
        if len(parts) == 3:
            month = str(int(parts[0]))
            day = str(int(parts[1]))
            year = parts[2]
            return f"run{month}/{day}/{year}"
        return date_str.strip()
    print(f"Looking for birthdays on {today}…")

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_date = row["Date"].strip()
            if normalize_date(row_date) != normalize_date(today):
                print(f"Skipping {row.get('Name', '[No Name]')} (Date: {row_date}) - does not match today ({today})")
                continue

            name    = row["Name"].strip()
            club    = row["Address"].strip()
            role    = row["Roll"].strip()
            img_url = row["image"].strip()


            safe_name = name.replace(" ", "_")
            img_path  = os.path.join(OUTPUT_DIR, f"{safe_name}_profile.jpg")

            # If the URL contains 'rotary-logo.png', use 'noImage.jpg' instead
            if 'rotary-logo.png' in img_url:
                print(f"Using noImage.jpg for {name} instead of rotary-logo.png")
                img_path = "noImage.jpg"
            else:
                # Always download photo from URL
                try:
                    print(f"Downloading image for {name} from {img_url}")
                    download_image(img_url, img_path)
                except Exception as e:
                    print(f"❌ ERROR: Failed to download image for {name} ({img_url}): {e}")
                    continue
            #create_picnie_image(img_url, (PHOTO_W, PHOTO_H), radius=30)
            # Open template
            try:
                base = Image.open(TEMPLATE_PATH).convert("RGB")
            except Exception as e:
                print(f"❌ ERROR: Failed to open template '{TEMPLATE_PATH}': {e}")
                continue
            draw = ImageDraw.Draw(base)

            # Paste rounded profile photo in the exact placeholder
            try:
            # Output file path for the profile image
                    profile_path = os.path.join(OUTPUT_DIR, f"{safe_name}_profile.jpg")
            
            # Get image URL with background removed
                    profile_url = remove_background_picnie(img_path)
                    print("Profile URL:", profile_url, " profile:", profile_path)

            # Download the processed image
                    download_image(profile_url, profile_path)

            # Open and resize the image
                    profile_img = Image.open(profile_path).convert("RGBA")
                    profile_img = profile_img.resize((PHOTO_W, PHOTO_H), Image.Resampling.LANCZOS)

            # Use alpha channel (if available) as mask
                    if profile_img.mode == "RGBA":
                        alpha = profile_img.getchannel("A")
                        base.paste(profile_img, (PHOTO_X, PHOTO_Y), mask=alpha)
                    else:
                        base.paste(profile_img, (PHOTO_X, PHOTO_Y))

            except Exception as e:
                    print(f"❌ ERROR: Failed to process or paste profile image for {name}: {e}")
                    continue

            # Draw Name / Address / Roll just below the photo
            TEXT_X_CENTER = PHOTO_X + PHOTO_W // 2
            TEXT_Y_START  = PHOTO_Y + PHOTO_H + TEXT_MARGIN
            lines = [name.upper(), club.upper(), role.upper()]
            fonts = [font_name, font_address, font_role]
            try:
                draw_multiline_centered(draw, lines, TEXT_X_CENTER, TEXT_Y_START, fonts, LINE_SPACING)
            except Exception as e:
                print(f"❌ ERROR: Failed to draw text for {name}: {e}")
                continue

            # Save output
            out_path = os.path.join(OUTPUT_DIR, f"{safe_name}_birthday.jpg")
            try:
                base.save(out_path)
                print(f"✅ Created: {out_path}")
                # Upload to Picnie and get the URL
                out_url = upload_to_picnie(out_path)
                if not out_url:
                    print(f"❌ ERROR: Failed to upload image for {name} to Picnie")
                else:
                    print(f"✅ Uploaded to Picnie: {out_url}")
                # Get WhatsApp number from the row data (assuming it's in the Phone or WhatsApp column)
                whatsapp_number = (row.get("WhatsApp") or row.get("Phone") or "").strip()

                if whatsapp_number:
                    # Send WhatsApp message with the generated image
                    send_whatsapp_message(whatsapp_number, out_url, name)
                else:
                    print(f"⚠️ No WhatsApp number found for {name}, skipping message")
                
            except Exception as e:
                print(f"❌ ERROR: Failed to save output for {name} to '{out_path}': {e}")

    print("🎉 All done!")

if __name__ == "__main__":
    main()
