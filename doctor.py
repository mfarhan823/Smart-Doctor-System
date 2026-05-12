import streamlit as st
import sqlite3
import os
import smtplib
import hashlib
import threading
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, datetime, timedelta
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import re

load_dotenv()

UPLOAD_DIR = Path("profile_pics")
UPLOAD_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════
#  GLOBAL CSS — PREMIUM DARK OVAL THEME
# ══════════════════════════════════════════════

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

:root {
    --bg-base:     #ffffff;
    --bg-surface:  #0d1628;
    --bg-elevated: #111e35;
    --teal:        #00e5c7;
    --teal-dim:    #00b89e;
    --teal-glow:   rgba(0, 229, 199, 0.15);
    --coral:       #ff6b6b;
    --gold:        #f5c842;
    --text-primary:   #000000;
    --text-secondary: #2c3e50;
    --text-muted:     #7f8c8d;
    --border:      rgba(0, 229, 199, 0.14);
    --border-hover:rgba(0, 229, 199, 0.38);
    --glass:       rgba(255,255,255,0.03);
    --glass-hover: rgba(255,255,255,0.06);
    --radius-pill: 50px;
    --radius-card: 20px;
    --radius-sm:   12px;
    --shadow-teal: 0 0 40px rgba(0,229,199,0.15);
    --shadow-card: 0 8px 40px rgba(0,0,0,0.5);
}

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif !important;
    background: var(--bg-base) !important;
    color: var(--text-primary) !important;
}

/* ── Scrollable page bg gradient ── */
.main .block-container {
    background: transparent !important;
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1100px !important;
}

/* Animated deep space background */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: -2;
    background:
        radial-gradient(ellipse 70% 50% at 15% 5%,  rgba(0,229,199,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 50% 70% at 85% 95%, rgba(255,107,107,0.06) 0%, transparent 55%),
        radial-gradient(ellipse 35% 35% at 55% 45%, rgba(245,200,66,0.04) 0%, transparent 55%),
        var(--bg-base);
}

/* Subtle animated grid overlay */
body::after {
    content: '';
    position: fixed;
    inset: 0;
    z-index: -1;
    background-image:
        linear-gradient(rgba(0,229,199,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,199,0.025) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 30%, transparent 100%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #f8f9fa !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 0 !important;
}

/* ── Sidebar brand ── */
.sidebar-brand {
    background: linear-gradient(145deg, #00b89e 0%, #007a7a 60%, #005560 100%);
    padding: 30px 22px 24px;
    margin: 0 -1rem 1.5rem;
    position: relative;
    overflow: hidden;
    border-radius: 0 0 28px 28px;
}
.sidebar-brand::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 120px; height: 120px;
    border-radius: 50%;
    background: rgba(255,255,255,0.10);
}
.sidebar-brand::after {
    content: '';
    position: absolute;
    bottom: -25px; left: -25px;
    width: 80px; height: 80px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
}
.brand-icon { font-size: 2.6rem; line-height: 1; margin-bottom: 8px; display: block; }
.brand-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #fff;
    line-height: 1.2;
    margin: 0;
    letter-spacing: -0.02em;
}
.brand-sub {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.65);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 4px;
    display: block;
}

/* ── User badge ── */
.user-badge {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: var(--radius-pill);
    padding: 10px 16px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: fadeUp 0.5s ease;
}
.user-avatar {
    width: 38px; height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--teal), #007a7a);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    box-shadow: 0 0 0 3px rgba(0,229,199,0.25);
}
.user-name {
    font-weight: 700;
    font-size: 0.88rem;
    color: var(--text-primary);
    line-height: 1.2;
}
.user-role {
    font-size: 0.68rem;
    color: var(--teal);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Nav radio ── */
div[data-testid="stRadio"] > label {
    display: none !important;
}
div[data-testid="stRadio"] > div {
    gap: 4px !important;
    flex-direction: column !important;
}
div[data-testid="stRadio"] label {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: var(--radius-pill) !important;
    padding: 10px 18px !important;
    margin-bottom: 2px !important;
    transition: all 0.22s ease !important;
    cursor: pointer !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    color: var(--text-secondary) !important;
    width: 100% !important;
}
div[data-testid="stRadio"] label:hover {
    background: var(--glass-hover) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
    transform: translateX(4px) !important;
}
div[data-testid="stRadio"] label[data-checked="true"],
div[data-testid="stRadio"] label[aria-checked="true"] {
    background: linear-gradient(135deg, rgba(0,229,199,0.16), rgba(0,229,199,0.05)) !important;
    border-color: var(--teal) !important;
    color: var(--teal) !important;
    box-shadow: 0 2px 16px rgba(0,229,199,0.12) !important;
}

/* ── Sidebar stat metrics ── */
div[data-testid="metric-container"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 12px 14px !important;
}
div[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--teal) !important;
    font-weight: 700 !important;
    font-size: 1.4rem !important;
}

/* ── Headings ── */
h1, h2, h3, h4 {
    font-family: 'Sora', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
}

/* ── Page hero ── */
.page-hero {
    background: linear-gradient(135deg, rgba(0,229,199,0.10) 0%, rgba(0,184,158,0.05) 50%, transparent 100%);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 32px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    animation: fadeUp 0.5s ease;
}
.page-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -20px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,229,199,0.12), transparent 70%);
    pointer-events: none;
}
.page-hero::after {
    content: '';
    position: absolute;
    bottom: 0; right: 0;
    width: 40%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,229,199,0.03));
    pointer-events: none;
}
.page-hero-icon {
    font-size: 2.6rem;
    margin-bottom: 10px;
    display: block;
}
.page-hero h2 {
    color: var(--text-primary) !important;
    margin: 0 0 6px !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
}
.page-hero p {
    color: var(--text-secondary);
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* ── Cards / containers ── */
.card {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: var(--radius-card);
    padding: 22px 24px;
    transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
    animation: fadeUp 0.4s ease;
}
.card:hover {
    border-color: var(--border-hover);
    box-shadow: 0 6px 28px rgba(0,229,199,0.08);
    transform: translateY(-2px);
}

/* Streamlit containers */
div[data-testid="stVerticalBlock"] > div > div[data-testid="stContainer"] > div {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-card) !important;
    padding: 22px !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
}
div[data-testid="stVerticalBlock"] > div > div[data-testid="stContainer"] > div:hover {
    border-color: var(--border-hover) !important;
    box-shadow: 0 4px 24px rgba(0,229,199,0.07) !important;
}

/* ── Doctor card ── */
.doc-card {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 22px 24px;
    margin-bottom: 14px;
    transition: all 0.3s ease;
    animation: fadeUp 0.4s ease;
    position: relative;
    overflow: hidden;
}
.doc-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--teal), transparent);
    border-radius: 3px 0 0 3px;
    opacity: 0;
    transition: opacity 0.3s ease;
}
.doc-card:hover {
    border-color: var(--border-hover);
    box-shadow: 0 8px 36px rgba(0,229,199,0.10);
    transform: translateY(-3px);
}
.doc-card:hover::before { opacity: 1; }
.doc-name {
    font-family: 'Sora', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary) !important;
    margin: 0 0 4px;
}
.doc-spec {
    color: var(--teal);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin: 0 0 10px;
}
.doc-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(0,229,199,0.10);
    border: 1px solid rgba(0,229,199,0.28);
    border-radius: var(--radius-pill);
    padding: 3px 12px;
    font-size: 0.74rem;
    color: var(--teal);
    font-weight: 600;
}
.doc-badge-busy {
    background: rgba(255,107,107,0.10);
    border-color: rgba(255,107,107,0.28);
    color: var(--coral);
}
.info-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.80rem;
    color: var(--text-secondary) !important;
    margin-right: 10px;
    margin-bottom: 4px;
}

/* ── Inputs ── */
input, textarea, select,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.88rem !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
input:focus, textarea:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 3px rgba(0,229,199,0.12) !important;
    outline: none !important;
}
label,
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stFileUploader"] label,
div[data-testid="stSlider"] label {
    color: var(--text-secondary) !important;
    font-size: 0.80rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    margin-bottom: 4px !important;
}
/* Selectbox text */
div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
    color: var(--text-primary) !important;
}
/* Slider label */
div[data-testid="stSlider"] p {
    color: var(--text-primary) !important;
}

/* ── Buttons (primary) ── */
button[kind="primary"],
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, var(--teal) 0%, var(--teal-dim) 100%) !important;
    border: none !important;
    border-radius: var(--radius-pill) !important;
    color: #050c18 !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.01em !important;
    padding: 11px 26px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(0,229,199,0.28) !important;
    text-transform: none !important;
}
button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 30px rgba(0,229,199,0.42) !important;
    filter: brightness(1.07) !important;
}
button[kind="primary"]:active,
div[data-testid="stFormSubmitButton"] button:active {
    transform: translateY(0) scale(0.99) !important;
}

/* ── Buttons (secondary) ── */
button[kind="secondary"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-pill) !important;
    color: var(--text-primary) !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.22s ease !important;
}
button[kind="secondary"]:hover {
    border-color: var(--teal) !important;
    color: var(--teal) !important;
    background: rgba(0,229,199,0.07) !important;
    transform: translateY(-1px) !important;
}

/* Logout button */
button[kind="secondary"]:has(p:contains("Logout")),
button[kind="secondary"][data-testid*="logout"] {
    border-color: rgba(255,107,107,0.3) !important;
    color: var(--coral) !important;
}
button[kind="secondary"]:has(p:contains("Logout")):hover {
    background: rgba(255,107,107,0.08) !important;
    border-color: var(--coral) !important;
}

/* ── Alerts / notifications ── */
div[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    border: none !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.88rem !important;
}
div[data-testid="stAlert"] p {
    color: var(--text-primary) !important;
}
/* Success */
div[data-testid="stAlert"][data-baseweb="notification"][kind="positive"] {
    background: rgba(0,229,199,0.08) !important;
    border-left: 3px solid var(--teal) !important;
}
/* Warning */
div[data-testid="stAlert"][data-baseweb="notification"][kind="warning"] {
    background: rgba(245,200,66,0.08) !important;
    border-left: 3px solid var(--gold) !important;
}
/* Error */
div[data-testid="stAlert"][data-baseweb="notification"][kind="negative"] {
    background: rgba(255,107,107,0.08) !important;
    border-left: 3px solid var(--coral) !important;
}
/* Info */
div[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(0,229,199,0.06) !important;
    border-left: 3px solid rgba(0,229,199,0.5) !important;
}

/* ── Tabs ── */
div[data-testid="stTabs"] button {
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: var(--text-secondary) !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    transition: color 0.2s ease !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--teal) !important;
    border-bottom: 2px solid var(--teal) !important;
}
div[data-testid="stTabs"] {
    border-bottom: 1px solid var(--border) !important;
}

/* ── Chat messages ── */
div[data-testid="stChatMessage"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    margin-bottom: 10px !important;
    animation: fadeUp 0.3s ease !important;
    padding: 14px 18px !important;
}
div[data-testid="stChatMessage"] p {
    color: var(--text-primary) !important;
    line-height: 1.65 !important;
}
div[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}

/* ── Divider ── */
hr {
    border-color: var(--border) !important;
    margin: 20px 0 !important;
}

/* ── Status badges ── */
.status-pending  { color: var(--gold) !important;  font-weight: 700 !important; }
.status-confirm  { color: var(--teal) !important;  font-weight: 700 !important; }
.status-cancel   { color: var(--coral) !important; font-weight: 700 !important; }

/* ── Auth page ── */
.auth-hero {
    text-align: center;
    padding: 44px 0 32px;
    animation: fadeUp 0.6s ease;
}
.auth-logo {
    width: 90px; height: 90px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--teal), #006e6e);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 2.8rem;
    margin: 0 auto 18px;
    box-shadow: 0 0 0 10px rgba(0,229,199,0.08), 0 0 0 20px rgba(0,229,199,0.04);
    animation: pulsate 3s ease-in-out infinite;
}
@keyframes pulsate {
    0%, 100% { box-shadow: 0 0 0 10px rgba(0,229,199,0.08), 0 0 0 20px rgba(0,229,199,0.04); }
    50%       { box-shadow: 0 0 0 14px rgba(0,229,199,0.12), 0 0 0 28px rgba(0,229,199,0.06); }
}
.auth-title {
    font-family: 'Sora', sans-serif;
    font-size: 2.0rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--teal) 0%, #00ffe8 50%, var(--gold) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: 8px;
    letter-spacing: -0.03em;
}
.auth-sub {
    color: var(--text-secondary);
    font-size: 0.88rem;
    line-height: 1.5;
}

/* ── Auth card ── */
.auth-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 34px 30px;
    backdrop-filter: blur(16px);
    animation: fadeUp 0.7s ease;
}

/* ── Form container ── */
div[data-testid="stForm"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-card) !important;
    padding: 26px !important;
}

/* ── Appointment row ── */
.appt-row {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: border-color 0.25s ease, transform 0.25s ease;
    animation: fadeUp 0.4s ease;
}
.appt-row:hover {
    border-color: var(--border-hover);
    transform: translateY(-1px);
}
.appt-row p {
    color: var(--text-primary) !important;
}
.appt-row .muted {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
}

/* ── AI info box ── */
.ai-box {
    background: linear-gradient(135deg, rgba(0,229,199,0.08), rgba(0,120,120,0.05));
    border: 1px solid rgba(0,229,199,0.22);
    border-radius: 16px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    margin: 12px 0;
}
.ai-box::after {
    content: '✦';
    position: absolute;
    top: 14px; right: 18px;
    font-size: 1rem;
    color: var(--teal);
    opacity: 0.35;
}
.ai-box p {
    color: var(--text-primary) !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    margin: 0 !important;
}
.ai-box-label {
    color: var(--teal) !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
    margin-bottom: 8px !important;
}

/* ── Demo hint ── */
.demo-hint {
    background: rgba(245,200,66,0.05);
    border: 1px solid rgba(245,200,66,0.18);
    border-radius: var(--radius-sm);
    padding: 14px 16px;
    font-size: 0.82rem;
    color: #c8a840;
    margin-top: 12px;
    line-height: 1.6;
}
.demo-hint strong { color: var(--gold); }

/* ── Profile avatar ── */
.profile-avatar-wrap {
    width: 72px; height: 72px;
    border-radius: 50%;
    border: 2px solid var(--teal);
    overflow: hidden;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #0a2030, #0d3040);
    box-shadow: 0 0 0 4px rgba(0,229,199,0.10);
    flex-shrink: 0;
}

/* ── Caption / small text ── */
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li,
div[data-testid="stMarkdownContainer"] span {
    color: var(--text-primary) !important;
}
.stCaption, div[data-testid="stCaption"] {
    color: var(--text-secondary) !important;
    font-size: 0.80rem !important;
}
small, .caption-text {
    color: var(--text-secondary) !important;
}

/* ── Selectbox dropdown ── */
div[role="listbox"] {
    background: #0d1628 !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
div[role="option"] {
    color: var(--text-primary) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.88rem !important;
}
div[role="option"]:hover {
    background: var(--glass-hover) !important;
    color: var(--teal) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,229,199,0.25); border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: var(--teal); }

/* ── Animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── File uploader ── */
div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.025) !important;
    border: 1px dashed var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
div[data-testid="stFileUploader"] section {
    background: transparent !important;
}

/* ── Date input ── */
div[data-testid="stDateInput"] input {
    color: var(--text-primary) !important;
}

/* ── Number input ── */
div[data-testid="stNumberInput"] button {
    background: var(--glass) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}

/* ── Remove extra whitespace/raw HTML showing ── */
.element-container:has(> .stMarkdownContainer > p > .appt-row) {
    margin-bottom: 0 !important;
}

/* Fix: hide any raw closing tags that may render */
.stMarkdownContainer p:empty { display: none !important; }
</style>
"""

# ══════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════

def get_conn():
    conn = sqlite3.connect("smart_doctor.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        display_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, specialization TEXT, city TEXT,
        consultation_type TEXT, experience INTEGER DEFAULT 0,
        rating REAL DEFAULT 4.0, contact TEXT,
        available INTEGER DEFAULT 1,
        email TEXT DEFAULT '',
        profile_pic TEXT DEFAULT '',
        username TEXT DEFAULT ''
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT, patient_contact TEXT,
        patient_email TEXT DEFAULT '',
        doctor_name TEXT, appt_date TEXT, appt_time TEXT,
        problem TEXT, status TEXT DEFAULT 'Pending',
        reminder_sent INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_name TEXT, patient_name TEXT,
        contact TEXT, problem TEXT,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # Migrations
    for col, defn in [("email","TEXT DEFAULT ''"),("profile_pic","TEXT DEFAULT ''"),("username","TEXT DEFAULT ''")]:
        try:
            c.execute(f"ALTER TABLE doctors ADD COLUMN {col} {defn}"); conn.commit()
        except sqlite3.OperationalError:
            pass

    for col, defn in [("patient_email","TEXT DEFAULT ''"),("reminder_sent","INTEGER DEFAULT 0")]:
        try:
            c.execute(f"ALTER TABLE appointments ADD COLUMN {col} {defn}"); conn.commit()
        except sqlite3.OperationalError:
            pass

    c.execute("UPDATE doctors SET email='fsohail985@gmail.com' WHERE email='' OR email IS NULL")
    conn.commit()

    c.execute("SELECT COUNT(*) FROM doctors")
    if c.fetchone()[0] == 0:
        sample = [
            ("Dr. Ahmed Raza",    "Cardiologist",     "Lahore",    "Both",     12, 4.8, "03001234567", 1, "fsohail985@gmail.com", "", "dr_ahmed"),
            ("Dr. Sara Khan",     "Dermatologist",    "Karachi",   "Online",    7, 4.5, "03111234567", 1, "fsohail985@gmail.com", "", "dr_sara"),
            ("Dr. Imran Malik",   "Orthopedic",       "Islamabad", "Physical", 15, 4.7, "03211234567", 1, "fsohail985@gmail.com", "", "dr_imran"),
            ("Dr. Nadia Hussain", "Neurologist",      "Lahore",    "Both",     10, 4.6, "03311234567", 0, "fsohail985@gmail.com", "", "dr_nadia"),
            ("Dr. Bilal Chaudhry","General Physician","Karachi",   "Online",    5, 4.3, "03411234567", 1, "fsohail985@gmail.com", "", "dr_bilal"),
            ("Dr. Fatima Zaidi",  "Gynecologist",     "Islamabad", "Physical",  9, 4.9, "03511234567", 1, "fsohail985@gmail.com", "", "dr_fatima"),
            ("Dr. Usman Ali",     "Psychiatrist",     "Lahore",    "Online",    8, 4.4, "03611234567", 1, "fsohail985@gmail.com", "", "dr_usman"),
            ("Dr. Hina Mirza",    "Pediatrician",     "Karachi",   "Both",     11, 4.7, "03711234567", 1, "fsohail985@gmail.com", "", "dr_hina"),
        ]
        c.executemany(
            "INSERT INTO doctors (name,specialization,city,consultation_type,experience,rating,contact,available,email,profile_pic,username) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            sample
        )

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        sample_users = [
            ("dr_ahmed",  hash_password("doctor123"), "doctor",  "Dr. Ahmed Raza"),
            ("dr_sara",   hash_password("doctor123"), "doctor",  "Dr. Sara Khan"),
            ("dr_imran",  hash_password("doctor123"), "doctor",  "Dr. Imran Malik"),
            ("dr_nadia",  hash_password("doctor123"), "doctor",  "Dr. Nadia Hussain"),
            ("dr_bilal",  hash_password("doctor123"), "doctor",  "Dr. Bilal Chaudhry"),
            ("dr_fatima", hash_password("doctor123"), "doctor",  "Dr. Fatima Zaidi"),
            ("dr_usman",  hash_password("doctor123"), "doctor",  "Dr. Usman Ali"),
            ("dr_hina",   hash_password("doctor123"), "doctor",  "Dr. Hina Mirza"),
            ("patient1",  hash_password("patient123"), "patient", "Ali Hassan"),
            ("patient2",  hash_password("patient123"), "patient", "Fatima Noor"),
        ]
        c.executemany(
            "INSERT OR IGNORE INTO users (username,password_hash,role,display_name) VALUES (?,?,?,?)",
            sample_users
        )

    conn.commit()
    conn.close()


def db_login(username, password):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password_hash=?",
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def db_register_user(username, password, role, display_name):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (username,password_hash,role,display_name) VALUES (?,?,?,?)",
            (username, hash_password(password), role, display_name)
        )
        conn.commit(); conn.close()
        return True, "Registered successfully"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already taken"

def db_search_doctors(city="", spec=""):
    conn = get_conn()
    q = "SELECT * FROM doctors WHERE 1=1"; p = []
    if city.strip():
        q += " AND LOWER(city) LIKE ?"; p.append(f"%{city.lower()}%")
    if spec.strip():
        q += " AND LOWER(specialization) LIKE ?"; p.append(f"%{spec.lower()}%")
    q += " ORDER BY rating DESC"
    result = [dict(r) for r in conn.execute(q, p).fetchall()]
    conn.close(); return result

def db_get_all_doctors():
    conn = get_conn()
    result = [dict(r) for r in conn.execute("SELECT * FROM doctors ORDER BY rating DESC").fetchall()]
    conn.close(); return result

def db_get_doctor_by_username(username):
    conn = get_conn()
    row = conn.execute("SELECT * FROM doctors WHERE username=?", (username,)).fetchone()
    conn.close(); return dict(row) if row else None

def db_add_doctor(name, spec, city, ctype, exp, contact, rating, email, pic_path, username):
    conn = get_conn()
    conn.execute(
        "INSERT INTO doctors (name,specialization,city,consultation_type,experience,contact,rating,email,profile_pic,username) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (name, spec, city, ctype, exp, contact, rating, email, pic_path, username)
    )
    conn.commit(); conn.close()

def db_update_doctor_pic(doctor_id, pic_path):
    conn = get_conn()
    conn.execute("UPDATE doctors SET profile_pic=? WHERE id=?", (pic_path, doctor_id))
    conn.commit(); conn.close()

def db_toggle_availability(doctor_id, status):
    conn = get_conn()
    conn.execute("UPDATE doctors SET available=? WHERE id=?", (status, doctor_id))
    conn.commit(); conn.close()

def db_update_appointment_status(appt_id, new_status):
    conn = get_conn()
    conn.execute("UPDATE appointments SET status=? WHERE id=?", (new_status, appt_id))
    conn.commit(); conn.close()

def db_book_appointment(patient, contact, patient_email, doctor_name, appt_date, appt_time, problem):
    conn = get_conn()
    existing = conn.execute(
        "SELECT * FROM appointments WHERE doctor_name=? AND appt_date=? AND appt_time=? AND status!='Cancelled'",
        (doctor_name, str(appt_date), str(appt_time))
    ).fetchone()
    conn.close()
    if existing: return False
    conn = get_conn()
    conn.execute(
        "INSERT INTO appointments (patient_name,patient_contact,patient_email,doctor_name,appt_date,appt_time,problem) VALUES (?,?,?,?,?,?,?)",
        (patient, contact, patient_email, doctor_name, str(appt_date), str(appt_time), problem)
    )
    conn.commit(); conn.close(); return True

def db_get_appointments(doctor_name=None, patient_name=None):
    conn = get_conn()
    if doctor_name:
        result = [dict(r) for r in conn.execute(
            "SELECT * FROM appointments WHERE doctor_name=? ORDER BY appt_date ASC, appt_time ASC",
            (doctor_name,)
        ).fetchall()]
    elif patient_name:
        result = [dict(r) for r in conn.execute(
            "SELECT * FROM appointments WHERE patient_name=? ORDER BY appt_date ASC",
            (patient_name,)
        ).fetchall()]
    else:
        result = [dict(r) for r in conn.execute(
            "SELECT * FROM appointments ORDER BY appt_date ASC, appt_time ASC"
        ).fetchall()]
    conn.close(); return result

def db_get_pending_reminders():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    conn = get_conn()
    result = [dict(r) for r in conn.execute(
        "SELECT * FROM appointments WHERE appt_date=? AND status!='Cancelled' AND reminder_sent=0 AND patient_email!=''",
        (tomorrow,)
    ).fetchall()]
    conn.close(); return result

def db_mark_reminder_sent(appt_id):
    conn = get_conn()
    conn.execute("UPDATE appointments SET reminder_sent=1 WHERE id=?", (appt_id,))
    conn.commit(); conn.close()

def db_get_doctor_slots(doctor_name, appt_date):
    conn = get_conn()
    taken = [r[0] for r in conn.execute(
        "SELECT appt_time FROM appointments WHERE doctor_name=? AND appt_date=? AND status!='Cancelled'",
        (doctor_name, str(appt_date))
    ).fetchall()]
    conn.close(); return taken

def db_save_message(doctor_name, patient_name, contact, problem):
    conn = get_conn()
    conn.execute(
        "INSERT INTO messages (doctor_name,patient_name,contact,problem) VALUES (?,?,?,?)",
        (doctor_name, patient_name, contact, problem)
    )
    conn.commit(); conn.close()

def db_get_stats():
    conn = get_conn()
    d = conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    a = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    m = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    conn.close(); return d, a, m


# ══════════════════════════════════════════════
#  EMAIL
# ══════════════════════════════════════════════

def send_email(to_email, subject, body):
    try:
        gmail  = os.getenv("GMAIL_ADDRESS","").strip()
        app_pw = os.getenv("GMAIL_APP_PASSWORD","").strip()
        if not gmail:   return False, "GMAIL_ADDRESS not set in .env"
        if not app_pw:  return False, "GMAIL_APP_PASSWORD not set in .env"
        if not to_email: return False, "No recipient email"
        msg = MIMEMultipart()
        msg["From"] = gmail; msg["To"] = to_email; msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as s:
            s.ehlo(); s.starttls(); s.ehlo(); s.login(gmail, app_pw)
            s.sendmail(gmail, to_email, msg.as_string())
        return True, "Sent"
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail auth failed — check App Password"
    except Exception as e:
        return False, f"Email error: {e}"

def notify_doctor_appointment(doctor_name, doctor_email, patient_name, contact, appt_date, appt_time, problem):
    body = f"""New appointment booked for {doctor_name}

Patient : {patient_name}
Contact : {contact}
Date    : {appt_date}
Time    : {appt_time}
Problem : {problem or 'Not specified'}

Log in to Smart Doctor Connect to confirm or reschedule.
"""
    ok, _ = send_email(doctor_email, f"New Appointment — {patient_name}", body)
    return ok

def notify_doctor_message(doctor_name, doctor_email, patient_name, contact, problem):
    body = f"""Patient reached {doctor_name} via AI chatbot.

Patient : {patient_name}
Contact : {contact}
Message : {problem}
Time    : {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    ok, _ = send_email(doctor_email, f"New Patient Message — {patient_name}", body)
    return ok

def send_appointment_reminder(patient_email, patient_name, doctor_name, appt_date, appt_time):
    body = f"""Dear {patient_name},

Reminder: Your appointment is TOMORROW.

Doctor : {doctor_name}
Date   : {appt_date}
Time   : {appt_time}

Please be on time. Contact clinic to reschedule if needed.
Smart Doctor Connect AI
"""
    ok, _ = send_email(patient_email, f"Reminder — Tomorrow with {doctor_name}", body)
    return ok


# ══════════════════════════════════════════════
#  REMINDER THREAD
# ══════════════════════════════════════════════

_reminder_started = False

def reminder_worker():
    while True:
        try:
            for appt in db_get_pending_reminders():
                ok = send_appointment_reminder(
                    appt['patient_email'], appt['patient_name'],
                    appt['doctor_name'], appt['appt_date'], appt['appt_time']
                )
                if ok: db_mark_reminder_sent(appt['id'])
        except Exception:
            pass
        time.sleep(3600)

def start_reminder_thread():
    global _reminder_started
    if not _reminder_started:
        threading.Thread(target=reminder_worker, daemon=True).start()
        _reminder_started = True


# ══════════════════════════════════════════════
#  AI FUNCTIONS
# ══════════════════════════════════════════════

def get_groq_client():
    key = os.getenv("GROQ_API_KEY","").strip()
    return Groq(api_key=key) if key else None

def ai_suggest_doctors(symptoms):
    doctors = db_get_all_doctors()
    if not doctors: return "No doctors registered yet.", []
    try:
        client = get_groq_client()
        if not client: return "AI unavailable (no GROQ_API_KEY).", []
        doc_list = "\n".join([
            f"- {d['name']} | {d['specialization']} | {d['city']} | Rating:{d['rating']} | "
            f"{d['consultation_type']} | {'Available' if d['available'] else 'Busy'}"
            for d in doctors
        ])
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":
                f"Patient symptoms: {symptoms}\n\nDoctors:\n{doc_list}\n\n"
                f"Suggest top 3 most suitable doctors. Prefer available. "
                f"Give 1 line reason each. "
                f"End with: SUGGESTED_NAMES: <comma separated exact names>"}],
            max_tokens=500
        )
        text = res.choices[0].message.content
        matched = []
        for line in text.split("\n"):
            if line.strip().startswith("SUGGESTED_NAMES:"):
                matched = [n.strip() for n in line.split(":",1)[1].split(",") if n.strip()]
                break
        if not matched:
            matched = [d['name'] for d in doctors if d['name'] in text]
        display = "\n".join(l for l in text.split("\n") if not l.strip().startswith("SUGGESTED_NAMES:"))
        return display.strip(), matched
    except Exception as e:
        return f"AI error: {e}", []

def ai_suggest_timeslot(doctor_name, appt_date):
    taken = db_get_doctor_slots(doctor_name, appt_date)
    all_slots = ["09:00","09:30","10:00","10:30","11:00","11:30",
                 "14:00","14:30","15:00","15:30","16:00","16:30"]
    free = [s for s in all_slots if s not in taken]
    if not free: return None, "No slots available on this date."
    wait = len(taken) * 30
    return free[0], f"Earliest available: **{free[0]}** · Also free: {', '.join(free[1:4])} · Est. wait: ~{wait} min"

def ai_chatbot(doctor_name, user_msg, chat_history):
    try:
        client = get_groq_client()
        if not client: return "AI unavailable. Please call the doctor directly."
        msgs = [{"role":"system","content":(
            f"You are an AI assistant for {doctor_name}'s clinic in Pakistan. "
            "Doctor is unavailable. Collect: full name, contact number, medical problem. "
            "Ask for each if not provided. Once collected, confirm and say doctor will contact them soon. "
            "Give first-aid only if urgent. Never prescribe medication. "
            "Keep replies under 4 sentences. Be warm and professional. "
            "When you have all 3 details, append at the END: "
            "[COLLECTED: name=<name>, contact=<contact>, problem=<problem>]"
        )}]
        for m in chat_history: msgs.append(m)
        msgs.append({"role":"user","content":user_msg})
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, max_tokens=400)
        return res.choices[0].message.content
    except Exception as e:
        return f"AI error: {e}. Please call the doctor directly."

def extract_collected_data(reply):
    m = re.search(r'\[COLLECTED: name=(.+?), contact=(.+?), problem=(.+?)\]', reply)
    return (m.group(1).strip(), m.group(2).strip(), m.group(3).strip()) if m else (None, None, None)

def clean_reply_text(reply):
    return re.sub(r'\[COLLECTED:.*?\]', '', reply).strip()


# ══════════════════════════════════════════════
#  PROFILE PICTURE HELPERS
# ══════════════════════════════════════════════

def save_profile_pic(uploaded_file, doctor_name):
    ext  = Path(uploaded_file.name).suffix.lower()
    safe = re.sub(r'[^a-zA-Z0-9]','_', doctor_name)
    path = UPLOAD_DIR / f"{safe}{ext}"
    with open(path,"wb") as f: f.write(uploaded_file.getbuffer())
    return str(path)

def show_profile_pic(pic_path, size=80):
    if pic_path and Path(pic_path).exists():
        st.image(pic_path, width=size)
    else:
        st.markdown(
            f"<div class='profile-avatar-wrap' style='width:{size}px;height:{size}px'>"
            f"<span style='font-size:{int(size*0.4)}px'>👨‍⚕️</span></div>",
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════

def init_state():
    defaults = {
        "page":"Find Doctor","logged_in":False,"user":None,
        "selected_doctor":None,"chat_history":[],"chat_display":[],
        "chat_doctor":None,"chat_patient_name":"","chat_patient_contact":"",
        "ai_suggested_doctors":[],"search_results":[],"ai_suggestion_text":"",
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v


# ══════════════════════════════════════════════
#  PAGE: AUTH
# ══════════════════════════════════════════════

def page_auth():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-hero">
        <div class="auth-logo">🏥</div>
        <div class="auth-title">Smart Doctor Connect AI</div>
        <div class="auth-sub">Pakistan's premier AI-powered healthcare discovery platform</div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐  Login", "📝  Register"])

        with tab1:
            with st.form("login_form"):
                st.markdown("#### Welcome back")
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                st.markdown("""
                <div class="demo-hint">
                    <strong>Demo accounts</strong><br>
                    Doctor: <strong>dr_ahmed</strong> / <strong>doctor123</strong><br>
                    Patient: <strong>patient1</strong> / <strong>patient123</strong>
                </div>""", unsafe_allow_html=True)
                if st.form_submit_button("🔐  Login", type="primary", use_container_width=True):
                    user = db_login(username.strip(), password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.page = "Find Doctor"
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

        with tab2:
            with st.form("register_form"):
                st.markdown("#### Create your account")
                r_name  = st.text_input("Full Name *")
                r_uname = st.text_input("Username *", placeholder="lowercase, no spaces")
                r_pass  = st.text_input("Password *", type="password", placeholder="Min. 6 characters")
                r_role  = st.selectbox("I am a", ["patient","doctor"])
                if st.form_submit_button("✅  Create Account", type="primary", use_container_width=True):
                    if not r_name.strip() or not r_uname.strip() or not r_pass.strip():
                        st.error("All fields are required.")
                    elif len(r_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        ok, msg = db_register_user(r_uname.strip().lower(), r_pass, r_role, r_name.strip())
                        if ok:
                            st.success("✅ Account created! Please login.")
                        else:
                            st.error(f"❌ {msg}")

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  SHARED: DOCTOR CARD
# ══════════════════════════════════════════════

def render_doctor_card(doc, key_prefix=""):
    avail_html = (
        '<span class="doc-badge">🟢 Available</span>' if doc['available']
        else '<span class="doc-badge doc-badge-busy">🔴 Busy</span>'
    )
    st.markdown(f"""
    <div class="doc-card">
        <p class="doc-name">{doc['name']}</p>
        <p class="doc-spec">{doc['specialization']}</p>
        <div style="margin: 8px 0 10px; flex-wrap: wrap;">
            <span class="info-chip">📍 {doc['city']}</span>
            <span class="info-chip">💻 {doc['consultation_type']}</span>
            <span class="info-chip">⭐ {doc['rating']}</span>
            <span class="info-chip">🩺 {doc['experience']} yrs</span>
            <span class="info-chip">📞 {doc['contact']}</span>
        </div>
        {avail_html}
    </div>
    """, unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("📅 Book Appointment", key=f"{key_prefix}book_{doc['id']}", use_container_width=True):
            st.session_state.selected_doctor = doc
            st.session_state.page = "Appointments"
            st.rerun()
    with b2:
        if st.button("💬 Chat with AI", key=f"{key_prefix}chat_{doc['id']}", use_container_width=True):
            st.session_state.selected_doctor = doc
            st.session_state.chat_doctor = doc['name']
            st.session_state.chat_history = []
            st.session_state.chat_display = []
            st.session_state.page = "Chat"
            st.rerun()


# ══════════════════════════════════════════════
#  PAGE: FIND DOCTOR
# ══════════════════════════════════════════════

def page_find_doctor():
    user = st.session_state.user
    st.markdown(f"""
    <div class="page-hero">
        <span class="page-hero-icon">🔍</span>
        <h2>Find a Doctor</h2>
        <p>Welcome back, <strong style="color: var(--teal);">{user['display_name']}</strong> · Search by city, specialization, or describe your symptoms for AI-powered recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            city = st.text_input("📍 City", placeholder="e.g. Lahore, Karachi, Islamabad")
        with c2:
            spec = st.text_input("🏥 Specialization", placeholder="e.g. Cardiologist, Dermatologist")
        symptoms = st.text_input(
            "🤖 AI Symptom Search",
            placeholder="Describe symptoms — e.g. chest pain, skin rash, back pain, fever"
        )
        b1, b2 = st.columns(2)
        with b1:
            search_clicked = st.button("🔍 Search Doctors", type="primary", use_container_width=True)
        with b2:
            show_all = st.button("📋 View All Doctors", use_container_width=True)

    if search_clicked or show_all:
        st.session_state.ai_suggestion_text   = ""
        st.session_state.ai_suggested_doctors = []
        if show_all:
            st.session_state.search_results = db_get_all_doctors()
        elif symptoms.strip() and not city.strip() and not spec.strip():
            with st.spinner("🤖 AI analyzing your symptoms..."):
                txt, names = ai_suggest_doctors(symptoms)
            st.session_state.ai_suggestion_text   = txt
            st.session_state.ai_suggested_doctors = names
            all_docs = db_get_all_doctors()
            st.session_state.search_results = [d for d in all_docs if d['name'] in names] or all_docs
        else:
            st.session_state.search_results = db_search_doctors(city, spec)

    if st.session_state.ai_suggestion_text:
        st.markdown(f"""
        <div class="ai-box">
            <p class="ai-box-label">🤖 AI Recommendation</p>
            <p style="white-space:pre-wrap;">{st.session_state.ai_suggestion_text}</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.search_results:
        label = "🤖 AI-Recommended Doctors" if st.session_state.ai_suggested_doctors else f"Results — {len(st.session_state.search_results)} doctor(s) found"
        st.markdown(f"### {label}")
        for doc in st.session_state.search_results:
            render_doctor_card(doc, key_prefix="find_")
    elif search_clicked or show_all:
        st.warning("No doctors found. Try different filters.")


# ══════════════════════════════════════════════
#  PAGE: APPOINTMENTS
# ══════════════════════════════════════════════

def _render_appointment_list(appts, show_manage=False):
    if not appts:
        st.info("No appointments found.")
        return
    status_filter = st.selectbox("Filter by status", ["All","Pending","Confirmed","Cancelled"], key="af")
    filtered = appts if status_filter == "All" else [a for a in appts if a['status'] == status_filter]
    st.caption(f"{len(filtered)} appointment(s)")
    for a in filtered:
        icon  = {"Pending":"🟡","Confirmed":"🟢","Cancelled":"🔴"}.get(a['status'],"⚪")
        status_cls = {"Pending":"status-pending","Confirmed":"status-confirm","Cancelled":"status-cancel"}.get(a['status'],"")
        email_info = f" &nbsp;·&nbsp; 📧 {a['patient_email']}" if a.get('patient_email') else ""
        reminder_badge = "<span style='color:var(--teal);font-size:0.75rem;'>📧 Reminder sent</span>" if a.get('reminder_sent') else ""

        st.markdown(f"""
        <div class="appt-row">
            <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;align-items:flex-start;">
                <div>
                    <p style="margin:0;font-weight:700;font-size:1rem;color:var(--text-primary);">{a['patient_name']}</p>
                    <p style="margin:2px 0 0;color:var(--text-secondary);font-size:0.82rem;">📞 {a['patient_contact']}{email_info}</p>
                </div>
                <div>
                    <p style="margin:0;color:var(--text-secondary);font-size:0.85rem;">👨‍⚕️ {a['doctor_name']}</p>
                    <p style="margin:2px 0 0;color:var(--text-secondary);font-size:0.82rem;">📅 {a['appt_date']} &nbsp;·&nbsp; {a['appt_time']}</p>
                </div>
                <div style="text-align:right;">
                    <p class="{status_cls}" style="margin:0;font-size:0.9rem;">{icon} {a['status']}</p>
                    <p style="margin:2px 0 0;color:var(--text-secondary);font-size:0.80rem;">📝 {a.get('problem') or 'No details'}</p>
                    {reminder_badge}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if show_manage and a['status'] in ('Pending','Confirmed'):
            cb1, cb2 = st.columns(2)
            with cb1:
                if a['status'] == 'Pending':
                    if st.button("✅ Confirm", key=f"c_{a['id']}", use_container_width=True):
                        db_update_appointment_status(a['id'], 'Confirmed'); st.rerun()
            with cb2:
                if st.button("❌ Cancel", key=f"x_{a['id']}", use_container_width=True):
                    db_update_appointment_status(a['id'], 'Cancelled'); st.rerun()


def page_appointments():
    user = st.session_state.user
    st.markdown("""
    <div class="page-hero">
        <span class="page-hero-icon">📅</span>
        <h2>Appointments</h2>
        <p>Book a new appointment or manage your existing schedule</p>
    </div>
    """, unsafe_allow_html=True)

    all_docs = db_get_all_doctors()
    if not all_docs:
        st.warning("No doctors registered yet."); return

    if user['role'] == 'doctor':
        my_doc = db_get_doctor_by_username(user['username'])
        if my_doc:
            st.info(f"👨‍⚕️ Managing appointments for **{my_doc['name']}**")
            _render_appointment_list(db_get_appointments(doctor_name=my_doc['name']), show_manage=True)
            return
        else:
            st.warning("Register your doctor profile first.")

    doc_names   = [d["name"] for d in all_docs]
    pre         = st.session_state.selected_doctor
    default_idx = 0
    if pre and isinstance(pre, dict):
        try: default_idx = doc_names.index(pre["name"])
        except: pass
        with st.container(border=True):
            st.success(f"📌 Booking with: **{pre['name']}** — {pre['specialization']}, {pre['city']}")

    with st.form("appt_form", clear_on_submit=True):
        st.markdown("#### Patient Information")
        c1, c2 = st.columns(2)
        with c1:
            p_name    = st.text_input("Full Name *", value=user.get('display_name',''))
            p_contact = st.text_input("Phone Number *", placeholder="03XXXXXXXXX")
            p_email   = st.text_input("Email (for reminder)", placeholder="Optional")
        with c2:
            sel_doc   = st.selectbox("Select Doctor *", doc_names, index=default_idx)
            appt_date = st.date_input("Appointment Date *", min_value=date.today())

        _, slot_msg = ai_suggest_timeslot(sel_doc, appt_date)
        st.markdown(f"""
        <div class="ai-box">
            <p class="ai-box-label">🤖 AI Slot Suggestion</p>
            <p>{slot_msg}</p>
        </div>
        """, unsafe_allow_html=True)

        slots = ["09:00","09:30","10:00","10:30","11:00","11:30",
                 "14:00","14:30","15:00","15:30","16:00","16:30"]
        taken = db_get_doctor_slots(sel_doc, appt_date)
        free  = [s for s in slots if s not in taken]

        if free:
            appt_time = st.selectbox("Time Slot *", free, help="Only free slots shown")
        else:
            st.error("No slots available. Choose another date."); appt_time = None

        problem = st.text_area("Describe your problem / symptoms", placeholder="Please provide as much detail as possible")

        if st.form_submit_button("✅  Confirm Appointment", type="primary", use_container_width=True):
            if not p_name.strip() or not p_contact.strip():
                st.error("Name and phone are required.")
            elif not appt_time:
                st.error("Select a valid date with free slots.")
            else:
                ok = db_book_appointment(p_name, p_contact, p_email, sel_doc, appt_date, appt_time, problem)
                if not ok:
                    st.error("❌ Slot just taken. Please refresh.")
                else:
                    st.success(f"✅ Booked with **{sel_doc}** on {appt_date} at {appt_time}!")
                    doc_obj   = next((d for d in all_docs if d["name"] == sel_doc), None)
                    doc_email = doc_obj.get("email","") if doc_obj else ""
                    if doc_email:
                        sent = notify_doctor_appointment(sel_doc, doc_email, p_name, p_contact, appt_date, appt_time, problem)
                        if sent:
                            st.success("📧 Doctor notified by email!")
                        else:
                            st.warning("⚠️ Email failed. Check .env")
                    if p_email.strip():
                        st.info("⏰ Reminder email will be sent automatically 1 day before your appointment.")
                    st.session_state.selected_doctor = None

    st.divider()
    st.markdown("### 📋 My Appointments")
    _render_appointment_list(db_get_appointments(patient_name=user.get('display_name','')), show_manage=False)


# ══════════════════════════════════════════════
#  PAGE: CHAT
# ══════════════════════════════════════════════

def page_chat():
    st.markdown("""
    <div class="page-hero">
        <span class="page-hero-icon">💬</span>
        <h2>Chat with Doctor's AI Assistant</h2>
        <p>Our AI collects your details and notifies the doctor instantly when unavailable</p>
    </div>
    """, unsafe_allow_html=True)

    all_docs = db_get_all_doctors()
    if not all_docs:
        st.warning("No doctors registered."); return

    doc_names   = [d["name"] for d in all_docs]
    pre         = st.session_state.selected_doctor
    default_idx = 0
    if pre and isinstance(pre, dict):
        try: default_idx = doc_names.index(pre["name"])
        except: pass

    sel = st.selectbox("Select Doctor", doc_names, index=default_idx)
    doc = next((d for d in all_docs if d["name"] == sel), None)

    if doc:
        avail_cls   = "" if doc['available'] else "doc-badge-busy"
        avail_badge = "🟢 Available for direct booking" if doc['available'] else "🔴 Busy — AI assistant active"
        st.markdown(f"""
        <div class="doc-card">
            <p class="doc-name">{doc['name']}</p>
            <p class="doc-spec">{doc['specialization']}</p>
            <div style="margin:8px 0 10px;">
                <span class="info-chip">📍 {doc['city']}</span>
                <span class="info-chip">💻 {doc['consultation_type']}</span>
                <span class="info-chip">📞 {doc['contact']}</span>
            </div>
            <span class="doc-badge {avail_cls}">{avail_badge}</span>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.chat_doctor != sel:
        st.session_state.chat_history        = []
        st.session_state.chat_display        = []
        st.session_state.chat_doctor         = sel
        st.session_state.chat_patient_name   = ""
        st.session_state.chat_patient_contact= ""

    for msg in st.session_state.chat_display:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Type your message…")
    if user_input:
        st.session_state.chat_display.append({"role":"user","content":user_input})
        st.session_state.chat_history.append({"role":"user","content":user_input})
        with st.spinner("🤖 AI typing…"):
            raw = ai_chatbot(sel, user_input, st.session_state.chat_history[:-1])
        p_name, p_contact, p_problem = extract_collected_data(raw)
        clean = clean_reply_text(raw)
        st.session_state.chat_display.append({"role":"assistant","content":clean})
        st.session_state.chat_history.append({"role":"assistant","content":clean})

        if p_name and p_contact:
            st.session_state.chat_patient_name    = p_name
            st.session_state.chat_patient_contact = p_contact
            db_save_message(sel, p_name, p_contact, p_problem or user_input)
            if doc and not doc['available'] and doc.get("email"):
                notify_doctor_message(sel, doc.get("email",""), p_name, p_contact, p_problem or user_input)
        else:
            db_save_message(sel, st.session_state.chat_patient_name or "Unknown",
                            st.session_state.chat_patient_contact or "", user_input)
            if doc and not doc['available'] and doc.get("email"):
                notify_doctor_message(sel, doc.get("email",""),
                                      st.session_state.chat_patient_name or "Unknown",
                                      st.session_state.chat_patient_contact or "", user_input)
        st.rerun()

    if doc and doc['available'] and st.session_state.chat_display:
        st.divider()
        if st.button("📅 Book Appointment with this Doctor", type="primary", use_container_width=True):
            st.session_state.selected_doctor = doc
            st.session_state.page = "Appointments"
            st.rerun()

    if st.session_state.chat_display:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_display        = []
            st.session_state.chat_history        = []
            st.session_state.chat_patient_name   = ""
            st.session_state.chat_patient_contact= ""
            st.rerun()


# ══════════════════════════════════════════════
#  PAGE: REGISTER DOCTOR
# ══════════════════════════════════════════════

def page_register_doctor():
    user = st.session_state.user
    st.markdown("""
    <div class="page-hero">
        <span class="page-hero-icon">👨‍⚕️</span>
        <h2>Doctor Profile Management</h2>
        <p>Register your medical profile to become discoverable to patients nationwide</p>
    </div>
    """, unsafe_allow_html=True)

    if user['role'] == 'doctor':
        my_doc = db_get_doctor_by_username(user['username'])
        if my_doc:
            st.success(f"✅ Your profile is live — **{my_doc['name']}**")
            with st.container(border=True):
                st.markdown("### 🖼️ Update Profile Picture")
                cp, cu = st.columns([1, 3])
                with cp:
                    show_profile_pic(my_doc.get("profile_pic",""), 100)
                with cu:
                    up = st.file_uploader("Upload new photo", type=["jpg","jpeg","png"], key="pp_up")
                    if up:
                        path = save_profile_pic(up, my_doc['name'])
                        db_update_doctor_pic(my_doc['id'], path)
                        st.success("✅ Picture updated!"); st.rerun()
            st.divider()

    st.markdown("### 📋 Register New Profile")
    with st.form("doc_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name    = st.text_input("Full Name (with Dr.) *", value=user.get('display_name','') if user['role']=='doctor' else "")
            spec    = st.text_input("Specialization *", placeholder="e.g. Cardiologist")
            city    = st.text_input("City *", placeholder="e.g. Lahore")
        with c2:
            ctype   = st.selectbox("Consultation Type", ["Online","Physical","Both"])
            exp     = st.number_input("Years of Experience", 0, 60, 1)
            contact = st.text_input("Contact Number *", placeholder="03XXXXXXXXX")
        email   = st.text_input("Email (for notifications)", value="fsohail985@gmail.com")
        rating  = st.slider("Initial Rating", 1.0, 5.0, 4.0, 0.1)
        pic_file= st.file_uploader("Profile Picture", type=["jpg","jpeg","png"])

        if st.form_submit_button("✅  Register Profile", type="primary", use_container_width=True):
            if not name.strip() or not spec.strip() or not city.strip() or not contact.strip():
                st.error("All starred fields are required.")
            else:
                pic_path = save_profile_pic(pic_file, name) if pic_file else ""
                db_add_doctor(name, spec, city, ctype, exp, contact, rating, email, pic_path, user['username'])
                st.success(f"✅ {name} registered and discoverable nationwide!")

    st.divider()
    doctors = db_get_all_doctors()
    if doctors:
        st.markdown(f"### All Registered Doctors ({len(doctors)})")
        for d in doctors:
            with st.container(border=True):
                cp, c1, c2, c3 = st.columns([1, 3, 2, 1])
                with cp:
                    show_profile_pic(d.get("profile_pic",""), 60)
                with c1:
                    st.markdown(f"**{d['name']}** — {d['specialization']}")
                    st.markdown(f"📍 {d['city']} · 💻 {d['consultation_type']}")
                    st.caption(f"📧 {d.get('email') or 'No email'}")
                with c2:
                    st.markdown(f"⭐ {d['rating']} · 🩺 {d['experience']} yrs · 📞 {d['contact']}")
                    appts = db_get_appointments(d['name'])
                    p  = sum(1 for a in appts if a['status']=='Pending')
                    cf = sum(1 for a in appts if a['status']=='Confirmed')
                    st.caption(f"🟡 {p} pending · 🟢 {cf} confirmed")
                with c3:
                    can_edit = (user['role']=='doctor' and d.get('username')==user['username'])
                    if can_edit:
                        lbl = "Set Busy" if d['available'] else "Set Available"
                        if st.button(lbl, key=f"tog_{d['id']}"):
                            db_toggle_availability(d['id'], 0 if d['available'] else 1); st.rerun()
                    else:
                        st.markdown("🟢 Available" if d['available'] else "🔴 Busy")
                    if st.button("📋", key=f"va_{d['id']}", help="View appointments"):
                        k = f"sa_{d['id']}"
                        st.session_state[k] = not st.session_state.get(k, False); st.rerun()

                if st.session_state.get(f"sa_{d['id']}", False):
                    for a in db_get_appointments(d['name']):
                        icon = {"Pending":"🟡","Confirmed":"🟢","Cancelled":"🔴"}.get(a['status'],"⚪")
                        st.markdown(
                            f"  {icon} **{a['patient_name']}** | "
                            f"{a['appt_date']} {a['appt_time']} | "
                            f"{a.get('problem') or 'N/A'}"
                        )


# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════

def main():
    st.set_page_config(page_title="Smart Doctor Connect AI", page_icon="🏥", layout="wide")
    init_db(); init_state(); start_reminder_thread()

    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    if not st.session_state.logged_in:
        page_auth(); return

    user = st.session_state.user

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <span class="brand-icon">🏥</span>
            <p class="brand-title">Smart Doctor<br>Connect AI</p>
            <span class="brand-sub">AI-Powered · Pakistan</span>
        </div>
        """, unsafe_allow_html=True)

        role_icon = "👨‍⚕️" if user['role'] == 'doctor' else "🧑"
        st.markdown(f"""
        <div class="user-badge">
            <div class="user-avatar">{role_icon}</div>
            <div>
                <div class="user-name">{user['display_name']}</div>
                <div class="user-role">{user['role']} · @{user['username']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

        st.divider()

        pages   = ["Find Doctor","Appointments","Chat","Register Doctor"]
        icons   = ["🔍","📅","💬","👨‍⚕️"]
        current = st.session_state.page if st.session_state.page in pages else "Find Doctor"
        selected = st.radio(
            "Navigate", pages,
            format_func=lambda x: f"{icons[pages.index(x)]}  {x}",
            index=pages.index(current)
        )
        if selected != st.session_state.page:
            st.session_state.page = selected; st.rerun()

        st.divider()
        st.markdown("### 📊 Live Stats")
        dc, ac, mc = db_get_stats()
        col1, col2 = st.columns(2)
        col1.metric("Doctors", dc)
        col2.metric("Appts", ac)
        st.metric("Messages", mc)

        st.divider()
        st.markdown("### 🔧 Tools")
        if st.button("📧 Send Test Email", use_container_width=True):
            ok, reason = send_email(
                os.getenv("GMAIL_ADDRESS",""),
                "Smart Doctor Connect — Test ✅",
                "Email working!\n\nSent from Smart Doctor Connect AI."
            )
            if ok:
                st.success("✅ Test email sent!")
            else:
                st.error(f"❌ {reason}")

        st.divider()
        st.markdown("### ⏰ Reminders")
        pending = db_get_pending_reminders()
        if pending:
            st.warning(f"📬 {len(pending)} reminder(s) for tomorrow")
            if st.button("📤 Send Now", use_container_width=True):
                sent = 0
                for a in pending:
                    if send_appointment_reminder(a['patient_email'], a['patient_name'],
                                                  a['doctor_name'], a['appt_date'], a['appt_time']):
                        db_mark_reminder_sent(a['id']); sent += 1
                st.success(f"✅ {sent} reminder(s) sent!"); st.rerun()
        else:
            st.success("✅ No pending reminders")

    page = st.session_state.page
    if   page == "Find Doctor":      page_find_doctor()
    elif page == "Appointments":     page_appointments()
    elif page == "Chat":             page_chat()
    elif page == "Register Doctor":  page_register_doctor()

if __name__ == "__main__":
    main()