import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_html = """<div class="speed-bg">
    <div class="speed-line" style="left:10%; animation-duration:1.2s; animation-delay:0s;"></div>
    <div class="speed-line" style="left:20%; animation-duration:1.5s; animation-delay:0.3s;"></div>
    <div class="speed-line" style="left:35%; animation-duration:0.9s; animation-delay:0.5s;"></div>
    <div class="speed-line" style="left:50%; animation-duration:1.8s; animation-delay:0.1s;"></div>
    <div class="speed-line" style="left:65%; animation-duration:1.3s; animation-delay:0.7s;"></div>
    <div class="speed-line" style="left:80%; animation-duration:1.1s; animation-delay:0.2s;"></div>
    <div class="speed-line" style="left:90%; animation-duration:1.6s; animation-delay:0.6s;"></div>
  </div>"""

content = re.sub(r'<!-- BACKGROUND ANIMATION -->.*?<div class="glow-orb purple"></div>\s*</div>', '<!-- BACKGROUND SPEED -->\n  ' + new_html, content, flags=re.DOTALL)
content = re.sub(r'<!-- Speed Streaks Animation -->.*?<div class="speed-particle"[^>]*></div>\s*</div>', '', content, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
