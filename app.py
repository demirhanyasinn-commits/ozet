import streamlit as st
import pandas as pd
import yfinance as yf
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="PRO Fon Simülatörü", layout="wide", initial_sidebar_state="collapsed")

# 2. Gelişmiş Tasarım CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #0e0e0e; font-family: 'Inter', sans-serif; }
    
    .ticker-container {
        background-color: #161616; padding: 12px 20px; border-radius: 12px;
        display: flex; justify-content: space-between; align-items: center;
        border: 1px solid #262626; margin-bottom: 30px; overflow-x: auto;
    }
    .ticker-item { text-align: center; min-width: 130px; padding: 0 15px; border-right: 1px solid #333; }
    .ticker-item:last-child { border-right: none; }
    .ticker-label { color: #888; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }
    .ticker-value { color: #fff; font-size: 0.95rem; font-weight: 700; display: block; margin: 2px 0; }
    .delta-up { color: #00ff88; font-size: 0.8rem; font-weight: 600; }
    .delta-down { color: #ff4b4b; font-size: 0.8rem; font-weight: 600; }

    .fund-card {
        background-color: #161616; border-left: 4px solid #007bff;
        border-radius: 12px; padding: 24px; margin-bottom: 20px;
        border-top: 1px solid #262626; border-right: 1px solid #262626; border-bottom: 1px solid #262626;
    }
    .fund-title { color: #fff; font-size: 1.4rem; font-weight: 700; }
    .fund-subtitle { color: #666; font-size: 0.75rem; margin-bottom: 20px; height: 35px; overflow: hidden; }
    .est-label { color: #999; font-size: 0.75rem; }
    .est-value { color: #00ff88; font-size: 2.2rem; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

def get_istanbul_now():
