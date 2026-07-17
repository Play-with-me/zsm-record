import base64
import re
from PIL import Image, ImageDraw
import io

icons_data_path = r"backend\app\icons_data.py"

with open(icons_data_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find all entries that are Khung ...
# format: 'Khung Name': 'data:image/jpeg;base64,...'
pattern = re.compile(r"('Khung [^']+':\s*'data:image/[a-zA-Z]+;base64,)([^']+)'")

def mask_image(match):
    prefix = match.group(1)
    b64_data = match.group(2)
    
    try:
        img_data = base64.b64decode(b64_data)
        img = Image.open(io.BytesIO(img_data)).convert("RGBA")
        
        draw = ImageDraw.Draw(img)
        width, height = img.size
        # Mask out center circle
        margin_x = width * 0.16
        margin_y = height * 0.16
        draw.ellipse((margin_x, margin_y, width - margin_x, height - margin_y), fill=(0, 0, 0, 255))
        
        out_buffer = io.BytesIO()
        img.save(out_buffer, format="PNG")
        new_b64 = base64.b64encode(out_buffer.getvalue()).decode("utf-8")
        
        # We also need to change the data URI to png just in case it was jpeg
        prefix = prefix.replace("image/jpeg", "image/png").replace("image/webp", "image/png")
        return f"{prefix}{new_b64}'"
    except Exception as e:
        print("Error processing image:", e)
        return match.group(0)

new_content = pattern.sub(mask_image, content)

with open(icons_data_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Processed all Khung images.")
