import streamlit as st, plotly.express as px, pandas as pd

# Set Streamlit page config for better aesthetics and mobile responsiveness
dark_bg = "#23272f"
light_text = "#e4e6eb"
accent_blue = "#64b5f6"
accent_green = "#81c784"
accent_red = "#e57373"
accent_yellow = "#ffd54f"

st.set_page_config(
    page_title="Supplement & Brand Aspect Sentiment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode, improved sidebar readability, and mobile responsiveness
st.markdown(
    f"""
    <style>
    body, .main, .stApp {{background-color: {dark_bg} !important; color: {light_text} !important;}}
    .stPlotlyChart {{background-color: #282c34 !important; border-radius: 12px; box-shadow: 0 2px 8px #111; padding: 1.5rem;}}
    section[data-testid="stSidebar"] {{background-color: {dark_bg} !important; color: {light_text} !important;}}
    label, .stSelectbox label, .stSidebar label, .stSidebar .css-1cpxqw2 {{color: {light_text} !important;}}
    /* Responsive font and padding for mobile */
    @media (max-width: 600px) {{
        .stPlotlyChart {{padding: 0.5rem !important;}}
        .block-container {{padding: 0.5rem 0.2rem 0.5rem 0.2rem !important;}}
        h1, h2, h3, h4, h5, h6 {{font-size: 1.1em !important;}}
        .stMarkdown p, .stMarkdown span, .stMarkdown div, .stTextInput input, .stSelectbox div {{font-size: 0.95em !important;}}
        .stSidebar {{width: 100vw !important; min-width: 0 !important;}}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Softer, aesthetic color palette for dark mode plots
color_discrete_map = {
    "positive": accent_green,   # Soft Green
    "neutral": accent_blue,    # Soft Blue
    "negative": accent_red     # Soft Red
}

# Read supplement data
absa_df_supps = pd.read_parquet("absa_df_supps.parquet")
absa_df_supps["month"] = absa_df_supps["dt"].dt.to_period("M")

# Read brand data
absa_df_brands = pd.read_parquet("absa_df_brands.parquet")
absa_df_brands["month"] = absa_df_brands["dt"].dt.to_period("M")

st.title(":sparkles: Supplement & Brand Aspect Sentiment Dashboard :sparkles:")
st.markdown("""
This dashboard allows you to explore sentiment trends and aspect mixes for both **supplements** and **brands**. Use the sidebar to select your focus and interact with the vibrant visualizations below.
""")

# Set default selections
supp_default = "creatine" if "creatine" in absa_df_supps["supplement"].unique() else sorted(absa_df_supps["supplement"].unique())[0]
aspect_default = "side effects" if "side effects" in absa_df_supps["aspect"].unique() else sorted(absa_df_supps["aspect"].unique())[0]
brand_default = "optimum nutrition" if "optimum nutrition" in absa_df_brands["supplement"].unique() else sorted(absa_df_brands["supplement"].unique())[0]
brand_aspect_default = "effectiveness" if "effectiveness" in absa_df_brands["aspect"].unique() else sorted(absa_df_brands["aspect"].unique())[0]

# Supplements section
st.header(":pill: Supplements Data")
supp = st.sidebar.selectbox("Supplement", sorted(absa_df_supps["supplement"].unique()), key="supp", index=sorted(absa_df_supps["supplement"].unique()).index(supp_default))
aspect = st.sidebar.selectbox("Aspect (Supplements)", sorted(absa_df_supps["aspect"].unique()), key="supp_aspect", index=sorted(absa_df_supps["aspect"].unique()).index(aspect_default))

trend_supp = (
    absa_df_supps.query("supplement == @supp and aspect == @aspect")
           .pivot_table(index="month", columns="sentiment", aggfunc="size", fill_value=0)
)
trend_supp.index = trend_supp.index.to_timestamp()

fig_trend_supp = px.line(
    trend_supp,
    markers=True,  # Show points
    line_shape="spline",
    title=f"Supplement: {supp} – {aspect} trend",
    color_discrete_sequence=[color_discrete_map.get(s, '#888') for s in trend_supp.columns],
)
fig_trend_supp.update_traces(line=dict(width=2))  # Thinner lines
fig_trend_supp.update_layout(
    plot_bgcolor=dark_bg,
    paper_bgcolor="#282c34",
    font=dict(size=15, color=light_text),
    title_font=dict(size=22, color=accent_blue),
    legend_title_text='Sentiment',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(color=light_text),
    yaxis=dict(color=light_text),
    transition=dict(duration=700, easing="elastic-in-out")
)
st.plotly_chart(fig_trend_supp, use_container_width=True)

mix_supp = (
    absa_df_supps[absa_df_supps["supplement"] == supp]
          .groupby(["aspect","sentiment"]).size().unstack(fill_value=0).reset_index()
)
fig_mix_supp = px.bar(
    mix_supp,
    x="aspect",
    y=["positive","neutral","negative"],
    barmode="stack",
    title=f"Supplement: {supp} – sentiment mix by aspect",
    color_discrete_map=color_discrete_map
)
fig_mix_supp.update_layout(
    plot_bgcolor=dark_bg,
    paper_bgcolor="#282c34",
    font=dict(size=15, color=light_text),
    title_font=dict(size=20, color=accent_blue),
    legend_title_text='Sentiment',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(color=light_text),
    yaxis=dict(color=light_text),
    transition=dict(duration=700, easing="elastic-in-out")
)
st.plotly_chart(fig_mix_supp, use_container_width=True)

# Brands section
st.header(":label: Brands Data")
brand = st.sidebar.selectbox("Brand", sorted(absa_df_brands["supplement"].unique()), key="brand", index=sorted(absa_df_brands["supplement"].unique()).index(brand_default))
brand_aspect = st.sidebar.selectbox("Aspect (Brands)", sorted(absa_df_brands["aspect"].unique()), key="brand_aspect", index=sorted(absa_df_brands["aspect"].unique()).index(brand_aspect_default))

trend_brand = (
    absa_df_brands.query("supplement == @brand and aspect == @brand_aspect")
           .pivot_table(index="month", columns="sentiment", aggfunc="size", fill_value=0)
)
trend_brand.index = trend_brand.index.to_timestamp()

fig_trend_brand = px.line(
    trend_brand,
    markers=True,  # Show points
    line_shape="spline",
    title=f"Brand: {brand} – {brand_aspect} trend",
    color_discrete_sequence=[color_discrete_map.get(s, '#888') for s in trend_brand.columns],
)
fig_trend_brand.update_traces(line=dict(width=2))  # Thinner lines
fig_trend_brand.update_layout(
    plot_bgcolor=dark_bg,
    paper_bgcolor="#282c34",
    font=dict(size=15, color=light_text),
    title_font=dict(size=22, color=accent_green),
    legend_title_text='Sentiment',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(color=light_text),
    yaxis=dict(color=light_text),
    transition=dict(duration=700, easing="elastic-in-out")
)
st.plotly_chart(fig_trend_brand, use_container_width=True)

mix_brand = (
    absa_df_brands[absa_df_brands["supplement"] == brand]
          .groupby(["aspect","sentiment"]).size().unstack(fill_value=0).reset_index()
)
fig_mix_brand = px.bar(
    mix_brand,
    x="aspect",
    y=["positive","neutral","negative"],
    barmode="stack",
    title=f"Brand: {brand} – sentiment mix by aspect",
    color_discrete_map=color_discrete_map
)
fig_mix_brand.update_layout(
    plot_bgcolor=dark_bg,
    paper_bgcolor="#282c34",
    font=dict(size=15, color=light_text),
    title_font=dict(size=20, color=accent_green),
    legend_title_text='Sentiment',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(color=light_text),
    yaxis=dict(color=light_text),
    transition=dict(duration=700, easing="elastic-in-out")
)
st.plotly_chart(fig_mix_brand, use_container_width=True)
