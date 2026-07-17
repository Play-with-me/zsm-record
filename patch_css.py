import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Variables
vars_old = """    :root {
      --bg: #080608;
      --bg-card: rgba(18,10,10,0.75);
      --bg-input: rgba(0,0,0,0.5);
      --border: rgba(255,255,255,0.07);
      --border-active: rgba(220,38,38,0.6);
      --text: #f0f0f5;
      --text-muted: #9c9cae;
      --text-dim: #7a7a8f;
      --blue: #3b82f6;
      --blue-hover: #60a5fa;
      --purple: #8b5cf6;
      --purple-light: #a78bfa;
      --green: #34d399;
      --red: #dc2626;
      --red-light: #ef4444;
      --red-glow: rgba(220,38,38,0.4);
      --orange: #fb923c;
      --yellow: #fbbf24;
      --radius: 12px;
      --radius-lg: 18px;
      --transition: color 0.18s ease, background-color 0.18s ease, border-color 0.18s ease, opacity 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
      --neon-cyan: #0ff;
      --neon-pink: #f0f;
      --neon-blue: #00f3ff;
      --neon-purple: #b537f2;
      --neon-glow-cyan: 0 0 10px rgba(0, 255, 255, 0.5), 0 0 20px rgba(0, 255, 255, 0.3);
      --neon-glow-pink: 0 0 10px rgba(255, 0, 255, 0.5), 0 0 20px rgba(255, 0, 255, 0.3);
      --neon-glow-purple: 0 0 10px rgba(181, 55, 242, 0.5), 0 0 20px rgba(181, 55, 242, 0.3);
    }"""
vars_new = """    :root {
      --bg: #090a0f;
      --bg-card: rgba(20, 22, 30, 0.85);
      --bg-input: rgba(10, 12, 18, 0.8);
      --border: rgba(255,255,255,0.06);
      --border-active: #d4af37;
      --text: #f8f9fa;
      --text-muted: #9ca3af;
      --text-dim: #6b7280;
      --blue: #1d4ed8;
      --blue-hover: #2563eb;
      --purple: #1e1b4b;
      --purple-light: #4c1d95;
      --green: #10b981;
      --red: #be123c;
      --red-light: #f43f5e;
      --red-glow: rgba(190, 18, 60, 0.4);
      --orange: #f59e0b;
      --yellow: #fbbf24;
      --gold: #d4af37;
      --gold-glow: rgba(212, 175, 55, 0.4);
      --radius: 0px;
      --radius-lg: 0px;
      --transition: all 0.2s cubic-bezier(0.16,1,0.3,1);
      /* Refined Esports Neon */
      --neon-cyan: #38bdf8;
      --neon-pink: #e11d48;
      --neon-blue: #2563eb;
      --neon-purple: #d4af37;
      --neon-glow-cyan: 0 0 15px rgba(56, 189, 248, 0.25);
      --neon-glow-pink: 0 0 15px rgba(225, 29, 72, 0.25);
      --neon-glow-purple: 0 0 15px rgba(212, 175, 55, 0.25);
    }"""
content = content.replace(vars_old, vars_new)

# 2. Backgrounds
bg_old = """    /* Speed lines BG */
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
    }"""
bg_new = """    /* Esports Grid BG */
    body::before {
      content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
      background: radial-gradient(ellipse 80% 80% at 50% -20%, rgba(190, 18, 60, 0.15) 0%, transparent 60%);
    }
    body::after {
      content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
      background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
      background-size: 40px 40px;
      mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%);
      -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%);
    }"""
content = content.replace(bg_old, bg_new)

# 3. Clip Path Buttons
btn_old = """    .btn {
      display:inline-flex; align-items:center; justify-content:center; gap:7px;
      padding:9px 18px; border-radius:8px; font-size:0.85rem; font-weight:600;
      border:none; transition:var(--transition); white-space:nowrap; cursor:pointer;
    }"""
btn_new = """    .btn {
      display:inline-flex; align-items:center; justify-content:center; gap:7px;
      padding:10px 22px; font-size:0.85rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;
      border:none; transition:var(--transition); white-space:nowrap; cursor:pointer;
      clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
    }"""
content = content.replace(btn_old, btn_new)

# Cards Clip path
card_old = """    /* CARDS */
    .card {
      background:var(--bg-card); border:1px solid var(--border);
      border-radius:var(--radius);
      transition:var(--transition);
    }
    .card-hover:hover { border-color:var(--neon-purple); transform:translateY(-2px); box-shadow:var(--neon-glow-purple); }"""
card_new = """    /* CARDS */
    .card {
      background:var(--bg-card); border:1px solid var(--border);
      transition:var(--transition);
      clip-path: polygon(0 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%);
    }
    .card-hover:hover { border-color:var(--gold); transform:translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.5); }"""
content = content.replace(card_old, card_new)

# Remove speed streaks and cyberpunk floating orbs
old_speed = """    /* ── Animated speed streaks ────────────────────── */"""
new_speed = """    .speed-streaks, .speed-streak, .speed-particle, .speed-bg, .cyberpunk-bg, .cyberpunk-grid, .glow-orb { display: none !important; }
    /* ── Animated speed streaks ────────────────────── */"""
content = content.replace(old_speed, new_speed)

# Form inputs clip path
form_old = """    .form-input {
      width:100%; padding:10px 13px; border-radius:8px; font-size:0.85rem;
      background:var(--bg-input); border:1px solid var(--border); color:var(--text);
      transition:var(--transition); outline:none;
    }"""
form_new = """    .form-input {
      width:100%; padding:10px 13px; font-size:0.85rem;
      background:var(--bg-input); border:1px solid var(--border); color:var(--text);
      transition:var(--transition); outline:none;
      clip-path: polygon(8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%, 0 8px);
    }"""
content = content.replace(form_old, form_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated index.html CSS successfully.")
