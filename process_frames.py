from PIL import Image, ImageDraw
import base64
import os
import re

images = {
    "Khung Băng Tuyết": r"C:\Users\LEGION\.gemini\antigravity\brain\21f4ca35-56b5-4763-937d-027a4a8cb8a5\frame_ice_1_1784018180002.jpg",
    "Khung Không Gian": r"C:\Users\LEGION\.gemini\antigravity\brain\21f4ca35-56b5-4763-937d-027a4a8cb8a5\frame_space_1_1784018198428.jpg",
    "Khung Vương Miện": r"C:\Users\LEGION\.gemini\antigravity\brain\21f4ca35-56b5-4763-937d-027a4a8cb8a5\frame_crown_1_1784018248143.jpg",
    "Khung Phượng Hoàng": r"C:\Users\LEGION\.gemini\antigravity\brain\21f4ca35-56b5-4763-937d-027a4a8cb8a5\frame_phoenix_1_1784018258010.jpg",
}

icons_data_path = r"backend\app\icons_data.py"

with open(icons_data_path, "r", encoding="utf-8") as f:
    content = f.read()

for name, path in images.items():
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        
        # We need to black out a circle in the center.
        draw = ImageDraw.Draw(img)
        width, height = img.size
        # The frame size is 128x128. Let's make the center circle black.
        margin_x = width * 0.16
        margin_y = height * 0.16
        draw.ellipse((margin_x, margin_y, width - margin_x, height - margin_y), fill=(0, 0, 0, 255))
        
        temp_path = path + ".tmp.png"
        img.save(temp_path, "PNG")
        
        with open(temp_path, "rb") as img_file:
            b64_str = base64.b64encode(img_file.read()).decode("utf-8")
            
        pattern = f"('{name}':\\s*'data:image/[a-zA-Z]+;base64,)[^']+'"
        # use regex sub to replace the base64 string
        content = re.sub(pattern, f"\\g<1>{b64_str}'", content)

with open(icons_data_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated icons_data.py with masked images.")
