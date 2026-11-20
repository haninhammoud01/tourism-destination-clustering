import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
cluster_colors       = st.session_state['cluster_colors']
feature_labels       = st.session_state['feature_labels']
df_eval              = st.session_state['df_eval']
hex_to_rgba          = st.session_state['hex_to_rgba']

# ─── PAGE ───────────────────────────────────────────────────
st.title("About the Model")
st.markdown("##### Technical details of the K-Prototypes clustering model used in this application.")
st.markdown("---")

# Ringkasan metode
col1, col2 = st.columns(2)
with col1:
    st.subheader("Methodology")
    st.markdown("""
    **Algorithm:** K-Prototypes Clustering

    K-Prototypes is an extension of K-Means designed for **mixed-type data**
    containing both numerical and categorical variables.
    It combines the distance measures of K-Means (for numerical features)
    and K-Modes (for categorical features).

    **Why K-Prototypes?**
    The dataset contains 6 numerical features and 1 categorical feature (region),
    making K-Prototypes the most appropriate algorithm compared to K-Means
    which only handles numerical data.

    **Preprocessing Steps:**
    - Aggregated per country (mean across all available years)
    - Countries with fewer than 3 features filled were removed
    - Missing values filled with median
    - Numerical features normalized using MinMaxScaler
    - Region assigned as categorical feature
    """)

with col2:
    st.subheader("Model Configuration")
    st.markdown("""
    **Final Configuration:**
    - Algorithm: K-Prototypes
    - Initialization: Cao method
    - Number of Clusters (K): 9
    - Scaler: MinMaxScaler
    - n_init: 5
    - random_state: 42

    **Dataset:**
    - 185 countries
    - 6 numerical features
    - 1 categorical feature (region)
    - Data source: Kaggle Tourism Dataset

    **Evaluation:**
    - Silhouette Score: **0.5635** (Good)
    - Silhouette range: -1 (worst) to 1 (best)
    - Score above 0.5 indicates well-defined clusters
    """)

st.markdown("---")

# Metrik evaluasi
col1, col2, col3 = st.columns(3)
col1.metric("Final K", "9")
col2.metric("Silhouette Score", "0.5635")
col3.metric("Countries Clustered", "185")

st.markdown("---")

# Elbow & Silhouette chart
st.subheader("Model Evaluation — Elbow Method & Silhouette Score")
st.caption("K=9 was selected based on the highest Silhouette Score across all tested values.")

fig_eval = go.Figure()

fig_eval.add_trace(go.Scatter(
    x=df_eval['K'], y=df_eval['Cost'],
    mode='lines+markers',
    name='Cost (Elbow)',
    line=dict(color='steelblue', width=2),
    marker=dict(size=8),
    yaxis='y1'
))

fig_eval.add_trace(go.Scatter(
    x=df_eval['K'], y=df_eval['Silhouette'],
    mode='lines+markers',
    name='Silhouette Score',
    line=dict(color='darkorange', width=2),
    marker=dict(size=8),
    yaxis='y2'
))

fig_eval.add_vline(
    x=9, line_dash="dash", line_color="red",
    annotation_text="K=9 (selected)",
    annotation_position="top right"
)

fig_eval.update_layout(
    height=420,
    xaxis=dict(title="Number of Clusters (K)", dtick=1),
    yaxis=dict(
        title="Cost",
        title_font=dict(color='steelblue')
    ),
    yaxis2=dict(
        title="Silhouette Score",
        title_font=dict(color='darkorange'),
        overlaying='y',
        side='right'
    ),
    legend=dict(orientation="h", y=1.1),
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis_showgrid=True,
    yaxis_showgrid=True
)
st.plotly_chart(fig_eval, use_container_width=True)

st.markdown("---")

# Scatter plot semua cluster — user pilih fitur
st.subheader("All Clusters — Interactive Scatter Plot")
st.caption("Select two features to explore how all 185 countries are distributed across clusters.")

col_x, col_y = st.columns(2)
with col_x:
    x_axis = st.selectbox("X Axis", list(feature_labels.keys()),
                          format_func=lambda x: feature_labels[x], key="model_x")
with col_y:
    y_axis = st.selectbox("Y Axis", list(feature_labels.keys()),
                          index=3, format_func=lambda x: feature_labels[x], key="model_y")

df_plot = df.copy()
df_plot['cluster_label'] = df_plot['cluster'].map(cluster_labels)

fig_scatter = px.scatter(
    df_plot,
    x=x_axis, y=y_axis,
    color='cluster_label',
    hover_name='Entity',
    color_discrete_map={v: cluster_colors[k] for k, v in cluster_labels.items()},
    labels={
        x_axis: feature_labels[x_axis],
        y_axis: feature_labels[y_axis],
        'cluster_label': 'Cluster'
    },
    title=f"{feature_labels[x_axis]} vs {feature_labels[y_axis]} — All Countries"
)
fig_scatter.update_traces(marker=dict(size=9, line=dict(width=1, color='black')))
fig_scatter.update_layout(
    height=520,
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
    yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
    legend=dict(orientation="v", x=1.01, y=1)
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# Distribusi negara per cluster
st.subheader("Country Distribution per Cluster")

cluster_counts = df.groupby('cluster')['Entity'].count().reset_index()
cluster_counts['label'] = cluster_counts['cluster'].map(cluster_labels)
cluster_counts['color'] = cluster_counts['cluster'].map(cluster_colors)

fig_dist = px.bar(
    cluster_counts,
    x='cluster', y='Entity',
    color='label',
    color_discrete_map={v: cluster_colors[k] for k, v in cluster_labels.items()},
    text='Entity',
    labels={'Entity': 'Number of Countries', 'cluster': 'Cluster', 'label': 'Cluster'}
)
fig_dist.update_traces(textposition='outside')
fig_dist.update_layout(
    height=420,
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(dtick=1, title="Cluster"),
    yaxis=dict(title="Number of Countries")
)
st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("---")

# Tabel ringkasan cluster
st.subheader("Cluster Summary Table")

summary_rows = []
for c in range(9):
    df_c = df[df['cluster'] == c]
    summary_rows.append({
        'Cluster': c,
        'Label': cluster_labels[c],
        'Countries': len(df_c),
        'Avg Inbound Tourists': f"{df_c['inbound_tourists'].mean():,.0f}",
        'Avg Hotel Guests': f"{df_c['foreign_hotel_guests'].mean():,.0f}",
        'Avg Stay (days)': f"{df_c['avg_length_of_stay'].mean():.2f}",
        'Avg Tourism GDP %': f"{df_c['tourism_gdp_pct'].mean():.2f}%"
    })

st.dataframe(summary_rows, use_container_width=True, hide_index=True)
