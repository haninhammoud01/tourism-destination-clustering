import streamlit as st
import plotly.express as px
import numpy as np
import sys
sys.path.append('..')
from utils import setup_page
setup_page()

# ─── LOAD SESSION STATE ─────────────────────────────────────
df                   = st.session_state['df']
df_scaled            = st.session_state['df_scaled']
pca                  = st.session_state['pca']
fitur                = st.session_state['fitur']
cluster_labels       = st.session_state['cluster_labels']
cluster_descriptions = st.session_state['cluster_descriptions']
cluster_colors       = st.session_state['cluster_colors']
feature_labels       = st.session_state['feature_labels']
hex_to_rgba          = st.session_state['hex_to_rgba']

# ─── PAGE ───────────────────────────────────────────────────
st.title("Explore by Cluster")
st.markdown("##### Dive deep into each destination cluster and discover which countries belong to each group.")
st.markdown("---")

selected_cluster = st.selectbox(
    "Select a Cluster",
    options=list(cluster_labels.keys()),
    format_func=lambda x: f"Cluster {x} — {cluster_labels[x]}"
)

df_cluster   = df[df['cluster'] == selected_cluster].copy()
border_color = cluster_colors[selected_cluster]

# Header cluster
st.markdown(f"""
<div style="border-left: 6px solid {border_color};
            background-color:{hex_to_rgba(border_color, 0.1)};
            padding: 16px; border-radius: 8px; margin-bottom: 20px;">
    <h3 style="color:{border_color};">Cluster {selected_cluster} — {cluster_labels[selected_cluster]}</h3>
    <p>{cluster_descriptions[selected_cluster]}</p>
    <b>{len(df_cluster)} countries</b>
</div>
""", unsafe_allow_html=True)

# Metrik ringkas
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(df_cluster))
col2.metric("Avg Length of Stay", f"{df_cluster['avg_length_of_stay'].mean():.1f} days")
col3.metric("Avg Tourism GDP %", f"{df_cluster['tourism_gdp_pct'].mean():.1f}%")

st.markdown("---")

# Scatter plot interaktif — user pilih fitur X dan Y
st.subheader("Interactive Scatter Plot")
st.caption("Select any two features to explore how countries in this cluster compare.")

col_x, col_y = st.columns(2)
with col_x:
    x_axis = st.selectbox(
        "X Axis", list(feature_labels.keys()),
        format_func=lambda x: feature_labels[x], key="explore_x"
    )
with col_y:
    y_axis = st.selectbox(
        "Y Axis", list(feature_labels.keys()),
        index=3, format_func=lambda x: feature_labels[x], key="explore_y"
    )

# Semua negara sebagai background
df_all = df.copy()
df_all['cluster_label'] = df_all['cluster'].map(cluster_labels)
df_sel = df_all[df_all['cluster'] == selected_cluster].copy()
df_bg  = df_all[df_all['cluster'] != selected_cluster].copy()

fig = px.scatter(
    df_bg,
    x=x_axis, y=y_axis,
    hover_name='Entity',
    labels={
        x_axis: feature_labels[x_axis],
        y_axis: feature_labels[y_axis]
    }
)
fig.update_traces(
    marker=dict(color='lightgrey', size=7, opacity=0.5),
    name='Other Countries',
    showlegend=True
)

# Cluster yang dipilih di atas
fig.add_scatter(
    x=df_sel[x_axis], y=df_sel[y_axis],
    mode='markers+text',
    marker=dict(color=border_color, size=12, line=dict(width=1, color='black')),
    text=df_sel['Entity'],
    textposition='top center',
    textfont=dict(size=9),
    name=cluster_labels[selected_cluster],
    hovertemplate='<b>%{text}</b><br>' +
                  feature_labels[x_axis] + ': %{x:,.2f}<br>' +
                  feature_labels[y_axis] + ': %{y:,.2f}<extra></extra>'
)

fig.update_layout(
    height=520,
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='#f0f0f0', title=feature_labels[x_axis]),
    yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title=feature_labels[y_axis]),
    legend=dict(orientation="h", y=1.1)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Tabel negara
st.subheader(f"Countries in Cluster {selected_cluster}")
df_show = df_cluster[['Entity', 'region'] + fitur].copy()
df_show.columns = ['Country', 'Region', 'Inbound Tourists',
                   'Hotel Guests', 'Same Day Arrivals',
                   'Avg Stay (days)', 'Employment/1000', 'Tourism GDP %']
for col in ['Inbound Tourists', 'Hotel Guests', 'Same Day Arrivals']:
    df_show[col] = df_show[col].apply(lambda x: f"{x:,.0f}")
df_show['Avg Stay (days)']  = df_show['Avg Stay (days)'].apply(lambda x: f"{x:.2f}")
df_show['Employment/1000']  = df_show['Employment/1000'].apply(lambda x: f"{x:.2f}")
df_show['Tourism GDP %']    = df_show['Tourism GDP %'].apply(lambda x: f"{x:.2f}%")

st.dataframe(df_show, use_container_width=True, hide_index=True)
