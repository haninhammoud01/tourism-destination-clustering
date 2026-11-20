import streamlit as st
import pandas as pd
import pickle
import warnings
warnings.filterwarnings('ignore')

# ─── HELPER ─────────────────────────────────────────────────
def hex_to_rgba(hex_color, opacity=0.15):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r},{g},{b},{opacity})'

# ─── CLUSTER CONFIG ─────────────────────────────────────────
cluster_labels = {
    0: "Americas - Latin & Caribbean",
    1: "Exclusive Luxury Destinations",
    2: "Developing African Destinations",
    3: "Asia - Middle East & Central Asia",
    4: "Pacific Island Destinations",
    5: "World Mass Tourism Hubs",
    6: "Mega Destinations",
    7: "Nature & Ecotourism",
    8: "Established European Destinations"
}

cluster_descriptions = {
    0: "Countries known for vibrant culture, warm hospitality, and diverse landscapes across Latin America and the Caribbean.",
    1: "Ultra-exclusive destinations with the highest tourism employment rates and GDP contribution — Monaco, Macao, and Cayman Islands.",
    2: "Emerging destinations across Africa with rich wildlife and cultural heritage, offering untapped potential for adventurous travelers.",
    3: "A dynamic mix of ancient history, modern cities, and diverse cultures spanning the Middle East and Central Asia.",
    4: "Stunning island nations across the Pacific, perfect for travelers seeking pristine beaches, marine life, and Polynesian culture.",
    5: "The world's top tourism powerhouses — high visitor volumes, world-class infrastructure, and iconic attractions.",
    6: "The busiest destinations on earth with massive visitor flows — France, USA, Mexico, and Poland.",
    7: "Destinations celebrated for extraordinary natural beauty, wildlife safaris, and immersive eco-experiences.",
    8: "Europe's mature tourism markets — rich history, excellent connectivity, and diverse experiences."
}

cluster_colors = {
    0: "#1A73E8",
    1: "#F4A100",
    2: "#34A853",
    3: "#EA4335",
    4: "#9B27AF",
    5: "#00ACC1",
    6: "#FF6D00",
    7: "#43A047",
    8: "#3949AB"
}

cluster_icons = {
    0: "🌎",
    1: "💎",
    2: "🌍",
    3: "🕌",
    4: "🏝",
    5: "🗼",
    6: "✈",
    7: "🌿",
    8: "🏰"
}

feature_labels = {
    'inbound_tourists'    : 'Inbound Tourists',
    'foreign_hotel_guests': 'Hotel Guests',
    'same_day_arrivals'   : 'Same Day Arrivals',
    'avg_length_of_stay'  : 'Avg Length of Stay (days)',
    'employment_per_1000' : 'Employment per 1000',
    'tourism_gdp_pct'     : 'Tourism GDP %'
}

fitur = [
    'inbound_tourists',
    'foreign_hotel_guests',
    'same_day_arrivals',
    'avg_length_of_stay',
    'employment_per_1000',
    'tourism_gdp_pct'
]

# ─── LOAD DATA ──────────────────────────────────────────────
@st.cache_data
def load_data():
    import os
    # Cari file pkl dari berbagai kemungkinan lokasi
    possible_paths = [
        'model_components.pkl',
        '../model_components.pkl',
        os.path.join(os.path.dirname(__file__), 'model_components.pkl')
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return pickle.load(f)
    raise FileNotFoundError("model_components.pkl tidak ditemukan!")

def get_data():
    components = load_data()
    df       = components['df_result']
    df_scaled= components['df_scaled']
    pca      = components['pca']
    df_eval  = components['df_hasil_mm']
    return df, df_scaled, pca, df_eval

# ─── CSS ────────────────────────────────────────────────────
def apply_css():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1A73E8 0%, #0D47A1 100%);
        }
        [data-testid="stSidebar"] * { color: white !important; }
        [data-testid="stSidebar"] a { color: white !important; }
        [data-testid="metric-container"] {
            background-color: #F0F6FF;
            border: 1px solid #1A73E8;
            border-radius: 10px;
            padding: 16px;
        }
        h1 { color: #1A73E8 !important; }
        h2 { color: #1A73E8 !important; }
        h3 { color: #0D47A1 !important; }
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        hr { border-color: #1A73E8 !important; opacity: 0.2; }
    </style>
    """, unsafe_allow_html=True)

# ─── SIDEBAR ────────────────────────────────────────────────
def render_sidebar():
    st.sidebar.markdown("""
    <div style="text-align:center; padding: 10px 0 20px 0;">
        <div style="font-size: 48px;">✈</div>
        <div style="font-size: 18px; font-weight: bold; line-height:1.3;">
            Tourism Destination Explorer
        </div>
        <div style="font-size: 11px; opacity: 0.8; margin-top: 4px;">
            Data-driven travel insights
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="font-size:12px; opacity:0.8; text-align:center;">
        185 countries &nbsp;|&nbsp; 9 clusters<br>
        Silhouette Score: <b>0.5635</b>
    </div>
    """, unsafe_allow_html=True)

# ─── SETUP HALAMAN ──────────────────────────────────────────
def setup_page(page_title="Tourism Destination Explorer"):
    st.set_page_config(
        page_title=page_title,
        page_icon="🌎",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    apply_css()
    render_sidebar()
    