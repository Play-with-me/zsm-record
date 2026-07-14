import os
import urllib.request
import urllib.parse
import base64
import sys
import time
import json
from io import BytesIO
try:
    from PIL import Image
except ImportError:
    os.system('pip install pillow')
    from PIL import Image

def generate_prompt(item, desc, action, style, color):
    return f"A high-quality retro pixel art illustration (16-bit or 8-bit style), depicting a central {item} with distinct {desc} properties. The {item} is {action}, positioned in the center of the image. The pixel art style is clean and crisp, featuring {style}. The background is solid black color, and the lighting is {color} lighting."

items_info = {
    "Khung Gỗ": ("avatar frame", "wooden texture and square border", "glowing slightly", "vibrant earthy colors", "soft top"),
    "Khung Bạc": ("avatar frame", "shiny silver and metallic", "shimmering", "sharp edges and metallic highlights", "bright reflective"),
    "Khung Vàng": ("avatar frame", "luxurious gold", "sparkling with gold dust", "rich yellow and golden gradients", "warm glowing"),
    "Khung Kim Cương": ("avatar frame", "diamond and icy crystalline", "radiating cold blue energy", "icy blue facets", "intense bright blue"),
    "Khung Lửa Đỏ": ("avatar frame", "fire and animated flames", "burning with glowing red and orange energy", "vibrant fiery colors", "intense warm"),
    "Khung Hắc Ám": ("avatar frame", "dark aura and black-purple mist", "emitting sinister dark energy", "deep purple and black gradients", "eerie glowing"),
    "Huy Hiệu Tập Sự": ("novice badge shield", "bronze metal and simple design", "shining faintly", "earthy bronze and brown colors", "soft top"),
    "Huy Hiệu Cao Thủ": ("pro badge shield", "silver wings and sharp metallic", "gleaming brightly", "sharp metallic silver and blue colors", "bright reflective"),
    "Huy Hiệu Tốc Độ": ("speed badge", "golden lightning bolt and tire", "sparkling with electricity", "dynamic yellow and golden colors", "intense bright"),
    "Huy Hiệu Huyền Thoại": ("legendary badge shield", "crown and diamond", "radiating legendary aura", "rich multi-colored glowing gradients", "ethereal glowing"),
    "Huy Hiệu Rồng Lửa": ("fire dragon badge", "fierce red and orange dragon head shaped shield", "breathing fire", "vibrant red and orange scales", "intense warm"),
    "Huy Hiệu Hắc Ám": ("dark badge shield", "sinister purple and black design with skull motif", "pulsing with dark energy", "deep purple and black colors", "eerie glowing")
}

icons = {}

for name, (item, desc, action, style, color) in items_info.items():
    prompt = generate_prompt(item, desc, action, style, color)
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=128&height=128&nologo=true&seed=42"
    
    success = False
    for attempt in range(3):
        print(f"Generating {name}... (Attempt {attempt+1})")
        sys.stdout.flush()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                data = response.read()
                img = Image.open(BytesIO(data)).convert("RGBA")
                
                # Make black pixels transparent
                if hasattr(img, 'getdata'):
                    datas = img.getdata()
                else:
                    datas = img.get_flattened_data()
                newData = []
                for item_pixel in datas:
                    if item_pixel[0] < 50 and item_pixel[1] < 50 and item_pixel[2] < 50:
                        newData.append((255, 255, 255, 0))
                    else:
                        newData.append(item_pixel)
                img.putdata(newData)
                
                buffered = BytesIO()
                img.save(buffered, format="WEBP", quality=80)
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                icons[name] = f"data:image/webp;base64,{img_str}"
                print(f"Success {name}!")
                sys.stdout.flush()
                success = True
                break
        except Exception as e:
            print(f"Error for {name}: {e}")
            sys.stdout.flush()
            time.sleep(2)
            
    if not success:
        print(f"Failed to generate {name} after 3 attempts.")
        sys.stdout.flush()

with open("pollinations_icons.json", "w", encoding="utf-8") as f:
    json.dump(icons, f, ensure_ascii=False, indent=4)
print("Saved to pollinations_icons.json!")
