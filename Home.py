import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pickle
import warnings
warnings.filterwarnings('ignore')

# ─── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="Tourism Destination Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar header */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A73E8 0%, #0D47A1 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] a {
        color: white !important;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #F0F6FF;
        border: 1px solid #1A73E8;
        border-radius: 10px;
        padding: 16px;
    }

    /* Section headers */
    h1 { color: #1A73E8 !important; }
    h2 { color: #1A73E8 !important; }
    h3 { color: #0D47A1 !important; }

    /* Cluster cards */
    .cluster-card {
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
        border-left: 5px solid;
        transition: transform 0.2s;
    }
    .cluster-card:hover {
        transform: translateX(4px);
    }

    /* Main container padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Divider color */
    hr { border-color: #1A73E8 !important; opacity: 0.2; }
</style>
""", unsafe_allow_html=True)

# ─── HELPER ─────────────────────────────────────────────────
def hex_to_rgba(hex_color, opacity=0.15):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r},{g},{b},{opacity})'

# ─── LOAD DATA ──────────────────────────────────────────────
@st.cache_data
def load_data():
    with open('model_components.pkl', 'rb') as f:
        components = pickle.load(f)
    return components

components = load_data()
df         = components['df_result']
df_scaled  = components['df_scaled']
pca        = components['pca']
fitur      = components['fitur']
df_eval    = components['df_hasil_mm']

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
    1: "Ultra-exclusive destinations with the highest tourism employment rates and GDP contribution - Monaco, Macao, and Cayman Islands.",
    2: "Emerging destinations across Africa with rich wildlife and cultural heritage, offering untapped potential for adventurous travelers.",
    3: "A dynamic mix of ancient history, modern cities, and diverse cultures spanning the Middle East and Central Asia.",
    4: "Stunning island nations across the Pacific, perfect for travelers seeking pristine beaches, marine life, and Polynesian culture.",
    5: "The world's top tourism powerhouses - high visitor volumes, world-class infrastructure, and iconic attractions.",
    6: "The busiest destinations on earth with massive visitor flows - France, USA, Mexico, and Poland.",
    7: "Destinations celebrated for extraordinary natural beauty, wildlife safaris, and immersive eco-experiences.",
    8: "Europe's mature tourism markets - rich history, excellent connectivity, and diverse experiences."
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

# ─── SESSION STATE ──────────────────────────────────────────
st.session_state['df']                   = df
st.session_state['df_scaled']            = df_scaled
st.session_state['pca']                  = pca
st.session_state['fitur']                = fitur
st.session_state['df_eval']              = df_eval
st.session_state['cluster_labels']       = cluster_labels
st.session_state['cluster_descriptions'] = cluster_descriptions
st.session_state['cluster_colors']       = cluster_colors
st.session_state['cluster_icons']        = cluster_icons
st.session_state['feature_labels']       = feature_labels
st.session_state['hex_to_rgba']          = hex_to_rgba

# ─── SIDEBAR ────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="text-align:center; padding: 10px 0 20px 0;">
    <div style="font-size: 48px;">✈</div>
    <div style="font-size: 20px; font-weight: bold;">Tourism Destination Explorer</div>
    <div style="font-size: 12px; opacity: 0.8; margin-top: 4px;">Data-driven travel insights</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-size:12px; opacity:0.8; text-align:center;">
    185 countries &nbsp;|&nbsp; 9 clusters<br>
    Silhouette Score: <b>0.5635</b>
</div>
""", unsafe_allow_html=True)

# ─── HOME PAGE ──────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:16px; margin-bottom:8px;">
    <span style="font-size:48px;">✈</span>
    <div>
        <h1 style="margin:0;">Tourism Destination Explorer</h1>
        <p style="margin:0; color:#555;">Discover and compare international tourism destinations through data-driven clustering</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Metrik
col1, col2, col3, col4 = st.columns(4)
col1.metric("Countries Analyzed", "185", help="Total countries in the dataset")
col2.metric("Destination Clusters", "9", help="Number of groups identified")
col3.metric("Tourism Features", "6", help="Features used for clustering")
col4.metric("Silhouette Score", "0.5635", help="Clustering quality score (0-1)")

st.markdown("---")

# Peta dunia
st.subheader("World Tourism Clusters Map")
st.caption("Hover over any country to see its cluster and region.")

df_map = df.copy()
df_map['cluster_label'] = df_map['cluster'].map(cluster_labels)

fig_map = px.choropleth(
    df_map,
    locations="Code",
    color="cluster_label",
    hover_name="Entity",
    hover_data={"cluster_label": True, "region": True, "Code": False},
    color_discrete_map={v: cluster_colors[k] for k, v in cluster_labels.items()},
    labels={"cluster_label": "Cluster"},
)
fig_map.update_layout(
    height=550,
    margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(
        orientation="v", x=1.01, y=0.5,
        title="Cluster",
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#1A73E8",
        borderwidth=1
    ),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#CCCCCC",
        projection_type='natural earth',
        bgcolor='rgba(240,246,255,1)'
    ),
    paper_bgcolor='rgba(240,246,255,1)'
)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# Cluster overview
st.subheader("Cluster Overview")
st.caption("Click any cluster name in the sidebar to explore further.")

cols = st.columns(3)
for i, (cluster_id, label) in enumerate(cluster_labels.items()):
    col   = cols[i % 3]
    count = len(df[df['cluster'] == cluster_id])
    icon  = cluster_icons[cluster_id]
    color = cluster_colors[cluster_id]
    with col:
        st.markdown(f"""
        <div class="cluster-card" style="
            background-color:{hex_to_rgba(color, 0.08)};
            border-left-color:{color};">
            <div style="font-size:24px;">{icon}</div>
            <div style="font-weight:bold; color:{color};">Cluster {cluster_id}</div>
            <div style="font-size:14px; font-weight:600;">{label}</div>
            <div style="font-size:12px; color:#555; margin-top:4px;">
                {cluster_descriptions[cluster_id][:80]}...
            </div>
            <div style="margin-top:8px;">
                <span style="background:{color}; color:white;
                             border-radius:12px; padding:2px 10px;
                             font-size:12px;">{count} countries</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        