import streamlit as st
import plotly.express as px
import sys
sys.path.append('..')
from utils import setup_page
setup_page()

# ─── LOAD SESSION STATE ─────────────────────────────────────
df                   = st.session_state['df']
fitur                = st.session_state['fitur']
cluster_labels       = st.session_state['cluster_labels']
cluster_descriptions = st.session_state['cluster_descriptions']
cluster_colors       = st.session_state['cluster_colors']
feature_labels       = st.session_state['feature_labels']
hex_to_rgba          = st.session_state['hex_to_rgba']

# ─── PAGE ───────────────────────────────────────────────────
st.title("Country Profile")
st.markdown("##### Explore the full tourism profile of any country and discover similar destinations.")
st.markdown("---")

country_list     = sorted(df['Entity'].tolist())
selected_country = st.selectbox("Select a Country", country_list,
                                 index=country_list.index("Indonesia"))

data         = df[df['Entity'] == selected_country].iloc[0]
cluster_id   = int(data['cluster'])
border_color = cluster_colors[cluster_id]

st.markdown("---")

# Header profil negara
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"""
    <div style="border-left: 6px solid {border_color};
                background-color:{hex_to_rgba(border_color, 0.1)};
                padding: 16px; border-radius: 8px;">
        <h2>{selected_country}</h2>
        <p><b>Region:</b> {data['region']}</p>
        <p><b>Cluster {cluster_id}:</b> {cluster_labels[cluster_id]}</p>
        <p><i>{cluster_descriptions[cluster_id]}</i></p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.metric("Inbound Tourists",  f"{data['inbound_tourists']:,.0f}")
    st.metric("Hotel Guests",      f"{data['foreign_hotel_guests']:,.0f}")
    st.metric("Same Day Arrivals", f"{data['same_day_arrivals']:,.0f}")
with col3:
    st.metric("Avg Length of Stay", f"{data['avg_length_of_stay']:.2f} days")
    st.metric("Employment/1000",    f"{data['employment_per_1000']:.2f}")
    st.metric("Tourism GDP %",      f"{data['tourism_gdp_pct']:.2f}%")

st.markdown("---")

# Scatter plot — negara dipilih vs semua negara
st.subheader("Position Among All Countries")
st.caption("Select two features to see where this country stands globally.")

col_x, col_y = st.columns(2)
with col_x:
    x_axis = st.selectbox("X Axis", list(feature_labels.keys()),
                          format_func=lambda x: feature_labels[x], key="profile_x")
with col_y:
    y_axis = st.selectbox("Y Axis", list(feature_labels.keys()),
                          index=3, format_func=lambda x: feature_labels[x], key="profile_y")

df_bg  = df[df['Entity'] != selected_country].copy()
df_sel = df[df['Entity'] == selected_country].copy()

fig = px.scatter(
    df_bg,
    x=x_axis, y=y_axis,
    hover_name='Entity',
    labels={x_axis: feature_labels[x_axis], y_axis: feature_labels[y_axis]}
)
fig.update_traces(
    marker=dict(color='lightgrey', size=7, opacity=0.6),
    name='Other Countries',
    showlegend=True
)

fig.add_scatter(
    x=df_sel[x_axis], y=df_sel[y_axis],
    mode='markers+text',
    marker=dict(color=border_color, size=18,
                line=dict(width=2, color='black')),
    text=[selected_country],
    textposition='top center',
    textfont=dict(size=12, color=border_color),
    name=selected_country,
    hovertemplate=f"<b>{selected_country}</b><br>" +
                  feature_labels[x_axis] + f": {data[x_axis]:,.2f}<br>" +
                  feature_labels[y_axis] + f": {data[y_axis]:,.2f}<extra></extra>"
)

fig.update_layout(
    height=500,
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='#f0f0f0', title=feature_labels[x_axis]),
    yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title=feature_labels[y_axis]),
    legend=dict(orientation="h", y=1.1)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Scatter plot — negara dipilih vs cluster-nya
st.subheader("Position Within Its Cluster")
st.caption("How this country compares to others in the same cluster.")

df_cluster = df[df['cluster'] == cluster_id].copy()
df_others  = df_cluster[df_cluster['Entity'] != selected_country]
df_self    = df_cluster[df_cluster['Entity'] == selected_country]

fig2 = px.scatter(
    df_others,
    x=x_axis, y=y_axis,
    hover_name='Entity',
    labels={x_axis: feature_labels[x_axis], y_axis: feature_labels[y_axis]}
)
fig2.update_traces(
    marker=dict(color=hex_to_rgba(border_color, 0.5), size=10,
                line=dict(width=1, color=border_color)),
    name=f'Cluster {cluster_id} countries',
    showlegend=True
)

fig2.add_scatter(
    x=df_self[x_axis], y=df_self[y_axis],
    mode='markers+text',
    marker=dict(color=border_color, size=18,
                line=dict(width=2, color='black')),
    text=[selected_country],
    textposition='top center',
    textfont=dict(size=12, color=border_color),
    name=selected_country,
    hovertemplate=f"<b>{selected_country}</b><br>" +
                  feature_labels[x_axis] + f": {data[x_axis]:,.2f}<br>" +
                  feature_labels[y_axis] + f": {data[y_axis]:,.2f}<extra></extra>"
)

fig2.update_layout(
    height=450,
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='#f0f0f0', title=feature_labels[x_axis]),
    yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title=feature_labels[y_axis]),
    legend=dict(orientation="h", y=1.1)
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Rekomendasi negara serupa
st.subheader("Similar Destinations")
st.caption("Countries in the same cluster with similar tourism characteristics.")

similar = df[
    (df['cluster'] == cluster_id) &
    (df['Entity'] != selected_country)
][['Entity', 'region'] + fitur].copy()

similar.columns = ['Country', 'Region', 'Inbound Tourists',
                   'Hotel Guests', 'Same Day Arrivals',
                   'Avg Stay (days)', 'Employment/1000', 'Tourism GDP %']
for col in ['Inbound Tourists', 'Hotel Guests', 'Same Day Arrivals']:
    similar[col] = similar[col].apply(lambda x: f"{x:,.0f}")
similar['Avg Stay (days)'] = similar['Avg Stay (days)'].apply(lambda x: f"{x:.2f}")
similar['Employment/1000'] = similar['Employment/1000'].apply(lambda x: f"{x:.2f}")
similar['Tourism GDP %']   = similar['Tourism GDP %'].apply(lambda x: f"{x:.2f}%")

st.dataframe(similar, use_container_width=True, hide_index=True)
