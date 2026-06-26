"""
app.py  –  Streamlit Chat Application  •  Oracle 26ai Vector Search
Run with:  run.bat
"""
from __future__ import annotations

import logging
import os
import time

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VectorSearch · Oracle 26ai",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── logging ──────────────────────────────────────────────────────────────────
_log_file        = os.path.join(os.path.dirname(__file__), "application.log")
_handler_file    = logging.FileHandler(_log_file, encoding="utf-8")
_handler_console = logging.StreamHandler()
_handler_file.setLevel(logging.DEBUG)
_handler_console.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[_handler_file, _handler_console],
)
logger = logging.getLogger(__name__)
logger.info("App started  |  log=%s", _log_file)


# ─── DB bootstrap ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def init_db():
    import db
    with db.get_conn() as conn:
        db.ensure_app_users(conn)
    db.ensure_tables()
    db.ensure_vector_index()
    return db


# ─── session defaults ─────────────────────────────────────────────────────────
def _init_session():
    defaults = {
        "authenticated": False,
        "user":          None,
        "messages":      [],
        "mode":          "rag",
        "login_error":   "",
        "llm_provider":  os.environ.get("LLM_PROVIDER", "ollama").lower(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()


# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  —  "Deep Sea Intelligence"
#  Fonts: Syne (display) + Epilogue (body)
#  Palette: abyssal dark + bioluminescent cyan
#  Login: full-bleed split layout with animated sonar mesh
#  Main: fluid responsive layout, collapsible sidebar
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Epilogue:wght@300;400;500;600&display=swap');

/* ── design tokens ── */
:root {
    --abyss:       #060810;
    --deep:        #0b0e1a;
    --surface:     #111627;
    --surface2:    #182035;
    --surface3:    #1e2840;
    --rim:         #243050;
    --rim2:        #2e3d60;
    --cyan:        #00d4c8;
    --cyan-dim:    #004d48;
    --cyan-glow:   rgba(0,212,200,.15);
    --cyan-glow2:  rgba(0,212,200,.06);
    --cyan-pulse:  rgba(0,212,200,.35);
    --text:        #e2eaf8;
    --text2:       #8899bb;
    --text3:       #404e6a;
    --green:       #00e5a0;
    --red:         #ff4d6a;
    --amber:       #ffb830;
    --font-display:'Syne', sans-serif;
    --font-body:   'Epilogue', sans-serif;
    --r:           10px;
    --r-sm:        6px;
}

/* ── global reset ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--abyss) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

/* hide streamlit chrome */
header[data-testid="stHeader"],
footer, #MainMenu,
[data-testid="stToolbar"]  { display: none !important; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: var(--deep) !important;
    border-right: 1px solid var(--rim) !important;
    min-width: 280px !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* ── typography ── */
* { font-family: var(--font-body) !important; box-sizing: border-box; }
h1,h2,h3,.syne { font-family: var(--font-display) !important; }

/* ── inputs ── */
input[type="text"],
input[type="password"],
[data-testid="stTextInput"] input {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--rim) !important;
    border-radius: var(--r-sm) !important;
    font-size: .9rem !important;
    transition: border-color .2s, box-shadow .2s !important;
    caret-color: var(--cyan) !important;
}
input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-glow) !important;
    outline: none !important;
}

/* ── primary button ── */
[data-testid="stFormSubmitButton"] button,
button[kind="primary"] {
    background: var(--cyan) !important;
    color: var(--abyss) !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: .9rem !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
    transition: all .2s ease !important;
}
[data-testid="stFormSubmitButton"] button:hover,
button[kind="primary"]:hover {
    background: #00ffe8 !important;
    box-shadow: 0 0 28px var(--cyan-pulse), 0 4px 16px rgba(0,0,0,.4) !important;
    transform: translateY(-2px) !important;
}

/* ── secondary button ── */
[data-testid="stButton"] button {
    background: var(--surface2) !important;
    color: var(--text2) !important;
    border: 1px solid var(--rim) !important;
    border-radius: var(--r-sm) !important;
    font-size: .82rem !important;
    transition: all .15s !important;
}
[data-testid="stButton"] button:hover {
    border-color: var(--cyan-dim) !important;
    color: var(--cyan) !important;
    background: var(--surface3) !important;
}

/* ── logout button ── */
.logout-btn [data-testid="stButton"] button {
    background: transparent !important;
    color: var(--red) !important;
    border: 1px solid rgba(255,77,106,.25) !important;
}
.logout-btn [data-testid="stButton"] button:hover {
    background: rgba(255,77,106,.08) !important;
    border-color: var(--red) !important;
}

/* ── chat input ── */
[data-testid="stChatInput"] textarea {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--rim) !important;
    border-radius: var(--r) !important;
    font-size: .9rem !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-glow) !important;
}

/* ── select / radio / slider ── */
[data-testid="stRadio"] label { color: var(--text) !important; }
[data-baseweb="select"] > div {
    background: var(--surface2) !important;
    border-color: var(--rim) !important;
    color: var(--text) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: var(--cyan) !important;
}

/* scrollbar */
::-webkit-scrollbar       { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--rim2); border-radius: 2px; }

hr { border-color: var(--rim) !important; margin: 12px 0 !important; }

/* progress */
[data-testid="stProgress"] > div { background: var(--cyan) !important; }


/* ═══════════════════════════════════════════════
   LOGIN PAGE  —  full-bleed split layout
═══════════════════════════════════════════════ */

.login-split {
    display: flex;
    min-height: 100vh;
    width: 100%;
}
.login-left {
    flex: 1.1;
    background: var(--deep);
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 48px;
    border-right: 1px solid var(--rim);
}
.login-left::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 50% 50%, rgba(0,212,200,.08) 0%, transparent 70%),
        radial-gradient(ellipse 40% 40% at 20% 80%, rgba(0,212,200,.05) 0%, transparent 60%);
}
.sonar {
    position: absolute;
    width: 340px; height: 340px;
    top: 50%; left: 50%;
    transform: translate(-50%,-50%);
}
.sonar-ring {
    position: absolute; inset: 0;
    border-radius: 50%;
    border: 1px solid var(--cyan);
    opacity: 0;
    animation: sonarPulse 4s ease-out infinite;
}
.sonar-ring:nth-child(2) { animation-delay: 1.3s; }
.sonar-ring:nth-child(3) { animation-delay: 2.6s; }
@keyframes sonarPulse {
    0%   { transform: scale(.2); opacity: .6; }
    100% { transform: scale(2.2); opacity: 0; }
}
.hex-grid {
    position: absolute; inset: 0; opacity: .07;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='100'%3E%3Cpath d='M28 66L0 50V16L28 0l28 16v34z' fill='none' stroke='%2300d4c8' stroke-width='.8'/%3E%3Cpath d='M28 100L0 84V50L28 34l28 16v34z' fill='none' stroke='%2300d4c8' stroke-width='.8'/%3E%3Cpath d='M56 66L28 50V16L56 0' fill='none' stroke='%2300d4c8' stroke-width='.8'/%3E%3C/svg%3E");
    background-size: 56px 100px;
}
.login-left-content { position: relative; z-index: 2; text-align: center; }
.login-eyebrow {
    font-family: var(--font-display) !important;
    font-size: .65rem; letter-spacing: .25em; text-transform: uppercase;
    color: var(--cyan); margin-bottom: 18px;
}
.login-headline {
    font-family: var(--font-display) !important;
    font-size: clamp(2rem, 3.5vw, 3rem); font-weight: 800;
    line-height: 1.1; color: var(--text); margin-bottom: 20px;
}
.login-headline span { color: var(--cyan); }
.login-tagline {
    font-size: .88rem; color: var(--text2); line-height: 1.7;
    max-width: 320px; margin: 0 auto 36px;
}
.login-pills { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.login-pill {
    background: rgba(0,212,200,.08); border: 1px solid rgba(0,212,200,.2);
    border-radius: 20px; padding: 5px 14px;
    font-size: .72rem; color: var(--cyan); letter-spacing: .04em;
}

/* ── RIGHT PANEL ── */
.login-right {
    flex: .9; background: var(--abyss);
    display: flex; align-items: center; justify-content: center;
    padding: 48px 40px; min-width: 360px;
}
.login-form-title {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0px;
    width: 100%; /* Ensures text-align works */
    text-align: center;
}

.login-form-sub {
    font-size: 1rem;
    color: #666;
    margin-bottom: 30px;
    width: 100%;
    text-align: center;
}
.login-err {
    background: rgba(255,77,106,.07); border: 1px solid rgba(255,77,106,.25);
    border-left: 3px solid var(--red); border-radius: var(--r-sm);
    color: #ffaab5; padding: 10px 14px; font-size: .82rem; margin-bottom: 18px;
    display: flex; align-items: center; gap: 8px;
    animation: errShake .35s cubic-bezier(.36,.07,.19,.97);
}
@keyframes errShake {
    10%,90%  { transform: translateX(-2px); }
    20%,80%  { transform: translateX(4px);  }
    30%,70%  { transform: translateX(-4px); }
    40%,60%  { transform: translateX(4px);  }
    50%      { transform: translateX(-2px); }
}
.login-form-footer {
    font-size: .65rem; color: var(--text3); text-align: center;
    margin-top: 12px; letter-spacing: .08em; text-transform: uppercase;
    font-family: var(--font-display) !important;
}
.login-form-author {
    font-size: .65rem; color: var(--cyan); opacity: .5; text-align: center;
    margin-top: 6px; letter-spacing: .1em; text-transform: uppercase;
    font-family: var(--font-display) !important;
}

/* ── login page stats strip ── */
.login-stats {
    display: flex; gap: 28px; justify-content: center;
    margin-top: 48px; flex-wrap: wrap;
}
.login-stat { text-align: center; }
.login-stat-val {
    font-family: var(--font-display) !important;
    font-size: 1.4rem; font-weight: 800; color: var(--cyan); line-height: 1;
}
.login-stat-lbl {
    font-size: .65rem; color: var(--text3); letter-spacing: .08em;
    text-transform: uppercase; margin-top: 4px;
}

@media (max-width: 820px) {
    .login-split   { flex-direction: column; }
    .login-left    { min-height: 240px; padding: 40px 24px; flex: none; }
    .login-right   { padding: 36px 24px; min-width: unset; }
    .login-headline { font-size: 1.6rem; }
}


/* ═══════════════════════════════════════════════
   MAIN APP — responsive layout
═══════════════════════════════════════════════ */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 0 12px; border-bottom: 1px solid var(--rim);
    margin-bottom: 20px; flex-wrap: wrap; gap: 10px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--surface3), var(--rim2));
    border: 1px solid var(--rim2); border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}
.brand-eyebrow {
    font-family: var(--font-display) !important;
    font-size: .58rem; letter-spacing: .2em; text-transform: uppercase;
    color: var(--cyan); margin-bottom: 2px;
}
.brand-name {
    font-family: var(--font-display) !important;
    font-size: 1.05rem; font-weight: 700; color: var(--text); line-height: 1;
}
.brand-sub { font-size: .68rem; color: var(--text3); margin-top: 2px; }
.topbar-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.session-chip {
    display: flex; align-items: center; gap: 7px;
    background: var(--surface); border: 1px solid var(--rim);
    border-radius: 20px; padding: 5px 14px 5px 10px;
    font-size: .78rem; color: var(--text2);
}
.pulse-dot {
    width: 7px; height: 7px; background: var(--green);
    border-radius: 50%; flex-shrink: 0;
    animation: pulseDot 2s ease-in-out infinite;
}
@keyframes pulseDot {
    0%   { box-shadow: 0 0 0 0 rgba(0,229,160,.5); }
    70%  { box-shadow: 0 0 0 6px rgba(0,229,160,0); }
    100% { box-shadow: 0 0 0 0 rgba(0,229,160,0); }
}
.user-card {
    display: flex; align-items: center; gap: 10px;
    padding: 12px; background: var(--surface2);
    border: 1px solid var(--rim); border-radius: var(--r); margin-bottom: 10px;
}
.user-avatar {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--cyan-dim), var(--cyan));
    border-radius: 8px; display: flex; align-items: center; justify-content: center;
    font-family: var(--font-display) !important;
    font-size: .85rem; font-weight: 700; color: var(--abyss); flex-shrink: 0;
}
.user-name   { font-weight: 600; font-size: .85rem; color: var(--text); line-height: 1.2; }
.user-handle { font-size: .68rem; color: var(--text3); }
.sec-label {
    font-family: var(--font-display) !important;
    font-size: .58rem; letter-spacing: .16em; text-transform: uppercase;
    color: var(--text3); margin: 14px 0 8px;
    display: flex; align-items: center; gap: 6px;
}
.sec-label::after { content: ''; flex: 1; height: 1px; background: var(--rim); }
.badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 20px;
    font-size: .66rem; font-weight: 600; letter-spacing: .05em; text-transform: uppercase;
}
.badge-ok  { background: rgba(0,229,160,.07); color:var(--green); border:1px solid rgba(0,229,160,.2); }
.badge-err { background: rgba(255,77,106,.07); color:var(--red);   border:1px solid rgba(255,77,106,.2); }
.doc-row {
    padding: 8px 10px; border-radius: var(--r-sm);
    border: 1px solid var(--rim); background: var(--surface2);
    margin-bottom: 5px; transition: border-color .15s, background .15s;
}
.doc-row:hover { border-color: var(--rim2); background: var(--surface3); }
.doc-name   { font-size: .78rem; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 175px; }
.doc-chunks { font-size: .65rem; color: var(--text3); margin-top: 1px; }
.chat-wrap {
    display: flex; gap: 10px; margin-bottom: 18px;
    animation: bubbleIn .25s cubic-bezier(.22,1,.36,1);
}
@keyframes bubbleIn {
    from { opacity:0; transform:translateY(12px) scale(.98); }
    to   { opacity:1; transform:translateY(0) scale(1); }
}
.chat-wrap.user { flex-direction: row-reverse; }
.chat-ava {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: .82rem; flex-shrink: 0; margin-top: 2px;
}
.chat-ava.user { background: linear-gradient(135deg,var(--surface3),var(--rim2)); border:1px solid var(--rim2); }
.chat-ava.ai   { background: linear-gradient(135deg,var(--cyan-dim),rgba(0,212,200,.2)); border: 1px solid rgba(0,212,200,.3); }
.chat-bubble {
    max-width: 74%; padding: 12px 16px; border-radius: 12px;
    font-size: .875rem; line-height: 1.7; white-space: pre-wrap;
}
.chat-bubble.user { background: var(--surface2); border: 1px solid var(--rim2); border-bottom-right-radius: 3px; }
.chat-bubble.ai   { background: linear-gradient(135deg, var(--surface) 0%, rgba(0,212,200,.04) 100%); border: 1px solid rgba(0,212,200,.15); border-bottom-left-radius: 3px; }
.chunk-card {
    background: var(--surface2); border: 1px solid var(--rim);
    border-left: 3px solid var(--cyan); border-radius: var(--r-sm);
    padding: 10px 14px; font-size: .77rem; color: var(--text2);
    margin-bottom: 7px; line-height: 1.6;
}
.chunk-meta {
    font-family: var(--font-display) !important;
    font-size: .6rem; color: var(--text3);
    letter-spacing: .08em; text-transform: uppercase; margin-bottom: 5px;
}
.empty-state { text-align: center; padding: 80px 24px 60px; }
.empty-icon  { font-size: 3rem; margin-bottom: 16px; opacity: .4; animation: floatIcon 4s ease-in-out infinite; }
@keyframes floatIcon {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-8px); }
}
.empty-title { font-family:var(--font-display) !important; font-size:1.1rem; font-weight:600; color:var(--text2); margin-bottom:6px; }
.empty-sub   { font-size:.8rem; color:var(--text3); }

/* ── chat action bar ── */
.chat-action-bar {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 0 4px;
    border-top: 1px solid var(--rim);
    margin-top: 8px;
}
.msg-count {
    font-family: var(--font-display) !important;
    font-size: .62rem; letter-spacing: .1em; text-transform: uppercase;
    color: var(--text3); flex: 1;
}

/* clear button — red tint */
.clear-btn [data-testid="stButton"] button {
    background: transparent !important;
    color: var(--red) !important;
    border: 1px solid rgba(255,77,106,.22) !important;
    font-size: .75rem !important;
    padding: 4px 14px !important;
    border-radius: 20px !important;
    transition: all .15s !important;
}
.clear-btn [data-testid="stButton"] button:hover {
    background: rgba(255,77,106,.08) !important;
    border-color: var(--red) !important;
    transform: none !important;
}

/* search button — cyan accent */
.search-btn [data-testid="stButton"] button {
    background: var(--cyan) !important;
    color: var(--abyss) !important;
    border: none !important;
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: .75rem !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
    padding: 4px 18px !important;
    border-radius: 20px !important;
    transition: all .2s ease !important;
}
.search-btn [data-testid="stButton"] button:hover {
    background: #00ffe8 !important;
    box-shadow: 0 0 16px var(--cyan-glow) !important;
    transform: translateY(-1px) !important;
}

@media (max-width: 640px) {
    .chat-bubble { max-width: 88%; font-size: .82rem; }
    .topbar { flex-direction: column; align-items: flex-start; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  LOGIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_login():
    # 1. Backgrounds & Layout CSS
    st.markdown("""
    <style>
    /* Full viewport reset for login */
    [data-testid="stAppViewContainer"] > section.main > div.block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    [data-testid="stSidebar"] { display: none !important; }

    /* Left Panel: Restoring Sonar & Grid */
    .hero-panel {
        position: fixed;
        left: 0; top: 0;
        width: 60vw;
        height: 100vh;
        background: var(--deep); /* Use theme variables */
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 0;
        overflow: hidden;
        border-right: 1px solid var(--rim);
    }

    /* Right Panel Background */
    .form-panel-bg {
        position: fixed;
        right: 0; top: 0;
        width: 40vw;
        height: 100vh;
        background: var(--abyss);
        border-left: 1px solid var(--rim);
        z-index: 0;
    }

    /* Form Widget Alignment - Targets the Streamlit Container */
    [data-testid="stVerticalBlock"] > .stElementContainer {
        margin-left: 60vw !important;
        width: 35vw !important;
        z-index: 10 !important; /* Ensures form stays on top */
    }

    /* Title and Subtitle Styling */
    .login-form-title { font-size: 2.5rem; font-weight: 800; color: white; text-align: center; margin-top: 15vh; }
    .login-form-sub { font-size: 1rem; color: #666; text-align: center; margin-bottom: 30px; }
    .fl { display: block; margin-bottom: 8px; font-size: 0.75rem; color: #666; text-transform: uppercase; }

    @media (max-width: 900px) {
        .hero-panel { display: none; }
        .form-panel-bg { width: 100vw; }
        [data-testid="stVerticalBlock"] > .stElementContainer { margin-left: 0 !important; width: 90vw !important; margin: 0 auto !important; }
    }
    </style>

    <div class="hero-panel">
        <div class="hex-grid"></div>
        <div class="sonar">
            <div class="sonar-ring"></div>
            <div class="sonar-ring"></div>
            <div class="sonar-ring"></div>
        </div>
        <div class="login-left-content" style="text-align:center;">
            <div class="login-eyebrow">◈ Oracle 26ai Platform</div>
            <div class="login-headline">Semantic<br><span>Vector</span><br>Intelligence</div>
            <div class="login-tagline">Search your knowledge base using meaning, not keywords.</div>
        </div>
    </div>
    <div class="form-panel-bg"></div>
    """, unsafe_allow_html=True)

    # 2. Functional Widgets (Positioned via CSS margin-left)
    st.markdown('<div class="login-form-title">Welcome back</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-form-sub">Sign in to access the knowledge base</div>', unsafe_allow_html=True)

    if st.session_state.get('login_error'):
        st.error(st.session_state.login_error)

    with st.form("login_form", clear_on_submit=False):
        st.markdown('<span class="fl">Username</span>', unsafe_allow_html=True)
        username = st.text_input("u", placeholder="your username", label_visibility="collapsed")
        st.markdown('<span class="fl">Password</span>', unsafe_allow_html=True)
        password = st.text_input("p", type="password", placeholder="••••••••", label_visibility="collapsed")
        submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

    st.markdown('<div class="login-form-footer">Secured · PBKDF2-SHA256 · Oracle 26ai</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-form-footer">Made by Voeurng Sovann</div>', unsafe_allow_html=True)

    # 3. Auth Logic
    if submitted:
        if not username or not password:
            st.session_state.login_error = "Username and password required."
            st.rerun()
        else:
            try:
                db = init_db()
                import auth
                with db.get_conn() as conn:
                    user = auth.login(conn, username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.login_error = ""
                        st.rerun()
                    else:
                        st.session_state.login_error = "Invalid username or password."
                        st.rerun()
            except Exception:
                st.session_state.login_error = "Connection error."
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def do_logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    _init_session()
    logger.info("User logged out")
    st.rerun()


def render_message(role: str, content: str, chunks: list[dict] | None = None, response_time: float | None = None):
    avatar     = "👤" if role == "user" else "◈"
    bubble_cls = "user" if role == "user" else "ai"
    row_cls    = "user" if role == "user" else ""
    st.markdown(f"""
        <div class="chat-wrap {row_cls}">
            <div class="chat-ava {bubble_cls}">{avatar}</div>
            <div class="chat-bubble {bubble_cls}">{content}</div>
        </div>""", unsafe_allow_html=True)
    if role == "assistant" and response_time is not None:
        st.markdown(f'<div style="font-size:.75rem;color:var(--text3);margin-top:-12px;margin-bottom:8px">⏱ {response_time:.2f}s</div>', unsafe_allow_html=True)
    if chunks:
        with st.expander(f"◈ {len(chunks)} source chunk(s)", expanded=False):
            for c in chunks:
                dist     = c.get("distance")
                dist_str = f"{dist:.4f}" if dist is not None else "—"
                st.markdown(f"""
                    <div class="chunk-card">
                        <div class="chunk-meta">Doc {c.get('doc_id')} / Chunk {c.get('chunk_id')} / dist {dist_str}</div>
                        {c.get('chunk_data','')}
                    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
def render_app():
    db       = init_db()
    user     = st.session_state.user
    initials = "".join(w[0].upper() for w in user["full_name"].split()[:2]) or "U"

    st.markdown(f"""
    <div class="topbar">
      <div class="brand">
        <div class="brand-icon">◈</div>
        <div>
          <div class="brand-eyebrow">Oracle 26ai</div>
          <div class="brand-name">Vector Search</div>
          <div class="brand-sub">Semantic knowledge base · ONNX · HNSW</div>
        </div>
      </div>
      <div class="topbar-right">
        <div class="session-chip">
          <div class="pulse-dot"></div>
          {user['full_name']}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"""
        <div class="user-card">
          <div class="user-avatar">{initials}</div>
          <div>
            <div class="user-name">{user['full_name']}</div>
            <div class="user-handle">@{user['username']}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪  Sign Out", use_container_width=True):
            do_logout()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-label">System</div>', unsafe_allow_html=True)
        try:
            with db.get_conn():
                pass
            st.markdown('<span class="badge badge-ok">⬤ &nbsp;DB Connected</span>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown('<span class="badge badge-err">✕ &nbsp;DB Error</span>', unsafe_allow_html=True)
            st.error(str(e))

        st.markdown('<div class="sec-label">Answer Mode</div>', unsafe_allow_html=True)
        mode = st.radio(
            "mode",
            ["rag", "search"],
            format_func=lambda m: "🤖  RAG — Ollama" if m == "rag" else "🔍  Pure Vector Search",
            label_visibility="collapsed",
            key="mode",
        )

        from rag import is_rag_available, list_models, default_model

        # ── runtime provider switcher ──────────────────────────────────────────
        # Only show providers that are actually configured
        _prov_options = {"ollama": "🖥  Ollama (local)"}
        if os.environ.get("GEMINI_API_KEY", "").strip():
            _prov_options["gemini"] = "✨ Google Gemini"

        if mode == "rag":
            st.markdown('<div class="sec-label">LLM Provider</div>', unsafe_allow_html=True)
            _prov_keys   = list(_prov_options.keys())
            _prov_labels = list(_prov_options.values())
            _cur_idx     = _prov_keys.index(st.session_state.llm_provider) \
                           if st.session_state.llm_provider in _prov_keys else 0
            _chosen_label = st.radio(
                "llm_provider_radio", _prov_labels,
                index=_cur_idx, label_visibility="collapsed",
            )
            _chosen_prov = _prov_keys[_prov_labels.index(_chosen_label)]
            if _chosen_prov != st.session_state.llm_provider:
                st.session_state.llm_provider = _chosen_prov
                st.rerun()

            # push choice into env so rag.py picks it up
            os.environ["LLM_PROVIDER"] = st.session_state.llm_provider

            if is_rag_available():
                models      = list_models()
                default_mdl = default_model()
                default_idx = models.index(default_mdl) if default_mdl in models else 0
                selected_model = st.selectbox("Model", models, index=default_idx)
            else:
                if st.session_state.llm_provider == "gemini":
                    st.warning("Cannot reach Gemini API — check GEMINI_API_KEY in .env", icon="⚠️")
                else:
                    st.warning(
                        f"Ollama not reachable at\n"
                        f"`{os.environ.get('OLLAMA_BASE_URL','http://localhost:11434/api')}`"
                        "\n\nStart with: `ollama serve`",
                        icon="⚠️",
                    )
                selected_model = default_model()
        else:
            selected_model = None

        st.markdown('<div class="sec-label">Search</div>', unsafe_allow_html=True)
        top_k           = st.slider("Top K results", 1, 20, int(os.environ.get("VECTOR_TOP_K", 5)))
        distance_metric = st.selectbox("Distance metric", ["COSINE", "DOT", "EUCLIDEAN"], index=0)

        st.markdown('<div class="sec-label">Upload Documents</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "drop", accept_multiple_files=True,
            type=["pdf", "docx", "txt", "md", "csv"],
            label_visibility="collapsed",
        )
        chunk_size = st.slider("Chunk size (words)", 100, 1000, 500, step=50)
        overlap    = st.slider("Overlap (words)", 0, 200, 50, step=10)

        if uploaded_files and st.button("⬆  Ingest Selected Files", use_container_width=True):
            from chunker import extract_text, chunk_text
            progress = st.progress(0, text="Starting …")
            for idx, f in enumerate(uploaded_files):
                progress.progress(idx / len(uploaded_files), text=f"Processing {f.name} …")
                try:
                    raw    = f.read()
                    text   = extract_text(f.name, raw)
                    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
                    doc_id = db.insert_document(f.name, raw)
                    db.insert_chunks(doc_id, chunks)
                    st.success(f"✓  {f.name}  →  {len(chunks)} chunks", icon="✅")
                    logger.info("Ingested %s  chunks=%d  doc_id=%d", f.name, len(chunks), doc_id)
                except Exception as e:
                    logger.exception("Ingest failed for %s", f.name)
                    st.error(f"✕  {f.name}: {type(e).__name__}: {e}")
            progress.progress(1.0, text="Done")
            time.sleep(0.5)
            st.rerun()

        st.markdown('<div class="sec-label">Knowledge Base</div>', unsafe_allow_html=True)
        try:
            docs = db.list_documents()
            if docs:
                for doc in docs:
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        st.markdown(f"""
                        <div class="doc-row">
                          <div class="doc-name" title="{doc['name']}">{doc['name']}</div>
                          <div class="doc-chunks">{doc['chunk_count']} chunks</div>
                        </div>""", unsafe_allow_html=True)
                    with c2:
                        if st.button("✕", key=f"del_{doc['id']}", help="Delete"):
                            db.delete_document(doc["id"])
                            st.rerun()
            else:
                st.caption("No documents yet.")
        except Exception as e:
            st.warning(f"Could not load docs: {e}")

    if not st.session_state.messages:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">◈</div>
          <div class="empty-title">Ready to search</div>
          <div class="empty-sub">Upload documents in the sidebar, then ask anything below.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── action bar above messages ─────────────────────────────────────────
        msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        col_count, col_spacer, col_clear = st.columns([3, 6, 2])
        with col_count:
            st.markdown(
                f'<div class="msg-count">{msg_count} question{"s" if msg_count != 1 else ""}</div>',
                unsafe_allow_html=True,
            )
        with col_clear:
            st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
            if st.button("🗑  Clear", key="clear_messages", help="Clear all messages"):
                st.session_state.messages = []
                logger.info("Chat history cleared by %s", user["username"])
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        render_message(msg["role"], msg["content"], msg.get("chunks"), msg.get("response_time"))

    # ── chat input + search button ──────────────────────────────────────────────
    prompt = st.chat_input("Ask anything … (press Enter to search)")
    st.markdown('<div style="display:flex;gap:8px;margin-top:8px">', unsafe_allow_html=True)
    col_search, col_spacer = st.columns([1, 9])
    with col_search:
        search_clicked = st.button("◈ Search", key="search_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # trigger on chat_input Enter OR Search button click
    query = prompt or (st.session_state.get("_last_prompt") if search_clicked else None)
    if search_clicked and not st.session_state.get("_last_prompt"):
        st.warning("Type a question first.", icon="⚠️")
        query = None

    if query:
        st.session_state["_last_prompt"] = query
        st.session_state.messages.append({"role": "user", "content": query})
        render_message("user", query)

        start_time = time.time()
        with st.spinner("Searching knowledge base …"):
            try:
                chunks = db.vector_search(query, top_k=top_k, distance=distance_metric)
            except Exception as e:
                st.error(f"Vector search failed: {e}")
                logger.exception("Vector search error")
                chunks = []

        if st.session_state.mode == "rag" and is_rag_available():
            with st.spinner(f"Generating answer with {selected_model} …"):
                try:
                    from rag import generate_answer
                    answer = generate_answer(query, chunks, model=selected_model)
                except Exception as e:
                    answer = f"RAG error: {e}"
                    logger.exception("RAG error")
        else:
            if chunks:
                lines = [f"**Top {len(chunks)} matches**\n"]
                for i, c in enumerate(chunks):
                    dist     = c.get("distance")
                    dist_str = f"{dist:.4f}" if dist is not None else "—"
                    preview  = c["chunk_data"][:300].replace("\n", " ")
                    lines.append(f"**#{i+1}** `dist={dist_str}`\n{preview}…")
                answer = "\n\n".join(lines)
            else:
                answer = "No matching chunks found in the knowledge base."

        response_time = round(time.time() - start_time, 2)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "chunks": chunks, "response_time": response_time}
        )
        render_message("assistant", answer, chunks, response_time)


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    render_login()
else:
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] > section.main > div.block-container {
        padding: 2rem 1rem 4rem 1rem !important;
        max-width: 1200px !important;
    }
    [data-testid="stSidebar"] { display: block !important; }
    </style>
    """, unsafe_allow_html=True)
    render_app()
