import base64
import os

images = {
    "Khung Băng Tuyết": r"C:\Users\LEGION\.gemini\antigravity\brain\21f4ca35-56b5-4763-937d-027a4a8cb8a5\frame_ice_1_1784018180002.jpg",
    "Khung Không Gian": r"C:\Users\LEGION\.gemini\antigravity\brain\21f4ca35-56b5-4763-937d-027a4a8cb8a5\frame_space_1_1784018198428.jpg",
    "Khung Vương Miện": r"C:\Users\LEGION\.gemini\antigravity\brain\21f4ca35-56b5-4763-937d-027a4a8cb8a5\frame_crown_1_1784018248143.jpg",
    "Khung Phượng Hoàng": r"C:\Users\LEGION\.gemini\antigravity\brain\21f4ca35-56b5-4763-937d-027a4a8cb8a5\frame_phoenix_1_1784018258010.jpg",
    "Huy Hiệu Cao Thủ": r"C:\Users\LEGION\.gemini\antigravity\brain\21f4ca35-56b5-4763-937d-027a4a8cb8a5\badge_water_1_1784018273733.jpg",
}

icons_data_path = r"backend\app\icons_data.py"

with open(icons_data_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove closing brace
content = content.strip()
if content.endswith("}"):
    content = content[:-1]
    
for name, path in images.items():
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            b64_str = base64.b64encode(img_file.read()).decode("utf-8")
            content += f",\n    '{name}': 'data:image/jpeg;base64,{b64_str}'"
    else:
        print(f"Not found: {path}")

content += "\n}\n"

with open(icons_data_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated icons_data.py")
