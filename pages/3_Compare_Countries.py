import streamlit as st
import plotly.express as px
import pandas as pd
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
st.title("Compare Countries")
st.markdown("##### Select two countries to compare their tourism characteristics side by side.")
st.markdown("---")

country_list = sorted(df['Entity'].tolist())

col1, col2 = st.columns(2)
with col1:
    country_a = st.selectbox("Select First Country", country_list,
                              index=country_list.index("Indonesia"))
with col2:
    country_b = st.selectbox("Select Second Country", country_list,
                              index=country_list.index("Malaysia"))

if country_a == country_b:
    st.warning("Please select two different countries.")
else:
    data_a = df[df['Entity'] == country_a].iloc[0]
    data_b = df[df['Entity'] == country_b].iloc[0]
    ca     = int(data_a['cluster'])
    cb     = int(data_b['cluster'])

    st.markdown("---")

    # Header perbandingan
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="border-left: 6px solid {cluster_colors[ca]};
                    background-color:{hex_to_rgba(cluster_colors[ca], 0.1)};
                    padding: 16px; border-radius: 8px; text-align:center;">
            <h3>{country_a}</h3>
            <p><b>Cluster {ca}</b><br>{cluster_labels[ca]}</p>
            <small>{data_a['region']}</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="border-left: 6px solid {cluster_colors[cb]};
                    background-color:{hex_to_rgba(cluster_colors[cb], 0.1)};
                    padding: 16px; border-radius: 8px; text-align:center;">
            <h3>{country_b}</h3>
            <p><b>Cluster {cb}</b><br>{cluster_labels[cb]}</p>
            <small>{data_b['region']}</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if ca == cb:
        st.success("Both countries are in the same cluster - they share similar tourism characteristics!")
    else:
        st.info("These countries are in different clusters - they have distinct tourism profiles.")

    st.markdown("---")

    # Scatter plot interaktif perbandingan
    st.subheader("Feature Scatter Plot")
    st.caption("Select two features to see where both countries stand among all countries.")

    col_x, col_y = st.columns(2)
    with col_x:
        x_axis = st.selectbox("X Axis", list(feature_labels.keys()),
                              format_func=lambda x: feature_labels[x], key="compare_x")
    with col_y:
        y_axis = st.selectbox("Y Axis", list(feature_labels.keys()),
                              index=3, format_func=lambda x: feature_labels[x], key="compare_y")

    df_all = df.copy()
    df_bg  = df_all[~df_all['Entity'].isin([country_a, country_b])]
    df_highlight = df_all[df_all['Entity'].isin([country_a, country_b])].copy()
    df_highlight['color'] = df_highlight['cluster'].map(cluster_colors)

    fig = px.scatter(
        df_bg,
        x=x_axis, y=y_axis,
        hover_name='Entity',
        labels={x_axis: feature_labels[x_axis], y_axis: feature_labels[y_axis]}
    )
    fig.update_traces(
        marker=dict(color='lightgrey', size=7, opacity=0.5),
        name='Other Countries',
        showlegend=True
    )

    for _, row in df_highlight.iterrows():
        clr = cluster_colors[int(row['cluster'])]
        fig.add_scatter(
            x=[row[x_axis]], y=[row[y_axis]],
            mode='markers+text',
            marker=dict(color=clr, size=16, line=dict(width=2, color='black')),
            text=[row['Entity']],
            textposition='top center',
            textfont=dict(size=11, color=clr),
            name=row['Entity'],
            hovertemplate=f"<b>{row['Entity']}</b><br>" +
                          feature_labels[x_axis] + f": {row[x_axis]:,.2f}<br>" +
                          feature_labels[y_axis] + f": {row[y_axis]:,.2f}<extra></extra>"
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

    # Tabel perbandingan detail
    st.subheader("Detailed Comparison")
    comparison_data = {
        "Feature": list(feature_labels.values()),
        country_a: [
            f"{data_a['inbound_tourists']:,.0f}",
            f"{data_a['foreign_hotel_guests']:,.0f}",
            f"{data_a['same_day_arrivals']:,.0f}",
            f"{data_a['avg_length_of_stay']:.2f} days",
            f"{data_a['employment_per_1000']:.2f}",
            f"{data_a['tourism_gdp_pct']:.2f}%"
        ],
        country_b: [
            f"{data_b['inbound_tourists']:,.0f}",
            f"{data_b['foreign_hotel_guests']:,.0f}",
            f"{data_b['same_day_arrivals']:,.0f}",
            f"{data_b['avg_length_of_stay']:.2f} days",
            f"{data_b['employment_per_1000']:.2f}",
            f"{data_b['tourism_gdp_pct']:.2f}%"
        ]
    }
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
    