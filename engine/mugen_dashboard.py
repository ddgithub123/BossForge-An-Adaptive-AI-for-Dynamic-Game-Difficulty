import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# ======================
# 🎮 CONFIGURATION
# ======================
st.set_page_config(
    page_title="M.U.G.E.N Fight Analytics Dashboard",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

FIGHT_LOG_PATH = r"D:\mugen-1_1b1\mugen-1.1b1\chars\BossForge\fight_logs.csv"

# ======================
# 🧩 LOAD DATA
# ======================
@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        st.error(f"❌ File not found: {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", errors="coerce")
    return df

df = load_data(FIGHT_LOG_PATH)

if df.empty:
    st.stop()

# ======================
# 🧱 SIDEBAR
# ======================
st.sidebar.header("⚙️ Dashboard Controls")

# Filter options
from datetime import datetime

# Handle timestamps safely
time_min = df["timestamp"].min().to_pydatetime()
time_max = df["timestamp"].max().to_pydatetime()

# Sidebar slider for datetime range
time_range = st.sidebar.slider(
    "🕒 Time Range",
    min_value=time_min,
    max_value=time_max,
    value=(time_min, time_max),
    format="YYYY-MM-DD HH:mm:ss"
)

# Filter dataframe
df = df[(df["timestamp"] >= pd.Timestamp(time_range[0])) & (df["timestamp"] <= pd.Timestamp(time_range[1]))]


# ======================
# 🧭 HEADER
# ======================
st.title("🥋 M.U.G.E.N Fight Performance Dashboard")
st.markdown("Visual analytics of AI vs AI battles logged from your M.U.G.E.N engine.")

# ======================
# 🧠 SUMMARY CARDS
# ======================
col1, col2, col3, col4 = st.columns(4)

avg_aggression = df["aggression"].mean()
avg_reaction = df["reaction_time"].mean()
avg_fight_time = df["fight_time"].mean()
win_rate = (df["win"].sum() / len(df)) * 100

col1.metric("🔥 Avg Aggression", f"{avg_aggression:.2f}")
col2.metric("⚡ Avg Reaction Time", f"{avg_reaction:.2f}s")
col3.metric("⏱️ Avg Fight Duration", f"{avg_fight_time:.2f}s")
col4.metric("🏆 Win Rate", f"{win_rate:.1f}%")

st.markdown("---")

# ======================
# 📈 VISUAL ANALYTICS
# ======================

tab1, tab2, tab3 = st.tabs(["📊 Trends", "📉 Correlations", "📘 Data Table"])

with tab1:
    st.subheader("📊 Fight Parameter Trends Over Time")

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.line(df, x="timestamp", y="aggression", title="Aggression Over Time", markers=True)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        fig2 = px.line(df, x="timestamp", y="reaction_time", title="Reaction Time Over Time", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = px.line(df, x="timestamp", y="fight_time", title="Fight Duration Over Time", markers=True)
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        fig4 = px.bar(df, x="timestamp", y="win", title="Win Outcomes (1=Win, 0=Loss)")
        st.plotly_chart(fig4, use_container_width=True)

with tab2:
    st.subheader("📉 Correlation Heatmap")
    import plotly.figure_factory as ff
    corr = df.corr(numeric_only=True)
    fig = ff.create_annotated_heatmap(
        z=corr.values,
        x=list(corr.columns),
        y=list(corr.columns),
        colorscale="Viridis",
        showscale=True
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("📘 Logged Fight Data")
    st.dataframe(df, use_container_width=True)

# ======================
# 🧾 FOOTER
# ======================
st.markdown("---")
st.markdown(
    "<center>💥 Built for M.U.G.E.N AI Analytics — Powered by Streamlit & Plotly 💥</center>",
    unsafe_allow_html=True
)
