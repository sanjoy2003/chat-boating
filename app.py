from dotenv import load_dotenv
import os
import time
import streamlit as st
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

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

# ── PREMIUM CSS ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

:root {
    --bg-void:     #02020a;
    --bg-deep:     #070712;
    --bg-panel:    #0b0b1a;
    --bg-card:     #0f0f1f;
    --bg-elevated: #141428;
    --border-dim:  rgba(255,255,255,0.04);
    --border-mid:  rgba(255,255,255,0.08);
    --border-hi:   rgba(255,255,255,0.14);

    /* Signature palette — deep violet × electric amber × ghost white */
    --amber:       #f5a623;
    --amber-glow:  rgba(245,166,35,0.18);
    --amber-soft:  rgba(245,166,35,0.08);
    --violet:      #7c5cbf;
    --violet-glow: rgba(124,92,191,0.25);
    --teal:        #2dd4bf;
    --teal-glow:   rgba(45,212,191,0.15);
    --rose:        #f472b6;

    --text-0:  #f0f0fa;
    --text-1:  #a0a0c0;
    --text-2:  #5a5a80;
    --text-3:  #2e2e50;

    --radius-sm: 10px;
    --radius-md: 16px;
    --radius-lg: 24px;
}

/* ── BASE ── */
html, body, .stApp {
    background: var(--bg-void) !important;
    font-family: 'Outfit', sans-serif !important;
    color: var(--text-0) !important;
}

/* ── DEEP SPACE BG ── */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 10% 0%, rgba(124,92,191,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 100%, rgba(245,166,35,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(45,212,191,0.04) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* Subtle noise texture */
.stApp::after {
    content: '';
    position: fixed; inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
}

/* ── HEADER ── */
.sanju-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 30px 4px 22px 4px;
    border-bottom: 1px solid var(--border-mid);
    margin-bottom: 28px;
    position: relative;
    z-index: 2;
}

.sanju-emblem {
    position: relative;
    width: 52px; height: 52px;
    flex-shrink: 0;
}

.sanju-emblem-ring {
    position: absolute; inset: 0;
    border-radius: 14px;
    border: 1.5px solid rgba(245,166,35,0.5);
    animation: ringPulse 3s ease-in-out infinite;
}

.sanju-emblem-inner {
    position: absolute; inset: 5px;
    background: linear-gradient(135deg, #f5a623, #d4880a);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 0 24px rgba(245,166,35,0.6), inset 0 1px 0 rgba(255,255,255,0.2);
}

@keyframes ringPulse {
    0%,100% { transform: scale(1); opacity: 0.6; }
    50%      { transform: scale(1.08); opacity: 1; }
}

.sanju-wordmark {
    flex: 1;
}

.sanju-name {
    font-size: 2.4rem;
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1;
    color: var(--text-0);
    text-shadow: 0 0 40px rgba(245,166,35,0.3);
}

.sanju-name em {
    font-style: normal;
    color: var(--amber);
}

.sanju-tagline {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: var(--text-2);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 4px;
}

.online-pill {
    display: flex; align-items: center; gap: 8px;
    background: rgba(45,212,191,0.06);
    border: 1px solid rgba(45,212,191,0.2);
    border-radius: 100px;
    padding: 8px 18px;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    color: var(--teal);
    letter-spacing: 2px;
}

.online-dot {
    width: 6px; height: 6px;
    background: var(--teal);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--teal);
    animation: blinkDot 2s ease-in-out infinite;
}

@keyframes blinkDot { 0%,100%{opacity:1;} 50%{opacity:0.2;} }

/* ── STATS BAR ── */
.stats-bar {
    display: flex; gap: 0;
    background: var(--bg-card);
    border: 1px solid var(--border-mid);
    border-radius: var(--radius-md);
    margin-bottom: 20px;
    overflow: hidden;
    position: relative; z-index: 2;
}

.stat-item {
    flex: 1;
    padding: 10px 16px;
    border-right: 1px solid var(--border-dim);
    display: flex; flex-direction: column; gap: 2px;
}

.stat-item:last-child { border-right: none; }

.stat-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.52rem;
    color: var(--text-2);
    letter-spacing: 2px;
    text-transform: uppercase;
}

.stat-value {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--amber);
}

/* ── MESSAGES ── */
.msg-wrap {
    display: flex;
    gap: 12px;
    margin: 16px 0;
    animation: fadeUp 0.4s cubic-bezier(0.16,1,0.3,1) both;
    position: relative; z-index: 2;
}

.msg-wrap.user-wrap { flex-direction: row-reverse; }

@keyframes fadeUp {
    from { opacity:0; transform: translateY(20px) scale(0.98); }
    to   { opacity:1; transform: translateY(0) scale(1); }
}

.av {
    width: 38px; height: 38px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
    margin-top: 4px;
}

.av-user {
    background: linear-gradient(145deg, #7c5cbf, #a855f7);
    box-shadow: 0 4px 16px rgba(124,92,191,0.4);
}

.av-ai {
    background: linear-gradient(145deg, #d4880a, #f5a623);
    box-shadow: 0 4px 16px rgba(245,166,35,0.4);
}

.bubble {
    max-width: 70%;
    padding: 14px 20px;
    border-radius: 20px;
    font-size: 0.93rem;
    line-height: 1.7;
    position: relative;
}

.bubble-user {
    background: linear-gradient(135deg, rgba(124,92,191,0.15), rgba(168,85,247,0.1));
    border: 1px solid rgba(124,92,191,0.25);
    border-top-right-radius: 4px;
}

.bubble-ai {
    background: var(--bg-elevated);
    border: 1px solid var(--border-mid);
    border-top-left-radius: 4px;
}

.bubble-ai::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, var(--amber), transparent);
    border-radius: 20px 20px 0 0;
    opacity: 0.5;
}

.bubble-meta {
    font-family: 'Space Mono', monospace;
    font-size: 0.55rem;
    color: var(--text-2);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
    display: flex; align-items: center; gap: 8px;
}

.bubble-meta-dot {
    width: 4px; height: 4px;
    background: var(--amber);
    border-radius: 50%;
}

/* ── THINKING PROCESS ── */
.thinking-wrap {
    display: flex;
    gap: 12px;
    margin: 16px 0;
    position: relative; z-index: 2;
    animation: fadeUp 0.3s ease both;
}

.thinking-bubble {
    background: var(--bg-card);
    border: 1px solid rgba(245,166,35,0.15);
    border-radius: 20px;
    border-top-left-radius: 4px;
    padding: 16px 20px;
    max-width: 70%;
    position: relative;
    overflow: hidden;
}

.thinking-bubble::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(245,166,35,0.04), transparent);
    pointer-events: none;
}

.thinking-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.55rem;
    color: var(--amber);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
}

.thinking-step {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    font-size: 0.78rem;
    color: var(--text-2);
    font-family: 'Space Mono', monospace;
    border-bottom: 1px solid var(--border-dim);
    animation: stepReveal 0.4s ease both;
}

.thinking-step:last-child { border-bottom: none; }

@keyframes stepReveal {
    from { opacity:0; transform: translateX(-8px); }
    to   { opacity:1; transform: translateX(0); }
}

.step-icon {
    font-size: 10px;
    margin-top: 3px;
    flex-shrink: 0;
    animation: spinIcon 2s linear infinite;
}

@keyframes spinIcon {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

.step-icon.done { animation: none; }

/* ── TYPING DOTS ── */
.typing-dots {
    display: flex; gap: 5px; align-items: center;
    padding: 4px 0;
}

.typing-dots span {
    width: 7px; height: 7px;
    background: var(--amber);
    border-radius: 50%;
    animation: bounce 1.2s ease-in-out infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; background: var(--teal); }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; background: var(--violet); }

@keyframes bounce {
    0%,80%,100% { transform: scale(0.5); opacity: 0.3; }
    40%          { transform: scale(1.1); opacity: 1; }
}

/* ── SHIMMER LINE (thinking progress) ── */
.shimmer-line {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--amber), var(--teal), transparent);
    background-size: 200% 100%;
    border-radius: 99px;
    margin-top: 10px;
    animation: shimmer 1.8s linear infinite;
}

@keyframes shimmer {
    from { background-position: 200% 0; }
    to   { background-position: -200% 0; }
}

/* ── WELCOME ── */
.welcome-wrap {
    text-align: center;
    padding: 50px 0 30px 0;
    position: relative; z-index: 2;
}

.welcome-logo {
    font-size: 3.5rem;
    margin-bottom: 16px;
    display: block;
    animation: floatLogo 4s ease-in-out infinite;
    filter: drop-shadow(0 0 20px rgba(245,166,35,0.6));
}

@keyframes floatLogo {
    0%,100% { transform: translateY(0) rotate(-3deg); }
    50%      { transform: translateY(-12px) rotate(3deg); }
}

.welcome-title {
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text-0);
    letter-spacing: -1px;
    margin-bottom: 8px;
}

.welcome-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    color: var(--text-2);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 30px;
}

.starters-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem;
    color: var(--text-3);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

/* ── INPUT ── */
.stTextInput input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-0) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.95rem !important;
    transition: all 0.25s !important;
    caret-color: var(--amber) !important;
    padding: 12px 18px !important;
}

.stTextInput input:focus {
    border-color: rgba(245,166,35,0.4) !important;
    box-shadow: 0 0 0 3px rgba(245,166,35,0.07), 0 4px 20px rgba(0,0,0,0.3) !important;
}

.stTextInput input::placeholder { color: var(--text-3) !important; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #f5a623, #d4880a) !important;
    color: #000 !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 16px rgba(245,166,35,0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(245,166,35,0.45) !important;
}

.stButton > button:active { transform: translateY(0) !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border-mid) !important;
}

[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text-0) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: var(--text-1) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.68rem !important;
}

/* ── CODE ── */
code {
    background: rgba(245,166,35,0.07) !important;
    border: 1px solid rgba(245,166,35,0.14) !important;
    border-radius: 6px !important;
    padding: 2px 7px !important;
    font-family: 'Space Mono', monospace !important;
    color: var(--amber) !important;
    font-size: 0.8em !important;
}

pre code {
    display: block !important;
    padding: 18px !important;
    border-radius: 14px !important;
    overflow-x: auto !important;
}

/* ── MISC ── */
hr { border-color: var(--border-dim) !important; margin: 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 99px; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "response_times" not in st.session_state:
    st.session_state.response_times = []
if "preset_input" not in st.session_state:
    st.session_state.preset_input = ""
if "thinking_steps" not in st.session_state:
    st.session_state.thinking_steps = []

# ── SIDEBAR ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✦ SANJU Settings")
    st.markdown("---")

    model_name = st.selectbox(
        "⚡ MODEL",
        ["mistral-small-2506", "mistral-medium-2505", "mistral-large-latest"],
        index=0,
    )

    temperature = st.slider("🌡️ TEMPERATURE", 0.0, 1.0, 0.7, 0.05)
    max_tokens  = st.slider("📏 MAX TOKENS", 256, 4096, 1024, 64)

    st.markdown("---")
    st.markdown("### 🎭 PERSONA")
    persona = st.selectbox("Choose Persona", [
        "🧠 Smart Assistant",
        "💻 Code Expert",
        "✍️ Creative Writer",
        "🔬 Research Analyst",
        "😄 Funny Friend",
        "🔧 Custom",
    ])

    persona_prompts = {
        "🧠 Smart Assistant": "You are SANJU, a highly intelligent AI assistant. Be concise, precise, and insightful.",
        "💻 Code Expert":     "You are SANJU, an elite software engineer. Provide clean code with clear explanations. Prefer modern best practices.",
        "✍️ Creative Writer": "You are SANJU, a brilliant creative writer. Be vivid, imaginative, and emotionally resonant.",
        "🔬 Research Analyst":"You are SANJU, a meticulous research analyst. Be thorough, cite reasoning, and structure information clearly.",
        "😄 Funny Friend":    "You are SANJU, a witty and funny conversationalist. Add humor, puns, and keep things light.",
        "🔧 Custom":          "",
    }

    if persona == "🔧 Custom":
        system_prompt = st.text_area("✏️ SYSTEM PROMPT", value="You are SANJU, an advanced AI assistant.", height=100)
    else:
        system_prompt = persona_prompts[persona]
        st.markdown(f"""
        <div style='background:rgba(245,166,35,0.05);border:1px solid rgba(245,166,35,0.15);
             border-radius:10px;padding:10px 12px;font-size:0.68rem;
             font-family:"Space Mono",monospace;color:#666;line-height:1.7;'>
        {system_prompt}
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    msg_count  = len(st.session_state.messages)
    user_count = sum(1 for r, _ in st.session_state.messages if r == "user")
    avg_rt     = (sum(st.session_state.response_times) / len(st.session_state.response_times)
                  if st.session_state.response_times else 0)

    st.markdown(f"""
    <div style='font-family:"Space Mono",monospace;font-size:0.65rem;color:#3a3a60;'>
    <div style='margin-bottom:10px;display:flex;justify-content:space-between;'>
        <span>💬 MESSAGES</span><span style='color:#f5a623;font-weight:700;'>{msg_count}</span>
    </div>
    <div style='margin-bottom:10px;display:flex;justify-content:space-between;'>
        <span>👤 TURNS</span><span style='color:#f5a623;font-weight:700;'>{user_count}</span>
    </div>
    <div style='margin-bottom:10px;display:flex;justify-content:space-between;'>
        <span>⚡ AVG TIME</span><span style='color:#2dd4bf;font-weight:700;'>{avg_rt:.1f}s</span>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑️ Clear"):
            st.session_state.messages = []
            st.session_state.response_times = []
            st.rerun()
    with col_b:
        if st.button("💾 Export"):
            if st.session_state.messages:
                export_text = "\n\n".join([
                    f"{'YOU' if r == 'user' else 'SANJU'}: {c}"
                    for r, c in st.session_state.messages
                ])
                st.download_button("⬇️ Download", data=export_text,
                                   file_name="sanju_chat.txt", mime="text/plain")

# ── MAIN ─────────────────────────────────────────────
main_col, _ = st.columns([1, 0.001])

with main_col:

    # ── HEADER ──
    st.markdown("""
    <div class='sanju-header'>
        <div class='sanju-emblem'>
            <div class='sanju-emblem-ring'></div>
            <div class='sanju-emblem-inner'>✦</div>
        </div>
        <div class='sanju-wordmark'>
            <div class='sanju-name'>SAN<em>JU</em></div>
            <div class='sanju-name'><em>Empowering</em> Ideas Through<em> Intelligence</em></div>
        </div>
        <div class='online-pill'>
            <div class='online-dot'></div>
            ONLINE
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── STATS BAR ──
    if st.session_state.messages:
        short_model = model_name.replace("mistral-","").replace("-latest","").upper()
        st.markdown(f"""
        <div class='stats-bar'>
            <div class='stat-item'>
                <div class='stat-label'>MODEL</div>
                <div class='stat-value'>{short_model}</div>
            </div>
            <div class='stat-item'>
                <div class='stat-label'>TEMP</div>
                <div class='stat-value'>{temperature}</div>
            </div>
            <div class='stat-item'>
                <div class='stat-label'>MESSAGES</div>
                <div class='stat-value'>{len(st.session_state.messages)}</div>
            </div>
            <div class='stat-item'>
                <div class='stat-label'>PERSONA</div>
                <div class='stat-value'>{persona.split()[-1].upper()}</div>
            </div>
            <div class='stat-item'>
                <div class='stat-label'>AVG TIME</div>
                <div class='stat-value'>{avg_rt:.1f}s</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── WELCOME SCREEN ──
    if not st.session_state.messages:
        st.markdown("""
        <div class='welcome-wrap'>
            <span class='welcome-logo'>✦</span>
            <div class='welcome-title'>Hello, I'm SANJU</div>
            <div class='welcome-sub'><span>Your advanced </span>AI companion <span>· Ready to assist</span></div>
            <div class='starters-label'>Quick Starters</div>
        </div>
        """, unsafe_allow_html=True)

        presets = [
            "✍️ Write a poem about space",
            "💻 Explain async/await in Python",
            "🔬 Summarize quantum computing",
            "🎨 Give me 5 startup ideas",
            "😄 Tell me a clever joke",
            "🌍 Best travel tips for Japan",
        ]
        cols = st.columns(3)
        for i, preset in enumerate(presets):
            with cols[i % 3]:
                if st.button(preset, key=f"preset_{i}"):
                    st.session_state.preset_input = preset

    # ── CHAT HISTORY ──
    for idx, (role, content) in enumerate(st.session_state.messages):
        if role == "user":
            st.markdown(f"""
            <div class='msg-wrap user-wrap'>
                <div class='av av-user'>👤</div>
                <div class='bubble bubble-user'>
                    <div class='bubble-meta'>YOU</div>
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='msg-wrap'>
                <div class='av av-ai'>✦</div>
                <div class='bubble bubble-ai'>
                    <div class='bubble-meta'>
                        <span class='bubble-meta-dot'></span>
                        SANJU · {model_name}
                    </div>
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── INPUT ──
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([6, 1])

    default_val = st.session_state.preset_input
    if default_val:
        st.session_state.preset_input = ""

    with col1:
        user_input = st.text_input(
            "Message",
            value=default_val,
            placeholder="Message SANJU...",
            label_visibility="collapsed",
            key="chat_input",
        )
    with col2:
        send = st.button("↑ Send", use_container_width=True)

    # ── GENERATE ──
    if send and user_input.strip():

        lc_messages = [SystemMessage(content=system_prompt)]
        for role, content in st.session_state.messages:
            lc_messages.append(HumanMessage(content=content) if role == "user"
                                else AIMessage(content=content))
        lc_messages.append(HumanMessage(content=user_input))

        # ── THINKING PROCESS UI ──
        thinking_placeholder = st.empty()

        THINKING_STEPS = [
            ("⟳", "Reading your message..."),
            ("⟳", "Analysing intent & context..."),
            ("⟳", "Searching knowledge base..."),
            ("⟳", "Structuring response..."),
            ("⟳", "Refining output quality..."),
        ]

        def render_thinking(steps_done: int, total: int):
            steps_html = ""
            for i, (icon, label) in enumerate(THINKING_STEPS):
                if i < steps_done:
                    steps_html += f"""
                    <div class='thinking-step' style='animation-delay:{i*0.1}s'>
                        <span class='step-icon done' style='color:#2dd4bf'>✔</span>
                        <span style='color:#5a5a80;text-decoration:line-through'>{label}</span>
                    </div>"""
                elif i == steps_done:
                    steps_html += f"""
                    <div class='thinking-step' style='animation-delay:{i*0.1}s'>
                        <span class='step-icon' style='color:#f5a623'>{icon}</span>
                        <span style='color:#a0a0c0'>{label}</span>
                    </div>"""
                else:
                    steps_html += f"""
                    <div class='thinking-step' style='opacity:0.3;animation-delay:{i*0.1}s'>
                        <span class='step-icon done'>○</span>
                        <span>{label}</span>
                    </div>"""

            thinking_placeholder.markdown(f"""
            <div class='thinking-wrap'>
                <div class='av av-ai'>✦</div>
                <div class='thinking-bubble'>
                    <div class='thinking-header'>
                        ◈ &nbsp;THINKING PROCESS
                    </div>
                    {steps_html}
                    <div class='shimmer-line'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Animate through steps while model loads
        try:
            start_time = time.time()

            model = ChatMistralAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                mistral_api_key=api_key,
            )

            # Show animated thinking steps
            import threading
            result_holder = {}
            error_holder  = {}

            def call_model():
                try:
                    result_holder["response"] = model.invoke(lc_messages)
                except Exception as e:
                    error_holder["error"] = e

            thread = threading.Thread(target=call_model)
            thread.start()

            step_delay = 0.55
            for step_i in range(len(THINKING_STEPS)):
                render_thinking(step_i, len(THINKING_STEPS))
                thread.join(timeout=step_delay)
                if not thread.is_alive():
                    # Model finished early — fast-forward steps
                    for remaining in range(step_i + 1, len(THINKING_STEPS)):
                        render_thinking(remaining, len(THINKING_STEPS))
                        time.sleep(0.12)
                    break

            thread.join()  # ensure done

            if "error" in error_holder:
                raise error_holder["error"]

            elapsed  = round(time.time() - start_time, 2)
            ai_reply = result_holder["response"].content

            thinking_placeholder.empty()

            st.session_state.messages.append(("user", user_input))
            st.session_state.messages.append(("assistant", ai_reply))
            st.session_state.response_times.append(elapsed)

            st.rerun()

        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"❌ API Error: {e}")