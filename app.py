from dotenv import load_dotenv
import os
import re
import time
import base64
import streamlit as st
import streamlit.components.v1 as components
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from collections import Counter
import requests
import urllib.parse
import io
from PIL import Image as PILImage

# ── Load ENV ─────────────────────────────────────────
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    st.error("❌ MISTRAL_API_KEY not found. Check your .env file.")
    st.stop()

# ── Page Config ──────────────────────────────────────
st.set_page_config(
    page_title="SANJU — AI Chat",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&family=Noto+Sans+Bengali:wght@400;600;700&display=swap');

:root {
    --bg-void:#02020a; --bg-panel:#0b0b1a; --bg-card:#0f0f1f; --bg-elevated:#141428;
    --border-dim:rgba(255,255,255,0.04); --border-mid:rgba(255,255,255,0.08);
    --amber:#f5a623; --violet:#7c5cbf; --teal:#2dd4bf;
    --text-0:#f0f0fa; --text-1:#a0a0c0; --text-2:#5a5a80; --text-3:#2e2e50;
    --r-sm:10px; --r-md:16px;
}
html,body,.stApp { background:var(--bg-void)!important; font-family:'Outfit','Noto Sans Bengali',sans-serif!important; color:var(--text-0)!important; }
.stApp::before { content:''; position:fixed; inset:0;
  background: radial-gradient(ellipse 80% 60% at 10% 0%,rgba(124,92,191,.12) 0%,transparent 60%),
              radial-gradient(ellipse 60% 50% at 90% 100%,rgba(245,166,35,.08) 0%,transparent 60%);
  pointer-events:none; z-index:0; }

.sanju-header { display:flex; align-items:center; gap:18px; padding:24px 4px 18px; border-bottom:1px solid var(--border-mid); margin-bottom:20px; position:relative; z-index:2; }
.sanju-emblem { position:relative; width:52px; height:52px; flex-shrink:0; }
.sanju-emblem-ring { position:absolute; inset:0; border-radius:14px; border:1.5px solid rgba(245,166,35,.5); animation:ringPulse 3s ease-in-out infinite; }
.sanju-emblem-inner { position:absolute; inset:5px; background:linear-gradient(135deg,#f5a623,#d4880a); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:20px; box-shadow:0 0 24px rgba(245,166,35,.6); }
@keyframes ringPulse { 0%,100%{transform:scale(1);opacity:.6;} 50%{transform:scale(1.08);opacity:1;} }
.sanju-wordmark { flex:1; }
.sanju-name { font-size:2.2rem; font-weight:900; letter-spacing:-2px; line-height:1; color:var(--text-0); text-shadow:0 0 40px rgba(245,166,35,.3); }
.sanju-name em { font-style:normal; color:var(--amber); }
.online-pill { display:flex; align-items:center; gap:8px; background:rgba(45,212,191,.06); border:1px solid rgba(45,212,191,.2); border-radius:100px; padding:8px 18px; font-family:'Space Mono',monospace; font-size:.62rem; color:var(--teal); letter-spacing:2px; }
.online-dot { width:6px; height:6px; background:var(--teal); border-radius:50%; box-shadow:0 0 8px var(--teal); animation:blinkDot 2s ease-in-out infinite; }
@keyframes blinkDot { 0%,100%{opacity:1;} 50%{opacity:.2;} }

.stats-bar { display:flex; background:var(--bg-card); border:1px solid var(--border-mid); border-radius:var(--r-md); margin-bottom:16px; overflow:hidden; z-index:2; position:relative; }
.stat-item { flex:1; padding:10px 14px; border-right:1px solid var(--border-dim); display:flex; flex-direction:column; gap:2px; }
.stat-item:last-child { border-right:none; }
.stat-label { font-family:'Space Mono',monospace; font-size:.5rem; color:var(--text-2); letter-spacing:2px; text-transform:uppercase; }
.stat-value { font-size:.8rem; font-weight:700; color:var(--amber); }

.msg-wrap { display:flex; gap:12px; margin:14px 0; animation:fadeUp .4s cubic-bezier(.16,1,.3,1) both; position:relative; z-index:2; }
.msg-wrap.user-wrap { flex-direction:row-reverse; }
@keyframes fadeUp { from{opacity:0;transform:translateY(20px) scale(.98);} to{opacity:1;transform:none;} }
.av { width:36px; height:36px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:15px; flex-shrink:0; margin-top:4px; }
.av-user { background:linear-gradient(145deg,#7c5cbf,#a855f7); box-shadow:0 4px 16px rgba(124,92,191,.4); }
.av-ai   { background:linear-gradient(145deg,#d4880a,#f5a623); box-shadow:0 4px 16px rgba(245,166,35,.4); }
.bubble { max-width:72%; padding:13px 18px; border-radius:20px; font-size:.92rem; line-height:1.75; position:relative; font-family:'Outfit','Noto Sans Bengali',sans-serif; }
.bubble-user { background:linear-gradient(135deg,rgba(124,92,191,.15),rgba(168,85,247,.1)); border:1px solid rgba(124,92,191,.25); border-top-right-radius:4px; }
.bubble-ai { background:var(--bg-elevated); border:1px solid var(--border-mid); border-top-left-radius:4px; }
.bubble-ai::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,var(--amber),transparent); border-radius:20px 20px 0 0; opacity:.5; }
.bubble-meta { font-family:'Space Mono',monospace; font-size:.52rem; color:var(--text-2); letter-spacing:2px; text-transform:uppercase; margin-bottom:7px; display:flex; align-items:center; gap:8px; }
.bubble-meta-dot { width:4px; height:4px; background:var(--amber); border-radius:50%; }
.attach-badge { display:inline-block; background:rgba(245,166,35,.08); border:1px solid rgba(245,166,35,.2); border-radius:8px; padding:4px 10px; font-family:'Space Mono',monospace; font-size:.6rem; color:var(--amber); margin-bottom:8px; }
.lang-badge { display:inline-block; font-family:'Space Mono',monospace; font-size:.5rem; color:var(--teal); background:rgba(45,212,191,.08); border:1px solid rgba(45,212,191,.2); border-radius:6px; padding:2px 8px; letter-spacing:1px; margin-left:8px; }

/* TYPEWRITER CURSOR */
.typing-cursor { display:inline-block; width:2px; height:1em; background:var(--amber); margin-left:2px; animation:cursorBlink .7s ease-in-out infinite; vertical-align:text-bottom; }
@keyframes cursorBlink { 0%,100%{opacity:1;} 50%{opacity:0;} }

.thinking-wrap { display:flex; gap:12px; margin:16px 0; position:relative; z-index:2; animation:fadeUp .3s ease both; }
.thinking-bubble { background:var(--bg-card); border:1px solid rgba(245,166,35,.15); border-radius:20px; border-top-left-radius:4px; padding:16px 20px; max-width:70%; }
.thinking-header { font-family:'Space Mono',monospace; font-size:.52rem; color:var(--amber); letter-spacing:2px; text-transform:uppercase; margin-bottom:12px; }
.thinking-step { display:flex; align-items:flex-start; gap:10px; padding:6px 0; font-size:.75rem; color:var(--text-2); font-family:'Space Mono',monospace; border-bottom:1px solid var(--border-dim); }
.thinking-step:last-child { border-bottom:none; }
.step-icon { font-size:10px; margin-top:3px; flex-shrink:0; animation:spinIcon 2s linear infinite; }
@keyframes spinIcon { from{transform:rotate(0deg);}to{transform:rotate(360deg);} }
.step-icon.done { animation:none; }
.shimmer-line { height:2px; background:linear-gradient(90deg,transparent,var(--amber),var(--teal),transparent); background-size:200% 100%; border-radius:99px; margin-top:10px; animation:shimmer 1.8s linear infinite; }
@keyframes shimmer { from{background-position:200% 0;}to{background-position:-200% 0;} }

.welcome-wrap { text-align:center; padding:36px 0 22px; position:relative; z-index:2; }
.welcome-logo { font-size:3.2rem; margin-bottom:14px; display:block; animation:floatLogo 4s ease-in-out infinite; filter:drop-shadow(0 0 20px rgba(245,166,35,.6)); }
@keyframes floatLogo { 0%,100%{transform:translateY(0) rotate(-3deg);}50%{transform:translateY(-10px) rotate(3deg);} }
.welcome-title { font-size:1.8rem; font-weight:800; color:var(--text-0); letter-spacing:-1px; margin-bottom:6px; }
.welcome-sub { font-family:'Space Mono',monospace; font-size:.6rem; color:var(--text-2); letter-spacing:3px; text-transform:uppercase; margin-bottom:26px; }
.starters-label { font-family:'Space Mono',monospace; font-size:.56rem; color:var(--text-3); letter-spacing:3px; text-transform:uppercase; margin-bottom:10px; }
.history-label { font-family:'Space Mono',monospace; font-size:.5rem; color:var(--text-3); letter-spacing:2px; text-transform:uppercase; margin-bottom:6px; }

.stTextInput input { background:var(--bg-elevated)!important; border:1px solid var(--border-mid)!important; border-radius:var(--r-md)!important; color:var(--text-0)!important; font-family:'Outfit','Noto Sans Bengali',sans-serif!important; font-size:.95rem!important; transition:all .25s!important; caret-color:var(--amber)!important; padding:12px 18px!important; }
.stTextInput input:focus { border-color:rgba(245,166,35,.4)!important; box-shadow:0 0 0 3px rgba(245,166,35,.07),0 4px 20px rgba(0,0,0,.3)!important; }
.stTextInput input::placeholder { color:var(--text-3)!important; }

.stButton>button { background:linear-gradient(135deg,#f5a623,#d4880a)!important; color:#000!important; border:none!important; border-radius:var(--r-sm)!important; font-family:'Outfit',sans-serif!important; font-weight:800!important; font-size:.88rem!important; transition:all .2s!important; box-shadow:0 4px 16px rgba(245,166,35,.3)!important; }
.stButton>button:hover { transform:translateY(-2px)!important; box-shadow:0 8px 28px rgba(245,166,35,.45)!important; }

[data-testid="stSidebar"] { background:var(--bg-panel)!important; border-right:1px solid var(--border-mid)!important; }
[data-testid="stSidebar"] .stMarkdown h2,[data-testid="stSidebar"] .stMarkdown h3 { color:var(--text-0)!important; font-family:'Outfit',sans-serif!important; font-weight:700!important; }
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p { color:var(--text-1)!important; font-family:'Space Mono',monospace!important; font-size:.68rem!important; }

[data-testid="stFileUploader"] { background:rgba(245,166,35,.03)!important; border:1.5px dashed rgba(245,166,35,.2)!important; border-radius:var(--r-md)!important; }

code { background:rgba(245,166,35,.07)!important; border:1px solid rgba(245,166,35,.14)!important; border-radius:6px!important; padding:2px 7px!important; font-family:'Space Mono',monospace!important; color:var(--amber)!important; font-size:.8em!important; }
hr { border-color:var(--border-dim)!important; margin:0!important; }
::-webkit-scrollbar { width:4px; } ::-webkit-scrollbar-thumb { background:var(--border-mid); border-radius:99px; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0!important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────
DEFAULTS = {
    "messages": [], "response_times": [], "preset_input": "",
    "auto_send": False, "search_history": [],
    "pending_file": None, "pending_file_name": "", "pending_file_type": "",
    "tts_enabled": True, "voice_lang": "🇧🇩 Bengali (bn-BD)",
    "tts_pending": None, "tts_lang_pending": "en-US",
    "voice_injected": "", "last_voice_msg": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ──────────────────────────────────────────
def get_top_searches(n=6):
    if not st.session_state.search_history:
        return []
    return [item for item, _ in Counter(st.session_state.search_history).most_common(n)]

def detect_language(text):
    bn = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
    return "BN" if bn > 2 else "EN"

def build_system(base, use_bn):
    if use_bn:
        return base + "\n\nGURU INSTRUCTION: User is writing in Bengali. You MUST respond ENTIRELY in Bengali (বাংলা). Natural, clear Bengali throughout."
    return base

def is_image_request(text):
    keywords = [
        "generate image", "create image", "make image", "draw", "generate a picture",
        "create a picture", "image of", "picture of", "generate photo", "make a photo",
        "ছবি বানাও", "ছবি তৈরি", "ছবি দাও", "একটি ছবি", "আঁকো",
    ]
    t = text.lower()
    return any(k in t for k in keywords)

def generate_image_pollinations(prompt):
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=768&nologo=true&enhance=true"
    return url

def export_markdown():
    lines = ["# SANJU Chat Export\n"]
    for item in st.session_state.messages:
        role, content = item[0], item[1]
        label = "**YOU**" if role == "user" else "**✦ SANJU**"
        lines.append(f"{label}\n\n{content}\n\n---\n")
    return "\n".join(lines)

def get_voice_lang_code():
    vl = st.session_state.get("voice_lang", "🇧🇩 Bengali (bn-BD)")
    if "Bengali" in vl:
        return "bn-BD"
    elif "English" in vl:
        return "en-US"
    else:
        return "bn-BD"

# ── SIDEBAR ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✦ SANJU Settings")
    st.markdown("---")

    model_name  = st.selectbox("⚡ MODEL", ["mistral-small-2506", "mistral-medium-2505", "mistral-large-latest"])
    temperature = st.slider("🌡️ TEMPERATURE", 0.0, 1.0, 0.7, 0.05)
    max_tokens  = st.slider("📏 MAX TOKENS", 256, 4096, 1024, 64)

    st.markdown("---")
    st.markdown("### 🌐 LANGUAGE")
    lang_mode = st.selectbox("Reply Language", ["🤖 Auto Detect", "🇧🇩 Always Bengali", "🇬🇧 Always English"])

    st.markdown("---")
    st.markdown("### 🔊 VOICE SETTINGS")
    st.session_state["tts_enabled"] = st.toggle("🔊 Speak AI Replies (TTS)", value=st.session_state["tts_enabled"])
    st.session_state["voice_lang"]  = st.selectbox(
        "🎤 Voice Input Language",
        ["🇧🇩 Bengali (bn-BD)", "🇬🇧 English (en-US)", "🌐 Auto (bn-BD)"],
        index=["🇧🇩 Bengali (bn-BD)", "🇬🇧 English (en-US)", "🌐 Auto (bn-BD)"].index(st.session_state["voice_lang"])
              if st.session_state["voice_lang"] in ["🇧🇩 Bengali (bn-BD)", "🇬🇧 English (en-US)", "🌐 Auto (bn-BD)"] else 0
    )

    st.markdown("---")
    st.markdown("### 🎭 PERSONA")
    persona = st.selectbox("Choose Persona", ["🧠 Smart Assistant","💻 Code Expert","✍️ Creative Writer","🔬 Research Analyst","😄 Funny Friend","🔧 Custom"])
    persona_map = {
        "🧠 Smart Assistant": "You are SANJU, a highly intelligent AI assistant. Be concise and insightful.",
        "💻 Code Expert":     "You are SANJU, an elite software engineer. Provide clean code with clear explanations.",
        "✍️ Creative Writer": "You are SANJU, a brilliant creative writer. Be vivid, imaginative, emotionally resonant.",
        "🔬 Research Analyst":"You are SANJU, a meticulous research analyst. Be thorough and structure info clearly.",
        "😄 Funny Friend":    "You are SANJU, witty and funny. Add humor and keep things light.",
        "🔧 Custom":          "",
    }
    if persona == "🔧 Custom":
        system_prompt = st.text_area("✏️ SYSTEM PROMPT", value="You are SANJU, an advanced AI assistant.", height=100)
    else:
        system_prompt = persona_map[persona]
        st.markdown(f"<div style='background:rgba(245,166,35,.05);border:1px solid rgba(245,166,35,.15);border-radius:10px;padding:10px 12px;font-size:.65rem;font-family:\"Space Mono\",monospace;color:#555;line-height:1.7;'>{system_prompt}</div>", unsafe_allow_html=True)

    st.markdown("---")
    msg_count  = len(st.session_state.messages)
    user_count = sum(1 for r, *_ in st.session_state.messages if r == "user")
    avg_rt     = sum(st.session_state.response_times) / len(st.session_state.response_times) if st.session_state.response_times else 0
    st.markdown(f"<div style='font-family:\"Space Mono\",monospace;font-size:.65rem;color:#3a3a60;'><div style='margin-bottom:8px;display:flex;justify-content:space-between;'><span>💬 MESSAGES</span><span style='color:#f5a623;font-weight:700;'>{msg_count}</span></div><div style='margin-bottom:8px;display:flex;justify-content:space-between;'><span>👤 TURNS</span><span style='color:#f5a623;font-weight:700;'>{user_count}</span></div><div style='display:flex;justify-content:space-between;'><span>⚡ AVG</span><span style='color:#2dd4bf;font-weight:700;'>{avg_rt:.1f}s</span></div></div>", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Clear"):
            for k in ["messages","response_times","search_history","pending_file","pending_file_name","pending_file_type"]:
                st.session_state[k] = [] if k in ["messages","response_times","search_history"] else (None if k == "pending_file" else "")
            st.rerun()
    with c2:
        if st.session_state.messages:
            st.download_button("📄 Export", data=export_markdown().encode("utf-8"), file_name="sanju_chat.md", mime="text/markdown")

# ── MAIN ─────────────────────────────────────────────
main_col, _ = st.columns([1, 0.001])
with main_col:

    # HEADER
    st.markdown("""<div class='sanju-header'>
        <div class='sanju-emblem'><div class='sanju-emblem-ring'></div><div class='sanju-emblem-inner'>✦</div></div>
        <div class='sanju-wordmark'>
            <div class='sanju-name'>SAN<em>JU</em></div>
            <div style='font-size:1rem;font-weight:600;letter-spacing:-.5px;margin-top:2px;color:#a0a0c0;'><em style='color:#f5a623;font-style:normal;'>Empowering</em> Ideas Through <em style='color:#f5a623;font-style:normal;'>Intelligence</em></div>
        </div>
        <div class='online-pill'><div class='online-dot'></div>ONLINE</div>
    </div>""", unsafe_allow_html=True)

    # ── TTS PLAYER (runs after rerun, visible height so browser allows audio) ──
    if st.session_state.get("tts_pending") and st.session_state.get("tts_enabled", True):
        _tts_text = st.session_state["tts_pending"]
        _tts_lang = st.session_state.get("tts_lang_pending", "en-US")
        # Escape for JS
        _tts_text = _tts_text.replace("\\", "\\\\").replace("`", "'").replace('\n', ' ').replace('"', "'")
        _tts_text = _tts_text[:600]  # limit length
        _tts_html = f"""
        <div id="ttsBox" style="background:rgba(45,212,191,0.06);border:1px solid rgba(45,212,191,0.2);border-radius:10px;padding:8px 16px;font-family:'Space Mono',monospace;font-size:.6rem;color:#2dd4bf;letter-spacing:2px;display:flex;align-items:center;gap:10px;">
            <span style="animation:blinkDot 1s infinite;display:inline-block;width:6px;height:6px;background:#2dd4bf;border-radius:50%;"></span>
            <span id="ttsLabel">🔊 SPEAKING...</span>
            <button onclick="window.speechSynthesis.cancel();document.getElementById('ttsBox').style.opacity='0.3';document.getElementById('ttsLabel').textContent='⏹ STOPPED';" style="background:rgba(239,68,68,.2);border:1px solid rgba(239,68,68,.3);border-radius:6px;color:#ef4444;font-size:.55rem;padding:2px 8px;cursor:pointer;font-family:'Space Mono',monospace;">STOP</button>
        </div>
        <script>
        (function() {{
            function speakNow() {{
                window.speechSynthesis.cancel();
                const u = new SpeechSynthesisUtterance(`{_tts_text}`);
                u.lang = '{_tts_lang}';
                u.rate = 1.0;
                u.pitch = 1.0;
                u.volume = 1.0;
                u.onend = function() {{
                    const box = document.getElementById('ttsBox');
                    if (box) {{ box.style.opacity = '0.4'; document.getElementById('ttsLabel').textContent = '✔ DONE'; }}
                }};
                u.onerror = function(e) {{
                    const box = document.getElementById('ttsBox');
                    if (box) document.getElementById('ttsLabel').textContent = '❌ TTS ERROR: ' + e.error;
                }};
                window.speechSynthesis.speak(u);
            }}
            if (document.readyState === 'complete') {{
                setTimeout(speakNow, 300);
            }} else {{
                window.addEventListener('load', () => setTimeout(speakNow, 300));
            }}
        }})();
        </script>
        """
        components.html(_tts_html, height=50)
        st.session_state["tts_pending"] = None

    # STATS
    if st.session_state.messages:
        sm = model_name.replace("mistral-","").replace("-latest","").upper()
        st.markdown(f"""<div class='stats-bar'>
            <div class='stat-item'><div class='stat-label'>MODEL</div><div class='stat-value'>{sm}</div></div>
            <div class='stat-item'><div class='stat-label'>TEMP</div><div class='stat-value'>{temperature}</div></div>
            <div class='stat-item'><div class='stat-label'>MSGS</div><div class='stat-value'>{msg_count}</div></div>
            <div class='stat-item'><div class='stat-label'>LANG</div><div class='stat-value'>{lang_mode.split()[0]}</div></div>
            <div class='stat-item'><div class='stat-label'>AVG</div><div class='stat-value'>{avg_rt:.1f}s</div></div>
        </div>""", unsafe_allow_html=True)

    # WELCOME
    if not st.session_state.messages:
        st.markdown("""<div class='welcome-wrap'>
            <span class='welcome-logo'>✦</span>
            <div class='welcome-title'>Hello, I'm SANJU</div>
            <div class='welcome-sub'>Your Advanced AI Companion · Ready to Assist</div>
            <div class='starters-label'>QUICK STARTERS — Click to send instantly</div>
        </div>""", unsafe_allow_html=True)

        presets = [
            "✍️ Write a poem about space",
            "💻 Explain async/await in Python",
            "🔬 Summarize quantum computing",
            "🎨 Give me 5 startup ideas",
            "😄 Tell me a clever joke",
            "🌍 Best travel tips for Japan",
        ]
        cols = st.columns(3)
        for i, p in enumerate(presets):
            with cols[i % 3]:
                if st.button(p, key=f"preset_{i}"):
                    st.session_state.preset_input = p
                    st.session_state.auto_send = True

    # CHAT HISTORY
    for idx, item in enumerate(st.session_state.messages):
        role, content = item[0], item[1]
        attach_meta = item[2] if len(item) > 2 else None
        lang_used   = item[3] if len(item) > 3 else "EN"
        img_bytes   = item[4] if len(item) > 4 else None

        if role == "user":
            ab = f"<div class='attach-badge'>📎 {attach_meta['name']}</div>" if attach_meta else ""
            st.markdown(f"""<div class='msg-wrap user-wrap'>
                <div class='av av-user'>👤</div>
                <div class='bubble bubble-user'>
                    <div class='bubble-meta'>YOU</div>
                    {ab}{content}
                </div>
            </div>""", unsafe_allow_html=True)
        elif lang_used == "IMG" and img_bytes:
            st.markdown(f"""<div class='msg-wrap'>
                <div class='av av-ai'>✦</div>
                <div style='flex:1;max-width:72%;'>
                <div style='font-family:"Space Mono",monospace;font-size:.52rem;color:#5a5a80;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>
                    <span style='width:4px;height:4px;background:#f5a623;border-radius:50%;display:inline-block;margin-right:8px;'></span>
                    SANJU · IMAGE GENERATION
                </div>
                <div style='font-family:"Space Mono",monospace;font-size:.6rem;color:#f5a623;margin-bottom:8px;'>
                    🎨 {content[:80]}
                </div>""", unsafe_allow_html=True)
            st.image(img_bytes, width=480)
            st.download_button(
                label="⬇️ Download Image",
                data=img_bytes,
                file_name=f"sanju_generated_{idx}.jpg",
                mime="image/jpeg",
                key=f"dl_{idx}"
            )
            st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            badge = "<span class='lang-badge'>বাংলা</span>" if lang_used == "BN" else ""
            st.markdown(f"""<div class='msg-wrap'>
                <div class='av av-ai'>✦</div>
                <div class='bubble bubble-ai'>
                    <div class='bubble-meta'><span class='bubble-meta-dot'></span>SANJU · {model_name}{badge}</div>
                    {content}
                </div>
            </div>""", unsafe_allow_html=True)

    # SEARCH HISTORY
    top = get_top_searches(6)
    if top:
        st.markdown("<div class='history-label' style='margin-top:10px;'>🕐 FREQUENT SEARCHES — Click to send</div>", unsafe_allow_html=True)
        hcols = st.columns(min(len(top), 3))
        for i, q in enumerate(top):
            with hcols[i % 3]:
                lbl = q[:25] + "..." if len(q) > 28 else q
                if st.button(f"↺ {lbl}", key=f"h_{i}_{hash(q)%9999}"):
                    st.session_state.preset_input = q
                    st.session_state.auto_send = True

    # FILE UPLOAD
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    with st.expander("📎 Attach Image or PDF (like ChatGPT)"):
        uploaded = st.file_uploader(
            "Image (PNG/JPG) or PDF", type=["png","jpg","jpeg","pdf"],
            key="fu", label_visibility="collapsed"
        )
        if uploaded:
            fb = uploaded.read()
            ft = uploaded.type
            fn = uploaded.name
            b64 = base64.b64encode(fb).decode("utf-8")
            if "image" in ft:
                st.session_state.pending_file = {"b64": b64, "mime": ft, "bytes": fb, "text": None}
                st.session_state.pending_file_type = "image"
                st.image(fb, caption=f"✅ {fn}", width=200)
                st.session_state.pending_file_name = fn
            elif "pdf" in ft:
                extracted_text = ""
                try:
                    import fitz
                    doc = fitz.open(stream=fb, filetype="pdf")
                    parts = []
                    for i, page in enumerate(doc):
                        parts.append("--- Page " + str(i+1) + " ---\n" + page.get_text())
                    extracted_text = "\n\n".join(parts)
                    doc.close()
                except Exception:
                    pass
                if not extracted_text.strip():
                    try:
                        import pypdf
                        reader = pypdf.PdfReader(io.BytesIO(fb))
                        parts = []
                        for i, page in enumerate(reader.pages):
                            parts.append("--- Page " + str(i+1) + " ---\n" + (page.extract_text() or ""))
                        extracted_text = "\n\n".join(parts)
                    except Exception:
                        pass
                st.session_state.pending_file = {"b64": b64, "mime": ft, "bytes": fb, "text": extracted_text}
                st.session_state.pending_file_type = "pdf"
                st.session_state.pending_file_name = fn
                if extracted_text.strip():
                    wc = len(extracted_text.split())
                    st.success(f"✅ PDF Ready: {fn} ({wc} words extracted)")
                else:
                    st.error("❌ Could not extract text. Run: pip install pymupdf")

    if st.session_state.pending_file:
        st.markdown(f"<div class='attach-badge'>📎 Ready: {st.session_state.pending_file_name}</div>", unsafe_allow_html=True)

    # ── VOICE INPUT via st.audio_input (native Streamlit — no iframe issue) ──
    voice_lang_code = get_voice_lang_code()

    st.markdown("""<div style='font-family:"Space Mono",monospace;font-size:.56rem;color:#5a5a80;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;'>
        🎤 VOICE INPUT — রেকর্ড করুন → Auto Transcribe → Send
    </div>""", unsafe_allow_html=True)

    audio_col, info_col = st.columns([2, 3])
    with audio_col:
        audio_data = st.audio_input("🎤 Tap to Record", label_visibility="collapsed", key="voice_recorder")

    with info_col:
        if audio_data:
            st.markdown("""<div style='background:rgba(45,212,191,.08);border:1px solid rgba(45,212,191,.25);border-radius:12px;padding:10px 14px;font-family:"Space Mono",monospace;font-size:.6rem;color:#2dd4bf;letter-spacing:1px;'>
                ✔ Audio recorded! Transcribing...
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style='background:rgba(124,92,191,.06);border:1px solid rgba(124,92,191,.2);border-radius:12px;padding:10px 14px;font-family:"Space Mono",monospace;font-size:.6rem;color:#7c5cbf;letter-spacing:1px;'>
                🎤 Mic button click koro → বলুন → থামুন → Auto send
            </div>""", unsafe_allow_html=True)

    # Transcribe audio if newly recorded
    if audio_data and id(audio_data) != st.session_state.get("last_audio_id"):
        st.session_state["last_audio_id"] = id(audio_data)
        transcribed = ""
        err_msg = ""
        try:
            import io as _io
            import wave
            import struct
            import tempfile, os

            audio_data.seek(0)
            raw_bytes = audio_data.read()

            # Write to temp file and detect format
            suffix = ".webm"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(raw_bytes)
                tmp_path = tmp.name

            wav_path = tmp_path.replace(".webm", ".wav")
            converted = False

            # Try ffmpeg (if installed)
            ret = os.system(f'ffmpeg -y -i "{tmp_path}" -ar 16000 -ac 1 "{wav_path}" -loglevel quiet 2>nul')
            if ret == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
                converted = True

            # Try soundfile if ffmpeg failed
            if not converted:
                try:
                    import soundfile as sf
                    import numpy as np
                    data, samplerate = sf.read(_io.BytesIO(raw_bytes))
                    if data.ndim > 1:
                        data = data[:, 0]
                    data_int16 = (data * 32767).astype(np.int16)
                    with wave.open(wav_path, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(samplerate)
                        wf.writeframes(data_int16.tobytes())
                    converted = True
                except Exception:
                    pass

            # Try pydub if others failed
            if not converted:
                try:
                    from pydub import AudioSegment
                    seg = AudioSegment.from_file(_io.BytesIO(raw_bytes))
                    seg = seg.set_frame_rate(16000).set_channels(1)
                    seg.export(wav_path, format="wav")
                    converted = True
                except Exception:
                    pass

            if converted and os.path.exists(wav_path):
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                with sr.AudioFile(wav_path) as source:
                    audio_recorded = recognizer.record(source)
                try:
                    transcribed = recognizer.recognize_google(audio_recorded, language=voice_lang_code)
                except sr.UnknownValueError:
                    try:
                        transcribed = recognizer.recognize_google(audio_recorded, language="en-US")
                    except sr.UnknownValueError:
                        err_msg = "⚠️ কিছু শোনা যায়নি — একটু জোরে বলুন বা কাছে ধরুন।"
                except sr.RequestError as e:
                    err_msg = f"⚠️ Internet error: {e}"
                finally:
                    try: os.unlink(wav_path)
                    except: pass
            else:
                err_msg = "⚠️ Audio convert হয়নি। Terminal-e run koro:\n`pip install pydub soundfile` এবং ffmpeg install koro।"

            try: os.unlink(tmp_path)
            except: pass

        except ImportError:
            err_msg = "⚠️ Run: `pip install SpeechRecognition soundfile`"
        except Exception as e:
            err_msg = f"⚠️ Error: {str(e)[:120]}"

        if transcribed:
            st.success(f"✔ শুনলাম: **{transcribed}**")
            st.session_state.preset_input = transcribed
            st.session_state.auto_send = True
            st.rerun()
        elif err_msg:
            st.warning(err_msg)


    # INPUT ROW
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([6, 1])

    dv = st.session_state.preset_input
    if not (dv and st.session_state.auto_send):
        st.session_state.preset_input = ""

    with c1:
        user_input = st.text_input("Message", value=dv,
            placeholder="Message SANJU... (Bengali or English)",
            label_visibility="collapsed", key="chat_input")
    with c2:
        send = st.button("↑ Send", use_container_width=True)

    should_send = send or (st.session_state.auto_send and user_input.strip())
    if st.session_state.auto_send:
        st.session_state.auto_send = False
        st.session_state.preset_input = ""

    # ── GENERATE ──────────────────────────────────────
    if should_send and user_input.strip():
        st.session_state.search_history.append(user_input.strip())

        # ── IMAGE GENERATION ──
        if is_image_request(user_input) and not st.session_state.pending_file:
            img_placeholder = st.empty()
            img_placeholder.markdown("""<div class='thinking-wrap'>
                <div class='av av-ai'>✦</div>
                <div class='thinking-bubble'>
                    <div class='thinking-header'>🎨 &nbsp;GENERATING IMAGE...</div>
                    <div class='thinking-step'><span class='step-icon' style='color:#f5a623'>⟳</span><span style='color:#a0a0c0'>Creating your image via Pollinations AI...</span></div>
                    <div class='shimmer-line'></div>
                </div>
            </div>""", unsafe_allow_html=True)

            img_prompt_sys = "Extract only the image description from the user message. Return ONLY the description, no extra words."
            try:
                prompt_llm = ChatMistralAI(model=model_name, temperature=0.3, max_tokens=100, mistral_api_key=api_key)
                prompt_resp = prompt_llm.invoke([
                    SystemMessage(content=img_prompt_sys),
                    HumanMessage(content=user_input)
                ])
                clean_prompt = prompt_resp.content.strip()
            except Exception:
                clean_prompt = user_input

            img_url = generate_image_pollinations(clean_prompt)

            def fetch_image(url, retries=3):
                for attempt in range(retries):
                    try:
                        resp = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
                        if resp.status_code != 200:
                            time.sleep(2)
                            continue
                        raw = resp.content
                        PILImage.open(io.BytesIO(raw)).verify()
                        return raw
                    except Exception:
                        time.sleep(3)
                return None

            img_bytes = fetch_image(img_url)
            img_placeholder.empty()

            st.session_state.messages.append(("user", user_input, None))
            if img_bytes:
                st.session_state.messages.append(("assistant", clean_prompt, None, "IMG", img_bytes))
            else:
                st.session_state.messages.append(("assistant",
                    "❌ Image could not be generated. Pollinations may be slow — please try again.",
                    None, "EN"))

            st.session_state.response_times.append(0.0)
            st.rerun()
            st.stop()

        # ── LANGUAGE DETECTION ──
        detected = detect_language(user_input)
        use_bn = (lang_mode == "🇧🇩 Always Bengali") or (lang_mode == "🤖 Auto Detect" and detected == "BN")
        final_sys = build_system(system_prompt, use_bn)

        # ── BUILD CONVERSATION HISTORY ──
        lc_msgs = [SystemMessage(content=final_sys)]
        for item in st.session_state.messages:
            r, c = item[0], item[1]
            lang_flag = item[3] if len(item) > 3 else "EN"
            if lang_flag == "IMG":
                continue
            lc_msgs.append(HumanMessage(content=c) if r == "user" else AIMessage(content=c))

        # ── BUILD CURRENT USER MESSAGE ──
        attach_meta = None
        if st.session_state.pending_file:
            pf   = st.session_state.pending_file
            fn   = st.session_state.pending_file_name
            ft   = st.session_state.pending_file_type
            attach_meta = {"name": fn, "type": ft}

            if ft == "image":
                lc_msgs.append(HumanMessage(content=[
                    {"type": "text", "text": user_input},
                    {"type": "image_url", "image_url": f"data:{pf['mime']};base64,{pf['b64']}"}
                ]))
            elif ft == "pdf":
                extracted = pf.get("text", "") or ""
                if extracted.strip():
                    snippet   = extracted[:12000]
                    truncated = "\n[...document truncated due to length]" if len(extracted) > 12000 else ""
                    prompt    = (
                        f"PDF Document: '{fn}'\n\n"
                        f"{snippet}{truncated}\n\n"
                        f"---\nUser: {user_input}"
                    )
                    lc_msgs.append(HumanMessage(content=prompt))
                else:
                    lc_msgs.append(HumanMessage(content=(
                        f"The user attached a PDF named '{fn}' but text could not be extracted. "
                        f"User's message: {user_input}"
                    )))

            st.session_state.pending_file      = None
            st.session_state.pending_file_name = ""
            st.session_state.pending_file_type = ""
        else:
            lc_msgs.append(HumanMessage(content=user_input))

        # ── THINKING ANIMATION ──
        tp = st.empty()
        STEPS = [
            ("⟳", "আপনার বার্তা পড়ছি..." if use_bn else "Reading your message..."),
            ("⟳", "প্রসঙ্গ বিশ্লেষণ..." if use_bn else "Analysing context..."),
            ("⟳", "জ্ঞান অনুসন্ধান..." if use_bn else "Searching knowledge base..."),
            ("⟳", "উত্তর তৈরি..." if use_bn else "Structuring response..."),
            ("⟳", "পরিশোধন..." if use_bn else "Refining output..."),
        ]

        def show_thinking(done):
            html = ""
            for i, (icon, lbl) in enumerate(STEPS):
                if i < done:
                    html += f"<div class='thinking-step'><span class='step-icon done' style='color:#2dd4bf'>✔</span><span style='color:#5a5a80;text-decoration:line-through'>{lbl}</span></div>"
                elif i == done:
                    html += f"<div class='thinking-step'><span class='step-icon' style='color:#f5a623'>{icon}</span><span style='color:#a0a0c0'>{lbl}</span></div>"
                else:
                    html += f"<div class='thinking-step' style='opacity:.3'><span class='step-icon done'>○</span><span>{lbl}</span></div>"
            tp.markdown(f"""<div class='thinking-wrap'>
                <div class='av av-ai'>✦</div>
                <div class='thinking-bubble'>
                    <div class='thinking-header'>◈ &nbsp;{'চিন্তা করছি...' if use_bn else 'THINKING PROCESS'}</div>
                    {html}<div class='shimmer-line'></div>
                </div>
            </div>""", unsafe_allow_html=True)

        # ── ADD USER MSG TO HISTORY NOW ──
        st.session_state.messages.append(("user", user_input, attach_meta))

        try:
            import threading
            t0  = time.time()
            llm = ChatMistralAI(model=model_name, temperature=temperature,
                                max_tokens=max_tokens, mistral_api_key=api_key)
            res, err = {}, {}

            def run():
                try: res["r"] = llm.invoke(lc_msgs)
                except Exception as e: err["e"] = e

            t = threading.Thread(target=run); t.start()
            for si in range(len(STEPS)):
                show_thinking(si)
                t.join(timeout=0.55)
                if not t.is_alive():
                    for ri in range(si+1, len(STEPS)):
                        show_thinking(ri); time.sleep(0.08)
                    break
            t.join()

            if "e" in err: raise err["e"]

            elapsed = round(time.time()-t0, 2)
            reply   = res["r"].content
            tp.empty()

            rl = "BN" if use_bn else "EN"
            st.session_state.messages.append(("assistant", reply, None, rl))
            st.session_state.response_times.append(elapsed)

            # ── STREAMING / TYPEWRITER EFFECT ──────────
            # Show the latest AI response with typewriter animation
            stream_placeholder = st.empty()
            badge = "<span class='lang-badge'>বাংলা</span>" if rl == "BN" else ""

            # Typewriter: reveal word by word
            words = reply.split(" ")
            displayed = ""
            CHUNK = 3  # reveal 3 words at a time for speed
            for wi in range(0, len(words), CHUNK):
                chunk = " ".join(words[wi:wi+CHUNK])
                displayed += ("" if wi == 0 else " ") + chunk
                stream_placeholder.markdown(f"""<div class='msg-wrap'>
                    <div class='av av-ai'>✦</div>
                    <div class='bubble bubble-ai'>
                        <div class='bubble-meta'><span class='bubble-meta-dot'></span>SANJU · {model_name}{badge}</div>
                        {displayed}<span class='typing-cursor'></span>
                    </div>
                </div>""", unsafe_allow_html=True)
                time.sleep(0.025)

            # Final render without cursor
            stream_placeholder.markdown(f"""<div class='msg-wrap'>
                <div class='av av-ai'>✦</div>
                <div class='bubble bubble-ai'>
                    <div class='bubble-meta'><span class='bubble-meta-dot'></span>SANJU · {model_name}{badge}</div>
                    {reply}
                </div>
            </div>""", unsafe_allow_html=True)

            # ── STORE TTS → play after rerun ────────────
            if st.session_state.get("tts_enabled", True):
                tts_lang = "bn-BD" if rl == "BN" else "en-US"
                clean_reply = re.sub(r'[#*`_~<>\[\]()]', '', reply)[:600]
                st.session_state["tts_pending"] = clean_reply
                st.session_state["tts_lang_pending"] = tts_lang

            st.rerun()

        except Exception as e:
            tp.empty()
            st.session_state.messages.pop()  # remove user msg on error
            st.error(f"❌ API Error: {e}")
