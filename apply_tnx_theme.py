import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Title and Meta
content = content.replace('<title>ZSM Record - Thư viện Record ZingSpeed Mobile</title>', '<title>TNX Record - Tenvyx Clan ZingSpeed Mobile</title>')
content = content.replace('content="Lưu trữ, tìm kiếm và xem bảng xếp hạng record ZingSpeed Mobile."', 'content="Kho lưu trữ và bảng xếp hạng kỷ lục tốc độ của Tenvyx Clan (TNX) - ZingSpeed Mobile."')

# 2. Add Rajdhani font
content = content.replace('family=Inter:wght@400;500;600;700;800;900&display=swap', 'family=Inter:wght@400;500;600;700;800;900&family=Rajdhani:wght@600;700;800&display=swap')

# 3. Colors and Theme
content = content.replace('--bg: #050508;', '--bg: #080608;')
content = content.replace('--bg-card: rgba(15,15,25,0.7);', '--bg-card: rgba(18,10,10,0.75);')
content = content.replace('--border-active: rgba(139,92,246,0.6);', '--border-active: rgba(220,38,38,0.6);')
content = content.replace('--red: #f87171;', '--red: #dc2626;\n      --red-light: #ef4444;\n      --red-glow: rgba(220,38,38,0.4);')

# 4. BG Mesh -> Speed lines
old_mesh = '''    /* BG mesh */
    body::before {
      content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
      background: radial-gradient(ellipse 80% 50% at 20% -10%, rgba(59,130,246,0.08) 0%, transparent 60%),
                  radial-gradient(ellipse 60% 40% at 80% 110%, rgba(139,92,246,0.08) 0%, transparent 60%);
    }'''
new_mesh = '''    /* Speed lines BG */
    body::before {
      content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
      background:
        radial-gradient(ellipse 70% 50% at 10% 20%, rgba(220,38,38,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 90% 80%, rgba(220,38,38,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 80% 30% at 50% 0%, rgba(30,10,10,0.9) 0%, transparent 70%);
    }
    body::after {
      content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
      background-image:
        repeating-linear-gradient(105deg, transparent 0px, transparent 80px, rgba(220,38,38,0.018) 80px, rgba(220,38,38,0.018) 81px),
        repeating-linear-gradient(105deg, transparent 0px, transparent 140px, rgba(255,255,255,0.012) 140px, rgba(255,255,255,0.012) 141px);
    }'''
content = content.replace(old_mesh, new_mesh)

# 5. Logo CSS
old_logo_css = '''    .logo {
      font-size:1.2rem; font-weight:900; letter-spacing:-0.04em; flex-shrink:0;
      background:linear-gradient(135deg, var(--blue), var(--purple-light));
      -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    }'''
new_logo_css = '''    .logo {
      font-size:1.4rem; font-weight:900; letter-spacing:-0.04em; flex-shrink:0;
      display:flex; align-items:center; gap:8px;
      color:var(--red); font-family:'Rajdhani', sans-serif; text-transform:uppercase;
      text-shadow: 0 0 10px rgba(220,38,38,0.3); transition: transform 0.3s ease;
    }
    .logo:hover { transform: scale(1.05); }'''
content = content.replace(old_logo_css, new_logo_css)

# 6. Grad class
old_grad = '''    .grad {
      background:linear-gradient(135deg, var(--blue-hover), var(--purple-light));
      -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    }'''
new_grad = '''    .grad {
      background:linear-gradient(135deg, var(--red-light), var(--red));
      -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    }'''
content = content.replace(old_grad, new_grad)

# 7. Hero Title CSS
old_hero_grad = '''    .hero .grad { background:linear-gradient(135deg,var(--blue),var(--purple-light),#e879f9); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }'''
new_hero_grad = '''    .hero .grad {
      background:linear-gradient(135deg, var(--red-light), var(--red), #fca5a5);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
      font-family:'Rajdhani', sans-serif; text-transform:uppercase;
    }'''
content = content.replace(old_hero_grad, new_hero_grad)

# 8. Add Animations CSS
anim_css = '''    /* Animations */
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes pulseGlow { 0% { box-shadow: 0 0 0 0 var(--red-glow); } 70% { box-shadow: 0 0 0 10px rgba(220,38,38,0); } 100% { box-shadow: 0 0 0 0 rgba(220,38,38,0); } }
    @keyframes slideInLeft { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
    .animate-up { animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; }
    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }
    .card-hover { transition: transform 0.3s cubic-bezier(0.16,1,0.3,1), box-shadow 0.3s ease; }
    .card-hover:hover { transform: translateY(-4px); box-shadow: 0 10px 25px -5px rgba(220,38,38,0.15); border-color: rgba(220,38,38,0.3); }
'''
content = content.replace('/* SCROLLBAR */', anim_css + '\n    /* SCROLLBAR */')

# 9. Navbar Logo HTML
old_nav = '<a href="#/" class="logo">ZSM Record</a>'
new_nav = '<a href="#/" class="logo"><img src="Logo-clan.jpg" alt="TNX" style="height:32px; width:auto; border-radius:4px; object-fit:contain;"/> TNX Record</a>'
content = content.replace(old_nav, new_nav)

# 10. Hero Content
old_hero = '''      <h1>Thư Viện Record<br><span class="grad">ZingSpeed Mobile</span></h1>
      <p>Khám phá, chia sẻ và so sánh các kỷ lục đỉnh cao của cộng đồng.</p>'''
new_hero = '''      <h1 class="animate-up">Kho Dữ Liệu Tốc Độ<br><span class="grad" style="font-size:1.1em;">TENVYX CLAN (TNX)</span></h1>
      <p class="animate-up delay-1" style="color:var(--text-muted);font-size:1.1rem;line-height:1.6;">Lưu trữ, vinh danh kỷ lục và chia sẻ kỹ năng của các tay đua xuất sắc nhất thuộc Tenvyx Clan.</p>'''
content = content.replace(old_hero, new_hero)
content = content.replace('<div class="hero-actions">', '<div class="hero-actions animate-up delay-2">')
content = content.replace('<div class="hero-stats" id="hero-stats">', '<div class="hero-stats animate-up delay-3" id="hero-stats">')

# 11. Auth Text & Password Eyes
def make_eye(name, placeholder, extra):
    return f'''<div style="position:relative;">
        <input class="form-input" type="password" name="{name}" placeholder="{placeholder}" required {extra} style="padding-right:40px;"/>
        <button type="button" onclick="const i=this.previousElementSibling; if(i.type==='password'){{i.type='text';this.innerHTML='&#128064;'}}else{{i.type='password';this.innerHTML='&#128065;'}}" style="position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--text-muted);font-size:1.1rem;cursor:pointer;transition:color 0.2s;">&#128065;</button>
      </div>'''

# Login
login_p_old = '<input class="form-input" type="password" name="p" placeholder="Nhập mật khẩu" required />'
login_p_new = make_eye('p', 'Nhập mật khẩu', '')
content = content.replace(login_p_old, login_p_new)
content = content.replace('<p class="auth-desc">Chào mừng trở lại, tay đua!</p>', '<p class="auth-desc">Chào mừng trở lại căn cứ TNX!</p>')

# Register
reg_p_old = '<input class="form-input" type="password" name="p" placeholder="Tối thiểu 6 ký tự" required minlength="6"/>'
reg_p_new = make_eye('p', 'Tối thiểu 6 ký tự', 'minlength="6"')
reg_c_old = '<input class="form-input" type="password" name="c" placeholder="Nhập lại mật khẩu" required />'
reg_c_new = make_eye('c', 'Nhập lại mật khẩu', '')
content = content.replace(reg_p_old, reg_p_new)
content = content.replace(reg_c_old, reg_c_new)
content = content.replace('<p class="auth-desc">Tham gia cộng đồng ZSM Record!</p>', '<p class="auth-desc">Trở thành tay đua chính thức của Tenvyx Clan!</p>')

# Add some pulse to the primary button
content = content.replace('class="btn btn-primary"', 'class="btn btn-primary" style="animation: pulseGlow 2s infinite;"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
