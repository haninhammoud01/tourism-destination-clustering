import streamlit as st
import plotly.express as px
import sys
sys.path.append('..')
from utils import setup_page
setup_page()

# ─── LOAD SESSION STATE ─────────────────────────────────────
df                   = st.session_state['df']
cluster_labels       = st.session_state['cluster_labels']
cluster_descriptions = st.session_state['cluster_descriptions']
cluster_colors       = st.session_state['cluster_colors']
cluster_icons        = st.session_state['cluster_icons']
feature_labels       = st.session_state['feature_labels']
fitur                = st.session_state['fitur']
hex_to_rgba          = st.session_state['hex_to_rgba']

# ─── PAGE ───────────────────────────────────────────────────
st.title("Find My Destination")
st.markdown("##### Answer a few questions about your travel preferences, and we'll recommend the best destination clusters for you to explore.")
st.markdown("---")

# ─── FORM PREFERENSI ────────────────────────────────────────
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("#### Your Travel Preferences")

    trip_length = st.selectbox(
        "How long do you plan to stay?",
        ["Short trip (1-3 days)", "Medium stay (4-7 days)", "Long stay (8+ days)"],
        help="This helps match your schedule to the right destination type."
    )
    destination_type = st.selectbox(
        "What type of destination do you prefer?",
        ["Busy & popular", "Nature & wildlife",
         "Luxury & exclusive", "Cultural & historical", "Island & beach"],
        help="Choose the experience that excites you most."
    )
    region_pref = st.selectbox(
        "Which region interests you most?",
        ["Any region", "Europe", "Asia", "Americas", "Africa", "Oceania"],
        help="Filter results by your preferred continent."
    )
    crowd_pref = st.selectbox(
        "How do you feel about crowds?",
        ["Love busy places", "Prefer moderate crowds", "Prefer quiet destinations"],
        help="This affects whether we recommend high-traffic or off-the-beaten-path destinations."
    )

with col2:
    st.markdown("#### How It Works")
    st.info(
        "This tool matches your travel style to one of **9 destination clusters** "
        "identified by analyzing 185 countries using K-Prototypes Clustering. "
        "Each cluster groups countries with similar tourism characteristics."
    )
    st.markdown("**Features used in clustering:**")
    for feat, desc in {
        "Inbound Tourists"  : "Number of international visitors",
        "Hotel Guests"      : "Foreign guests in accommodation",
        "Same-Day Arrivals" : "Day-trip visitors",
        "Length of Stay"    : "Average nights spent",
        "Employment"        : "Tourism jobs per 1,000 people",
        "Tourism GDP %"     : "Economic contribution of tourism"
    }.items():
        st.markdown(f"- **{feat}**: {desc}")

st.markdown("---")

if st.button("Find My Destination", type="primary", use_container_width=True):

    # ─── SCORING LOGIC ──────────────────────────────────────
    scores = {i: 0 for i in range(9)}

    if trip_length == "Long stay (8+ days)":
        scores[7] += 3; scores[4] += 2; scores[0] += 1
    elif trip_length == "Medium stay (4-7 days)":
        scores[2] += 2; scores[3] += 2; scores[8] += 1
    else:
        scores[6] += 3; scores[5] += 2; scores[1] += 2

    if destination_type == "Busy & popular":
        scores[5] += 3; scores[6] += 3; scores[8] += 2
    elif destination_type == "Nature & wildlife":
        scores[7] += 3; scores[4] += 3; scores[2] += 2
    elif destination_type == "Luxury & exclusive":
        scores[1] += 4; scores[5] += 1
    elif destination_type == "Cultural & historical":
        scores[3] += 3; scores[8] += 2; scores[0] += 2
    elif destination_type == "Island & beach":
        scores[4] += 4; scores[0] += 2; scores[7] += 1

    region_cluster_map = {
        "Europe"  : [8, 5],
        "Asia"    : [3, 5],
        "Americas": [0, 6],
        "Africa"  : [2, 7],
        "Oceania" : [4, 7]
    }
    if region_pref != "Any region":
        for c in region_cluster_map.get(region_pref, []):
            scores[c] += 2

    if crowd_pref == "Love busy places":
        scores[5] += 2; scores[6] += 2
    elif crowd_pref == "Prefer quiet destinations":
        scores[1] += 2; scores[4] += 2; scores[2] += 1

    top3 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

    # ─── HASIL REKOMENDASI ──────────────────────────────────
    st.subheader("Your Recommended Destinations")

    medals = ["🥇 Top Pick", "🥈 2nd Choice", "🥉 3rd Choice"]

    for rank, (cluster_id, score) in enumerate(top3):
        countries = df[df['cluster'] == cluster_id]['Entity'].tolist()
        if region_pref != "Any region":
            filtered = df[
                (df['cluster'] == cluster_id) &
                (df['region'] == region_pref)
            ]['Entity'].tolist()
            show_countries = filtered if filtered else countries[:10]
        else:
            show_countries = countries[:10]

        color = cluster_colors[cluster_id]
        icon  = cluster_icons[cluster_id]

        st.markdown(f"""
        <div style="border: 2px solid {color}; border-radius: 12px;
                    padding: 18px; margin-bottom: 16px;
                    background: linear-gradient(135deg, {hex_to_rgba(color, 0.06)}, white);">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                <span style="font-size:28px;">{icon}</span>
                <div>
                    <span style="font-size:13px; color:#888;">{medals[rank]}</span><br>
                    <span style="font-size:18px; font-weight:bold; color:{color};">
                        Cluster {cluster_id}: {cluster_labels[cluster_id]}
                    </span>
                </div>
            </div>
            <p style="color:#444; margin:8px 0;">{cluster_descriptions[cluster_id]}</p>
            <div style="margin-top:10px;">
                <b style="color:#333;">Countries to consider:</b><br>
                <span style="color:#555;">{", ".join(show_countries)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ─── SCATTER PLOT REKOMENDASI ───────────────────────────
    st.subheader("Explore Recommended Destinations")
    st.caption("Select two features to compare countries from your recommended clusters.")

    col_x, col_y = st.columns(2)
    with col_x:
        x_axis = st.selectbox("X Axis", list(feature_labels.keys()),
                              format_func=lambda x: feature_labels[x], key="find_x")
    with col_y:
        y_axis = st.selectbox("Y Axis", list(feature_labels.keys()),
                              index=3, format_func=lambda x: feature_labels[x], key="find_y")

    top3_ids = [c for c, _ in top3]
    df_rec   = df[df['cluster'].isin(top3_ids)].copy()
    df_rec['cluster_label'] = df_rec['cluster'].map(cluster_labels)

    fig = px.scatter(
        df_rec,
        x=x_axis, y=y_axis,
        color='cluster_label',
        hover_name='Entity',
        size_max=18,
        color_discrete_map={cluster_labels[c]: cluster_colors[c] for c in top3_ids},
        labels={
            x_axis: feature_labels[x_axis],
            y_axis: feature_labels[y_axis],
            'cluster_label': 'Cluster'
        },
        title=f"{feature_labels[x_axis]} vs {feature_labels[y_axis]}"
    )
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color='white')))
    fig.update_layout(
        height=480,
        plot_bgcolor='#F8FBFF',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#E0EAFF', title=feature_labels[x_axis]),
        yaxis=dict(showgrid=True, gridcolor='#E0EAFF', title=feature_labels[y_axis]),
        legend=dict(orientation="h", y=1.12, title="Cluster"),
        font=dict(family="sans-serif", size=12)
    )
    st.plotly_chart(fig, use_container_width=True)
    