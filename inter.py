"""
SentimentPro - Enterprise Sentiment Analysis Platform
Professional interface for comment extraction and analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
from pathlib import Path
import io
import base64
from typing import List, Dict
import google.generativeai as genai
from transformers import pipeline, CamembertTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv
import time

# Load environment
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Page configuration
st.set_page_config(
    page_title="SentimentPro | Analyse de Sentiment Intelligente",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enterprise Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #0066FF;
        --primary-dark: #0052CC;
        --primary-light: #E6F0FF;
        --secondary: #6554C0;
        --success: #00875A;
        --success-light: #E3FCEF;
        --warning: #FF8B00;
        --warning-light: #FFFAE6;
        --danger: #DE350B;
        --danger-light: #FFEBE6;
        --neutral-900: #091E42;
        --neutral-800: #172B4D;
        --neutral-700: #253858;
        --neutral-600: #344563;
        --neutral-500: #5E6C84;
        --neutral-400: #8993A4;
        --neutral-300: #C1C7D0;
        --neutral-200: #DFE1E6;
        --neutral-100: #EBECF0;
        --neutral-50: #F4F5F7;
        --neutral-25: #FAFBFC;
        --white: #FFFFFF;
        --shadow-sm: 0 1px 2px 0 rgba(9, 30, 66, 0.08);
        --shadow-md: 0 4px 8px -2px rgba(9, 30, 66, 0.08), 0 0 1px rgba(9, 30, 66, 0.08);
        --shadow-lg: 0 8px 16px -4px rgba(9, 30, 66, 0.08), 0 0 1px rgba(9, 30, 66, 0.12);
        --shadow-xl: 0 16px 32px -8px rgba(9, 30, 66, 0.12), 0 0 1px rgba(9, 30, 66, 0.12);
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
    }
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: var(--neutral-25);
    }
    
    /* Hide Streamlit Elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}
    
    /* ===== NAVIGATION BAR ===== */
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 64px;
        background: var(--white);
        border-bottom: 1px solid var(--neutral-200);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 32px;
        z-index: 1000;
        box-shadow: var(--shadow-sm);
    }
    
    .navbar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .navbar-logo {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
        font-size: 18px;
    }
    
    .navbar-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--neutral-900);
        letter-spacing: -0.02em;
    }
    
    .navbar-subtitle {
        font-size: 12px;
        color: var(--neutral-500);
        font-weight: 500;
    }
    
    .navbar-actions {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    .navbar-status {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: var(--success-light);
        border-radius: var(--radius-md);
        font-size: 13px;
        font-weight: 600;
        color: var(--success);
    }
    
    .navbar-status-dot {
        width: 8px;
        height: 8px;
        background: var(--success);
        border-radius: 50%;
        animation: pulse-dot 2s infinite;
    }
    
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
    }
    
    /* ===== MAIN CONTAINER ===== */
    .main-container {
        margin-top: 80px;
        padding: 0 32px 32px;
        max-width: 1400px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* ===== PAGE HEADER ===== */
    .page-header {
        margin-bottom: 32px;
    }
    
    .page-title {
        font-size: 28px;
        font-weight: 800;
        color: var(--neutral-900);
        letter-spacing: -0.02em;
        margin-bottom: 8px;
    }
    
    .page-description {
        font-size: 15px;
        color: var(--neutral-500);
        line-height: 1.5;
    }
    
    /* ===== METRICS GRID ===== */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 32px;
    }
    
    .metric-card {
        background: var(--white);
        border-radius: var(--radius-lg);
        padding: 24px;
        border: 1px solid var(--neutral-200);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
    }
    
    .metric-card.total::before { background: var(--primary); }
    .metric-card.positive::before { background: var(--success); }
    .metric-card.negative::before { background: var(--danger); }
    .metric-card.neutral::before { background: var(--warning); }
    
    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
    }
    
    .metric-icon {
        width: 44px;
        height: 44px;
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    
    .metric-icon.total { background: var(--primary-light); }
    .metric-icon.positive { background: var(--success-light); }
    .metric-icon.negative { background: var(--danger-light); }
    .metric-icon.neutral { background: var(--warning-light); }
    
    .metric-trend {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: var(--radius-sm);
    }
    
    .metric-trend.up {
        color: var(--success);
        background: var(--success-light);
    }
    
    .metric-trend.down {
        color: var(--danger);
        background: var(--danger-light);
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: 800;
        color: var(--neutral-900);
        line-height: 1;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }
    
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: var(--neutral-500);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* ===== TABS ===== */
    .stTabs {
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: var(--white);
        padding: 4px;
        border-radius: var(--radius-lg);
        border: 1px solid var(--neutral-200);
        box-shadow: var(--shadow-sm);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md);
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        color: var(--neutral-600);
        background: transparent;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--neutral-900);
        background: var(--neutral-50);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: var(--white) !important;
        box-shadow: var(--shadow-md);
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    
    /* ===== CARDS ===== */
    .card {
        background: var(--white);
        border-radius: var(--radius-lg);
        border: 1px solid var(--neutral-200);
        box-shadow: var(--shadow-sm);
        overflow: hidden;
    }
    
    .card-header {
        padding: 20px 24px;
        border-bottom: 1px solid var(--neutral-100);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .card-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--neutral-900);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .card-title-icon {
        width: 32px;
        height: 32px;
        border-radius: var(--radius-md);
        background: var(--primary-light);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
    }
    
    .card-body {
        padding: 24px;
    }
    
    .card-footer {
        padding: 16px 24px;
        border-top: 1px solid var(--neutral-100);
        background: var(--neutral-25);
    }
    
    /* ===== UPLOAD ZONE ===== */
    .upload-zone {
        border: 2px dashed var(--neutral-300);
        border-radius: var(--radius-lg);
        padding: 48px;
        text-align: center;
        background: var(--neutral-25);
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .upload-zone:hover {
        border-color: var(--primary);
        background: var(--primary-light);
    }
    
    .upload-icon {
        width: 72px;
        height: 72px;
        background: var(--white);
        border-radius: var(--radius-xl);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 24px;
        font-size: 32px;
        box-shadow: var(--shadow-md);
    }
    
    .upload-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--neutral-900);
        margin-bottom: 8px;
    }
    
    .upload-subtitle {
        font-size: 14px;
        color: var(--neutral-500);
        margin-bottom: 24px;
    }
    
    .upload-formats {
        display: flex;
        justify-content: center;
        gap: 12px;
    }
    
    .upload-format-badge {
        padding: 6px 12px;
        background: var(--white);
        border: 1px solid var(--neutral-200);
        border-radius: var(--radius-md);
        font-size: 12px;
        font-weight: 600;
        color: var(--neutral-600);
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: var(--primary);
        color: var(--white);
        border: none;
        border-radius: var(--radius-md);
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: var(--primary-dark);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .btn-secondary > button {
        background: var(--white) !important;
        color: var(--neutral-700) !important;
        border: 1px solid var(--neutral-200) !important;
    }
    
    .btn-secondary > button:hover {
        background: var(--neutral-50) !important;
        border-color: var(--neutral-300) !important;
    }
    
    .btn-success > button {
        background: var(--success) !important;
    }
    
    .btn-success > button:hover {
        background: #006644 !important;
    }
    
    .btn-danger > button {
        background: var(--danger) !important;
    }
    
    .btn-danger > button:hover {
        background: #BF2600 !important;
    }
    
    /* ===== BADGES ===== */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: var(--radius-md);
        font-size: 12px;
        font-weight: 600;
    }
    
    .badge-positive {
        background: var(--success-light);
        color: var(--success);
    }
    
    .badge-negative {
        background: var(--danger-light);
        color: var(--danger);
    }
    
    .badge-neutral {
        background: var(--warning-light);
        color: var(--warning);
    }
    
    .badge-primary {
        background: var(--primary-light);
        color: var(--primary);
    }
    
    .badge-secondary {
        background: var(--neutral-100);
        color: var(--neutral-600);
    }
    
    /* ===== COMMENT CARDS ===== */
    .comment-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .comment-card {
        background: var(--white);
        border-radius: var(--radius-lg);
        border: 1px solid var(--neutral-200);
        padding: 20px;
        transition: all 0.2s ease;
    }
    
    .comment-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--neutral-300);
    }
    
    .comment-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .comment-meta {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .comment-confidence {
        text-align: right;
    }
    
    .comment-confidence-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--neutral-400);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .comment-confidence-value {
        font-size: 18px;
        font-weight: 800;
        color: var(--neutral-900);
    }
    
    .comment-text {
        font-size: 15px;
        line-height: 1.7;
        color: var(--neutral-700);
        margin-bottom: 16px;
    }
    
    .comment-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding-top: 16px;
        border-top: 1px solid var(--neutral-100);
    }
    
    /* ===== PROGRESS ===== */
    .progress-container {
        background: var(--white);
        border-radius: var(--radius-lg);
        border: 1px solid var(--neutral-200);
        padding: 48px;
        text-align: center;
    }
    
    .progress-spinner {
        width: 64px;
        height: 64px;
        border: 4px solid var(--neutral-200);
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 24px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .progress-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--neutral-900);
        margin-bottom: 8px;
    }
    
    .progress-subtitle {
        font-size: 14px;
        color: var(--neutral-500);
        margin-bottom: 32px;
    }
    
    .progress-steps {
        display: flex;
        justify-content: center;
        gap: 48px;
        margin-top: 32px;
    }
    
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
    }
    
    .progress-step-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        transition: all 0.3s ease;
    }
    
    .progress-step-icon.completed {
        background: var(--success-light);
        color: var(--success);
    }
    
    .progress-step-icon.active {
        background: var(--primary-light);
        color: var(--primary);
        animation: pulse 2s infinite;
    }
    
    .progress-step-icon.pending {
        background: var(--neutral-100);
        color: var(--neutral-400);
    }
    
    .progress-step-label {
        font-size: 13px;
        font-weight: 600;
        color: var(--neutral-500);
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 102, 255, 0.4); }
        50% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(0, 102, 255, 0); }
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: var(--radius-md);
    }
    
    /* ===== FILTERS ===== */
    .filters-container {
        background: var(--white);
        border-radius: var(--radius-lg);
        border: 1px solid var(--neutral-200);
        padding: 16px 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
    }
    
    .filter-group {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .filter-label {
        font-size: 13px;
        font-weight: 600;
        color: var(--neutral-500);
    }
    
    .stSelectbox > div > div {
        border-radius: var(--radius-md) !important;
        border-color: var(--neutral-200) !important;
        font-size: 14px;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1) !important;
    }
    
    .stTextInput > div > div > input {
        border-radius: var(--radius-md) !important;
        border-color: var(--neutral-200) !important;
        font-size: 14px;
        padding: 10px 14px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1) !important;
    }
    
    /* ===== DATA TABLE ===== */
    .stDataFrame {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--neutral-200) !important;
        overflow: hidden;
    }
    
    .stDataFrame thead tr th {
        background: var(--neutral-50) !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: var(--neutral-600) !important;
        padding: 14px 16px !important;
        border-bottom: 1px solid var(--neutral-200) !important;
    }
    
    .stDataFrame tbody tr td {
        padding: 14px 16px !important;
        font-size: 14px !important;
        color: var(--neutral-700) !important;
    }
    
    .stDataFrame tbody tr:hover {
        background: var(--neutral-25) !important;
    }
    
    /* ===== CHARTS ===== */
    .chart-card {
        background: var(--white);
        border-radius: var(--radius-lg);
        border: 1px solid var(--neutral-200);
        padding: 24px;
        box-shadow: var(--shadow-sm);
    }
    
    .chart-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--neutral-900);
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* ===== EMPTY STATE ===== */
    .empty-state {
        background: var(--white);
        border-radius: var(--radius-lg);
        border: 1px solid var(--neutral-200);
        padding: 64px 48px;
        text-align: center;
    }
    
    .empty-state-icon {
        width: 80px;
        height: 80px;
        background: var(--neutral-100);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 24px;
        font-size: 36px;
    }
    
    .empty-state-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--neutral-900);
        margin-bottom: 8px;
    }
    
    .empty-state-description {
        font-size: 15px;
        color: var(--neutral-500);
        max-width: 400px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        padding: 0 !important;
    }
    
    [data-testid="stFileUploader"] > div {
        padding: 0 !important;
    }
    
    [data-testid="stFileUploader"] section {
        border: 2px dashed var(--neutral-300) !important;
        border-radius: var(--radius-lg) !important;
        padding: 40px !important;
        background: var(--neutral-25) !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stFileUploader"] section:hover {
        border-color: var(--primary) !important;
        background: var(--primary-light) !important;
    }
    
    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        background: var(--white) !important;
        color: var(--neutral-700) !important;
        border: 1px solid var(--neutral-200) !important;
        box-shadow: none !important;
    }
    
    .stDownloadButton > button:hover {
        background: var(--neutral-50) !important;
        border-color: var(--neutral-300) !important;
    }
    
    /* ===== EXPANDER ===== */
    .stExpander {
        background: var(--white);
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--neutral-200) !important;
        overflow: hidden;
    }
    
    .stExpander > div > div > div {
        padding: 16px 20px !important;
    }
    
    /* ===== SUCCESS/INFO/WARNING ALERTS ===== */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: var(--radius-md) !important;
        border: none !important;
        font-weight: 500 !important;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 1024px) {
        .metrics-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .navbar {
            padding: 0 16px;
        }
        
        .main-container {
            padding: 0 16px 16px;
        }
    }
    
    @media (max-width: 640px) {
        .metrics-grid {
            grid-template-columns: 1fr;
        }
        
        .progress-steps {
            flex-direction: column;
            gap: 24px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_results' not in st.session_state:
    st.session_state.current_results = None
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
if 'sentiment_model' not in st.session_state:
    st.session_state.sentiment_model = None

# Prompts
PROMPT_EXTRACT = """Extract all user comments from this screenshot.

Return the comments as a JSON array of strings. Just the array, nothing else.

Rules:
- Include only the actual comment text, not usernames, timestamps, or UI elements
- Each comment should be a separate string in the array
- Preserve the original text exactly as written
- If a comment spans multiple lines, keep it as one string
- Skip empty or duplicate comments
- Maintain the order of comments as they appear

Example output format:
["First comment here", "Second comment here", "Third comment here"]
"""

@st.cache_resource
def load_sentiment_model():
    """Load sentiment analysis model (cached)"""
    try:
        model_name = "cmarkea/distilcamembert-base-sentiment"
        tokenizer = CamembertTokenizer.from_pretrained(model_name, token=HF_TOKEN)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, token=HF_TOKEN)
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=-1
        )
        return sentiment_pipeline
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle: {e}")
        return None

def extract_comments_from_image(image_file):
    """Extract comments from uploaded image"""
    try:
        temp_path = f"temp_{image_file.name}"
        with open(temp_path, "wb") as f:
            f.write(image_file.getbuffer())
        
        uploaded_file = genai.upload_file(temp_path)
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={"response_mime_type": "application/json"}
        )
        
        response = model.generate_content([PROMPT_EXTRACT, uploaded_file])
        result = json.loads(response.text)
        
        os.remove(temp_path)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            return result.get("content", result.get("comments", []))
        return []
        
    except Exception as e:
        st.error(f"Erreur extraction {image_file.name}: {e}")
        return []

def analyze_sentiment(text: str, sentiment_model):
    """Analyze sentiment of text"""
    try:
        result = sentiment_model(text[:512])[0]
        label = result['label'].lower()
        score = result['score']
        
        if 'star' in label:
            if label in ['1 star', '2 stars']:
                return 'negative', score
            elif label == '3 stars':
                return 'neutral', score
            else:
                return 'positive', score
        
        if label in ['positive', 'negative', 'neutral']:
            return label, score
        
        return "neutral", score
        
    except Exception as e:
        return "neutral", 0.0

def identify_topic_theme(text: str):
    """Identify topic and theme using Gemini"""
    try:
        prompt = f"""
Analyze this comment and generate a 'topic' and 'theme'.

Comment: "{text}"

Rules:
- 'theme' = high-level category (e.g., "Qualité de service", "Problème technique")
- 'topic' = specific sub-category (e.g., "Réactivité", "Panne réseau")
- Both in French
- Return JSON with keys "topic" and "theme"

Example:
{{"topic": "Coupures fréquentes", "theme": "Problème de connexion"}}
"""
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={"response_mime_type": "application/json"}
        )
        
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        return result.get("topic", "Non défini"), result.get("theme", "Non défini")
        
    except Exception as e:
        return "Non défini", "Non défini"

def process_images(uploaded_files, sentiment_model, progress_bar, status_text, stats_container):
    """Process multiple images"""
    all_data = []
    total_files = len(uploaded_files)
    total_comments = 0
    
    for idx, file in enumerate(uploaded_files):
        status_text.markdown(f"""
            <div style="text-align: center; color: var(--neutral-500); font-size: 14px;">
                Traitement de <strong>{file.name}</strong> ({idx + 1}/{total_files})
            </div>
        """, unsafe_allow_html=True)
        
        progress_bar.progress((idx + 0.3) / total_files)
        
        comments = extract_comments_from_image(file)
        total_comments += len(comments)
        
        stats_container.markdown(f"""
            <div style="text-align: center; margin-top: 16px;">
                <span class="badge badge-primary">{total_comments} commentaires extraits</span>
            </div>
        """, unsafe_allow_html=True)
        
        progress_bar.progress((idx + 0.6) / total_files)
        
        for comment in comments:
            if len(comment.strip()) < 10:
                continue
            
            sentiment, confidence = analyze_sentiment(comment, sentiment_model)
            topic, theme = identify_topic_theme(comment)
            
            all_data.append({
                'image_source': file.name,
                'comment': comment,
                'sentiment': sentiment,
                'confidence': round(confidence, 4),
                'topic': topic,
                'theme': theme,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        progress_bar.progress((idx + 1) / total_files)
    
    return pd.DataFrame(all_data)

def render_navbar():
    """Render navigation bar"""
    has_data = st.session_state.current_results is not None and len(st.session_state.current_results) > 0
    status_html = """
        <div class="navbar-status">
            <div class="navbar-status-dot"></div>
            Système opérationnel
        </div>
    """ if has_data else ""
    
    st.markdown(f"""
    <div class="navbar">
        <div class="navbar-brand">
            <div class="navbar-logo">S</div>
            <div>
                <div class="navbar-title">SentimentPro</div>
                <div class="navbar-subtitle">Analyse de Sentiment IA</div>
            </div>
        </div>
        <div class="navbar-actions">
            {status_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metrics(df):
    """Render metrics cards"""
    total = len(df)
    positive = len(df[df['sentiment'] == 'positive'])
    negative = len(df[df['sentiment'] == 'negative'])
    neutral = len(df[df['sentiment'] == 'neutral'])
    
    pos_pct = round(positive/total*100) if total > 0 else 0
    neg_pct = round(negative/total*100) if total > 0 else 0
    
    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card total">
            <div class="metric-header">
                <div class="metric-icon total">📊</div>
            </div>
            <div class="metric-value">{total}</div>
            <div class="metric-label">Total Commentaires</div>
        </div>
        <div class="metric-card positive">
            <div class="metric-header">
                <div class="metric-icon positive">✓</div>
                <div class="metric-trend up">↑ {pos_pct}%</div>
            </div>
            <div class="metric-value">{positive}</div>
            <div class="metric-label">Positifs</div>
        </div>
        <div class="metric-card negative">
            <div class="metric-header">
                <div class="metric-icon negative">✗</div>
                <div class="metric-trend down">↓ {neg_pct}%</div>
            </div>
            <div class="metric-value">{negative}</div>
            <div class="metric-label">Négatifs</div>
        </div>
        <div class="metric-card neutral">
            <div class="metric-header">
                <div class="metric-icon neutral">○</div>
            </div>
            <div class="metric-value">{neutral}</div>
            <div class="metric-label">Neutres</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_comment_card(row, idx):
    """Render a comment card"""
    sentiment_config = {
        'positive': ('✓ Positif', 'positive'),
        'negative': ('✗ Négatif', 'negative'),
        'neutral': ('○ Neutre', 'neutral')
    }
    
    badge_text, badge_class = sentiment_config.get(row['sentiment'], ('○ Neutre', 'neutral'))
    confidence = round(row['confidence'] * 100)
    
    st.markdown(f"""
    <div class="comment-card">
        <div class="comment-header">
            <div class="comment-meta">
                <span class="badge badge-{badge_class}">{badge_text}</span>
                <span class="badge badge-secondary">#{idx + 1}</span>
            </div>
            <div class="comment-confidence">
                <div class="comment-confidence-label">Confiance</div>
                <div class="comment-confidence-value">{confidence}%</div>
            </div>
        </div>
        <div class="comment-text">{row['comment']}</div>
        <div class="comment-tags">
            <span class="badge badge-primary">🏷️ {row['theme']}</span>
            <span class="badge badge-secondary">📌 {row['topic']}</span>
            <span class="badge badge-secondary">📄 {row['image_source']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_sentiment_chart(df):
    """Create sentiment pie chart"""
    sentiment_counts = df['sentiment'].value_counts()
    
    colors = {'positive': '#00875A', 'neutral': '#FF8B00', 'negative': '#DE350B'}
    labels = {'positive': 'Positif', 'neutral': 'Neutre', 'negative': 'Négatif'}
    
    fig = go.Figure(data=[go.Pie(
        labels=[labels.get(s, s) for s in sentiment_counts.index],
        values=sentiment_counts.values,
        hole=0.65,
        marker_colors=[colors.get(s, '#8993A4') for s in sentiment_counts.index],
        textinfo='percent',
        textfont_size=14,
        textfont_color='white',
        hovertemplate="<b>%{label}</b><br>%{value} commentaires<br>%{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        margin=dict(t=20, b=60, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=320,
        annotations=[dict(
            text=f"<b>{len(df)}</b><br>Total",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )]
    )
    
    return fig

def create_theme_chart(df):
    """Create theme bar chart"""
    theme_counts = df['theme'].value_counts().head(8)
    
    fig = go.Figure(data=[go.Bar(
        y=theme_counts.index,
        x=theme_counts.values,
        orientation='h',
        marker_color='#0066FF',
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>%{x} commentaires<extra></extra>"
    )])
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=320,
        yaxis=dict(
            categoryorder='total ascending',
            tickfont=dict(size=12)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='#EBECF0',
            tickfont=dict(size=11)
        )
    )
    
    return fig

def create_confidence_chart(df):
    """Create confidence distribution chart"""
    fig = go.Figure(data=[go.Histogram(
        x=df['confidence'],
        nbinsx=20,
        marker_color='#6554C0',
        hovertemplate="Confiance: %{x:.0%}<br>Nombre: %{y}<extra></extra>"
    )])
    
    fig.update_layout(
        xaxis_title="Score de confiance",
        yaxis_title="Nombre de commentaires",
        margin=dict(t=20, b=40, l=40, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=280,
        xaxis=dict(
            tickformat='.0%',
            showgrid=True,
            gridcolor='#EBECF0'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#EBECF0'
        )
    )
    
    return fig

def export_data(df, format_type):
    """Export data"""
    if format_type == "CSV":
        return df.to_csv(index=False).encode('utf-8')
    elif format_type == "Excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Analyse')
        return output.getvalue()
    elif format_type == "JSON":
        return df.to_json(orient='records', force_ascii=False).encode('utf-8')

def main():
    # Navbar
    render_navbar()
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Page header
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Tableau de bord</h1>
        <p class="page-description">Analysez automatiquement les sentiments de vos commentaires clients à partir de captures d'écran.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    if st.session_state.current_results is not None and len(st.session_state.current_results) > 0:
        render_metrics(st.session_state.current_results)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📤 Importer", "💬 Résultats", "📊 Analytique"])
    
    # Tab 1: Upload
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-header">
            <div class="card-title">
                <div class="card-title-icon">📤</div>
                Importer des captures d'écran
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="card-body">', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Déposez vos fichiers ici",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Formats acceptés: PNG, JPG, JPEG",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px; margin: 20px 0;">
                <span class="badge badge-primary">✓ {len(uploaded_files)} fichier(s) sélectionné(s)</span>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("👁️ Aperçu des images", expanded=False):
                cols = st.columns(min(5, len(uploaded_files)))
                for idx, file in enumerate(uploaded_files[:10]):
                    with cols[idx % 5]:
                        st.image(file, caption=file.name, use_container_width=True)
                if len(uploaded_files) > 10:
                    st.info(f"+ {len(uploaded_files) - 10} autre(s) fichier(s)")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_files:
            st.markdown('<div class="card-footer">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Lancer l'analyse", use_container_width=True, type="primary"):
                    if not st.session_state.model_loaded:
                        with st.spinner("Chargement du modèle d'analyse..."):
                            st.session_state.sentiment_model = load_sentiment_model()
                            st.session_state.model_loaded = True
                    
                    if st.session_state.sentiment_model:
                        st.markdown("""
                        <div class="progress-container">
                            <div class="progress-spinner"></div>
                            <div class="progress-title">Analyse en cours</div>
                            <div class="progress-subtitle">Extraction et analyse des commentaires...</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        stats_container = st.empty()
                        
                        df_results = process_images(
                            uploaded_files,
                            st.session_state.sentiment_model,
                            progress_bar,
                            status_text,
                            stats_container
                        )
                        
                        if len(df_results) > 0:
                            st.session_state.current_results = df_results
                            st.session_state.analysis_history.append({
                                'timestamp': datetime.now(),
                                'images': len(uploaded_files),
                                'comments': len(df_results)
                            })
                            st.success(f"✅ Analyse terminée : {len(df_results)} commentaires analysés")
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.warning("⚠️ Aucun commentaire détecté dans les images")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: Results
    with tab2:
        if st.session_state.current_results is not None and len(st.session_state.current_results) > 0:
            df = st.session_state.current_results
            
            # Filters
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            
            with col1:
                search = st.text_input("🔍 Rechercher", placeholder="Rechercher dans les commentaires...", label_visibility="collapsed")
            with col2:
                sentiment_filter = st.selectbox("Sentiment", ["Tous", "Positif", "Négatif", "Neutre"], label_visibility="collapsed")
            with col3:
                themes = ["Tous les thèmes"] + list(df['theme'].unique())
                theme_filter = st.selectbox("Thème", themes, label_visibility="collapsed")
            with col4:
                csv = export_data(df, "CSV")
                st.download_button("⬇️ CSV", csv, f"export_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
            with col5:
                if st.button("🗑️ Reset", use_container_width=True):
                    st.session_state.current_results = None
                    st.rerun()
            
            # Apply filters
            filtered = df.copy()
            if search:
                filtered = filtered[filtered['comment'].str.contains(search, case=False, na=False)]
            if sentiment_filter != "Tous":
                mapping = {"Positif": "positive", "Négatif": "negative", "Neutre": "neutral"}
                filtered = filtered[filtered['sentiment'] == mapping[sentiment_filter]]
            if theme_filter != "Tous les thèmes":
                filtered = filtered[filtered['theme'] == theme_filter]
            
            st.markdown(f"""
            <div style="margin: 16px 0; color: #5E6C84; font-size: 14px;">
                Affichage de <strong>{len(filtered)}</strong> sur {len(df)} résultats
            </div>
            """, unsafe_allow_html=True)
            
            # Comments
            for idx, (_, row) in enumerate(filtered.head(50).iterrows()):
                render_comment_card(row, idx)
            
            if len(filtered) > 50:
                st.info(f"Affichage limité aux 50 premiers résultats. {len(filtered) - 50} résultats supplémentaires.")
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-title">Aucun résultat</div>
                <div class="empty-state-description">Importez des captures d'écran et lancez une analyse pour voir les résultats ici.</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 3: Analytics
    with tab3:
        if st.session_state.current_results is not None and len(st.session_state.current_results) > 0:
            df = st.session_state.current_results
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="chart-card">
                    <div class="chart-title">📊 Distribution des sentiments</div>
                </div>
                """, unsafe_allow_html=True)
                fig = create_sentiment_chart(df)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("""
                <div class="chart-card">
                    <div class="chart-title">🏷️ Thèmes principaux</div>
                </div>
                """, unsafe_allow_html=True)
                fig = create_theme_chart(df)
                st.plotly_chart(fig, use_container_width=True)
            
            # Confidence distribution
            st.markdown("""
            <div class="chart-card" style="margin-top: 20px;">
                <div class="chart-title">📈 Distribution des scores de confiance</div>
            </div>
            """, unsafe_allow_html=True)
            fig = create_confidence_chart(df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.markdown("""
            <div class="card" style="margin-top: 20px;">
                <div class="card-header">
                    <div class="card-title">📋 Données détaillées</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            display_df = df[['comment', 'sentiment', 'confidence', 'theme', 'topic']].copy()
            display_df.columns = ['Commentaire', 'Sentiment', 'Confiance', 'Thème', 'Topic']
            display_df['Confiance'] = display_df['Confiance'].apply(lambda x: f"{x*100:.0f}%")
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            # Export options
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "📥 Exporter en CSV",
                    export_data(df, "CSV"),
                    f"analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    "📥 Exporter en Excel",
                    export_data(df, "Excel"),
                    f"analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with col3:
                st.download_button(
                    "📥 Exporter en JSON",
                    export_data(df, "JSON"),
                    f"analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json",
                    use_container_width=True
                )
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <div class="empty-state-title">Aucune donnée</div>
                <div class="empty-state-description">Lancez une analyse pour visualiser les statistiques et graphiques.</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()