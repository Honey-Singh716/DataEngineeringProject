"""
ROAD INSIGHT — AI-Powered Indian Road Accident Analysis Dashboard
File: dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Road Insight — Indian Road Safety Analytics",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME & CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #111827 100%);
    border-right: 1px solid rgba(99, 179, 237, 0.15);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(26,43,67,0.9), rgba(15,30,50,0.9));
    border: 1px solid rgba(99, 179, 237, 0.25);
    border-radius: 16px;
    padding: 20px !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99,179,237,0.2);
}
[data-testid="metric-container"] label {
    color: #94a3b8 !important; font-size: 0.8rem !important;
    font-weight: 500 !important; letter-spacing: 0.05em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e2e8f0 !important; font-size: 1.8rem !important; font-weight: 700 !important;
}

.section-header {
    font-size: 1.4rem; font-weight: 700; color: #e2e8f0;
    margin: 1.5rem 0 0.5rem 0; padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(99, 179, 237, 0.3);
}

.hero-banner {
    background: linear-gradient(135deg, rgba(37,99,235,0.25) 0%, rgba(6,182,212,0.15) 50%, rgba(139,92,246,0.15) 100%);
    border: 1px solid rgba(99,179,237,0.25); border-radius: 20px;
    padding: 2.5rem; margin-bottom: 2rem;
    backdrop-filter: blur(10px); box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}
.hero-title {
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #06b6d4, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1.2;
}
.hero-sub { color: #94a3b8; font-size: 1rem; margin-top: 0.5rem; }

div[data-testid="stExpander"] {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(99, 179, 237, 0.15); border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY DARK THEME HELPERS
# ─────────────────────────────────────────────
PAPER_BG   = "rgba(15,23,42,0)"
GRID_COLOR = "rgba(99,179,237,0.08)"
COLOR_QUAL = ["#63b3ed","#06b6d4","#a78bfa","#f59e0b","#34d399","#f87171","#fb923c","#e879f9","#4ade80"]

def styled_fig(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PAPER_BG,
        font=dict(family="Inter", color="#e2e8f0"),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(99,179,237,0.2)", borderwidth=1),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zeroline=False)
    fig.update_yaxes(gridcolor=GRID_COLOR, zeroline=False)
    return fig

# ─────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return create_engine(
        "postgresql://postgres:b24cm1030@localhost:5432/roadinsight",
        connect_args={"options": "-csearch_path=road_insight,public"}
    )

@st.cache_data(ttl=300)
def query(_engine, sql: str) -> pd.DataFrame:
    with _engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem 0;'>
        <div style='font-size:2.5rem;'>🚦</div>
        <div style='font-size:1.2rem; font-weight:800; color:#63b3ed; letter-spacing:-0.02em;'>Road Insight</div>
        <div style='font-size:0.72rem; color:#64748b; margin-top:2px;'>Indian Road Safety Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["🏠 Overview", "📈 National Trends", "🗺️ State Analysis",
         "🏙️ City Rankings", "💥 Collision & Violations", "🌧️ Weather & Road Features"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#475569; line-height:1.7;'>
    <b style='color:#64748b;'>Data Sources</b><br>
    MoRTH Road Accident Reports<br>
    2019 – 2023 · 10 CSV datasets<br>
    50 cities · 37 states/UTs<br><br>
    <b style='color:#64748b;'>Schema</b><br>
    PostgreSQL · 3NF · 13 tables<br>
    9 analytical views
    </div>
    """, unsafe_allow_html=True)

engine = get_engine()


# ══════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════
if page == "🏠 Overview":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🚦 Road Insight</div>
        <div class="hero-title" style="font-size:1.5rem;">Indian Road Safety Analytics Platform</div>
        <div class="hero-sub">Comprehensive analysis of road accidents across India's 37 States & UTs and 50 major cities · 2019–2023</div>
    </div>
    """, unsafe_allow_html=True)

    nat23 = query(engine, "SELECT * FROM vw_national_trends WHERE year=2023")
    nat19 = query(engine, "SELECT * FROM vw_national_trends WHERE year=2019")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        val = int(nat23["total_accidents"].iloc[0])
        prev = int(nat19["total_accidents"].iloc[0])
        st.metric("🚗 Total Accidents (2023)", f"{val:,}", f"+{val-prev:,} vs 2019")
    with c2:
        val = int(nat23["total_fatalities"].iloc[0])
        prev = int(nat19["total_fatalities"].iloc[0])
        st.metric("💀 Lives Lost (2023)", f"{val:,}", f"+{val-prev:,} vs 2019")
    with c3:
        val = int(nat23["total_injured"].iloc[0])
        prev = int(nat19["total_injured"].iloc[0])
        st.metric("🏥 Persons Injured (2023)", f"{val:,}", f"+{val-prev:,} vs 2019")
    with c4:
        acc = int(nat23["total_accidents"].iloc[0])
        kil = int(nat23["total_fatalities"].iloc[0])
        st.metric("⚠️ Fatality Rate", f"{round(kil/acc*100,1)}%", "per 100 accidents")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="section-header">📅 National Trend 2019–2023</div>', unsafe_allow_html=True)
        trend = query(engine, "SELECT year, total_accidents, total_fatalities, total_injured FROM vw_national_trends WHERE year>=2019 ORDER BY year")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend["year"], y=trend["total_accidents"], name="Accidents",
            line=dict(color="#63b3ed", width=3), mode="lines+markers",
            marker=dict(size=8, color="#63b3ed", line=dict(color="#fff", width=1.5))))
        fig.add_trace(go.Scatter(x=trend["year"], y=trend["total_fatalities"], name="Fatalities",
            line=dict(color="#f87171", width=3), mode="lines+markers",
            marker=dict(size=8, color="#f87171", line=dict(color="#fff", width=1.5))))
        fig.add_trace(go.Scatter(x=trend["year"], y=trend["total_injured"], name="Injured",
            line=dict(color="#f59e0b", width=2, dash="dot"), mode="lines+markers",
            marker=dict(size=7, color="#f59e0b")))
        fig.update_layout(title="Accidents, Fatalities & Injuries 2019–2023",
                          xaxis=dict(tickvals=list(trend["year"])), height=320)
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">💥 Collision Types (2023)</div>', unsafe_allow_html=True)
        coll = query(engine, "SELECT collision_type_name, accident_count FROM vw_collision_type_summary WHERE year=2023 ORDER BY accident_count DESC")
        fig2 = px.pie(coll, values="accident_count", names="collision_type_name",
                      hole=0.55, color_discrete_sequence=COLOR_QUAL)
        fig2.update_traces(textposition="outside", textinfo="percent+label", textfont_size=10)
        fig2.update_layout(showlegend=False, height=320,
                           annotations=[dict(text="2023", x=0.5, y=0.5,
                                            font_size=14, font_color="#e2e8f0", showarrow=False)])
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    st.markdown('<div class="section-header">🗺️ Top 10 Most Dangerous States (2023)</div>', unsafe_allow_html=True)
    states = query(engine, "SELECT state_name, accident_count, persons_killed FROM vw_state_stats_full WHERE year=2023 AND accident_count IS NOT NULL ORDER BY accident_count DESC LIMIT 10")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Accidents", x=states["state_name"], y=states["accident_count"],
                          marker_color="#63b3ed", opacity=0.9))
    fig3.add_trace(go.Bar(name="Killed", x=states["state_name"], y=states["persons_killed"],
                          marker_color="#f87171", opacity=0.9))
    fig3.update_layout(barmode="group", height=350, xaxis_title="", yaxis_title="Count",
                       title="Accidents & Deaths by State — 2023")
    st.plotly_chart(styled_fig(fig3), use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 2 — NATIONAL TRENDS
# ══════════════════════════════════════════════
elif page == "📈 National Trends":
    st.markdown('<div class="hero-banner"><div class="hero-title">📈 National Trends</div><div class="hero-sub">Historical data from 1970 to 2023 — long-term patterns and safety rate analysis</div></div>', unsafe_allow_html=True)

    trend = query(engine, "SELECT * FROM vw_national_trends ORDER BY year")

    tab1, tab2, tab3 = st.tabs(["📊 Accident Volume", "📉 Rate per Population", "📅 Year-over-Year Change"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend["year"], y=trend["total_accidents"], name="Total Accidents",
            fill="tozeroy", fillcolor="rgba(99,179,237,0.08)",
            line=dict(color="#63b3ed", width=2.5), mode="lines"))
        fig.add_trace(go.Scatter(x=trend["year"], y=trend["total_fatalities"], name="Fatalities",
            line=dict(color="#f87171", width=2.5), mode="lines"))
        fig.add_trace(go.Scatter(x=trend["year"], y=trend["total_injured"], name="Injured",
            line=dict(color="#f59e0b", width=2, dash="dot"), mode="lines"))
        fig.add_vrect(x0=2019.5, x1=2020.5, fillcolor="rgba(248,113,113,0.08)",
                      annotation_text="COVID-19 Drop", annotation_position="top left", line_width=0)
        fig.update_layout(title="Accident Volume 1970–2023",
                          xaxis_title="Year", yaxis_title="Count", height=440)
        st.plotly_chart(styled_fig(fig), use_container_width=True)

        col1, col2, col3 = st.columns(3)
        peak = trend.loc[trend["total_accidents"].idxmax()]
        with col1:
            st.metric("📈 Peak Accident Year", str(int(peak["year"])), f"{int(peak['total_accidents']):,} accidents")
        covid_drop = trend[trend["year"]==2020]["total_accidents"].values
        pre_covid  = trend[trend["year"]==2019]["total_accidents"].values
        if len(covid_drop) and len(pre_covid):
            drop = round((pre_covid[0]-covid_drop[0])/pre_covid[0]*100, 1)
            with col2: st.metric("😷 COVID-19 Drop (2020)", f"-{drop}%", "vs 2019")
        val23 = trend[trend["year"]==2023]["total_accidents"].values
        val10 = trend[trend["year"]==2010]["total_accidents"].values
        if len(val23) and len(val10):
            chg = round((val23[0]-val10[0])/val10[0]*100, 1)
            with col3: st.metric("📉 Change since 2010", f"{chg:+.1f}%", "total accidents")

    with tab2:
        hist = trend[trend["accidents_per_lakh_pop"].notna()].copy()
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(x=hist["year"], y=hist["accidents_per_lakh_pop"],
                              name="Accidents / Lakh Pop", marker_color="#63b3ed", opacity=0.75), secondary_y=False)
        fig2.add_trace(go.Scatter(x=hist["year"], y=hist["killed_per_lakh_pop"],
                                  name="Killed / Lakh Pop", line=dict(color="#f87171", width=2.5),
                                  mode="lines+markers"), secondary_y=True)
        fig2.update_yaxes(title_text="Accidents per Lakh", secondary_y=False, gridcolor=GRID_COLOR)
        fig2.update_yaxes(title_text="Killed per Lakh", secondary_y=True, gridcolor=GRID_COLOR)
        fig2.update_layout(template="plotly_dark", paper_bgcolor=PAPER_BG,
                           font=dict(family="Inter", color="#e2e8f0"),
                           title="Road Safety Rates per Lakh Population (1970–2019)", height=420,
                           margin=dict(l=20,r=20,t=40,b=20))
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        yoy = query(engine, """
            SELECT year, total_accidents, total_fatalities,
                   LAG(total_accidents) OVER (ORDER BY year) AS prev_acc
            FROM vw_national_trends WHERE year>=2019 ORDER BY year
        """)
        yoy = yoy.dropna(subset=["prev_acc"])
        yoy["pct"] = ((yoy["total_accidents"]-yoy["prev_acc"])/yoy["prev_acc"]*100).round(1)
        colors = ["#f87171" if v>0 else "#34d399" for v in yoy["pct"]]
        fig3 = go.Figure(go.Bar(x=yoy["year"].astype(str), y=yoy["pct"], marker_color=colors,
                                text=[f"{v:+.1f}%" for v in yoy["pct"]], textposition="outside"))
        fig3.update_layout(title="Year-over-Year % Change in Accidents (2019–2023)",
                           yaxis_title="% Change", xaxis_title="Year", height=380)
        st.plotly_chart(styled_fig(fig3), use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 3 — STATE ANALYSIS
# ══════════════════════════════════════════════
elif page == "🗺️ State Analysis":
    st.markdown('<div class="hero-banner"><div class="hero-title">🗺️ State Analysis</div><div class="hero-sub">Accident and fatality breakdown across all Indian States & Union Territories (2019–2023)</div></div>', unsafe_allow_html=True)

    year_sel = st.select_slider("Select Year", options=[2019,2020,2021,2022,2023], value=2023)
    states = query(engine, f"""
        SELECT state_name, state_type, accident_count, persons_killed, accident_rank, killed_rank
        FROM vw_state_stats_full WHERE year={year_sel} AND accident_count IS NOT NULL
        ORDER BY accident_count DESC
    """)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("States with Data", len(states))
    with c2: st.metric("Total Accidents", f"{states['accident_count'].sum():,}")
    with c3: st.metric("Total Killed", f"{int(states['persons_killed'].sum()):,}")
    with c4: st.metric("🔴 Most Accidents", states.iloc[0]["state_name"] if not states.empty else "—")

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📊 Accidents Ranking", "💀 Fatalities Ranking", "📈 Year-over-Year"])

    with tab1:
        fig = px.bar(states.head(20), x="accident_count", y="state_name", orientation="h",
                     title=f"Top 20 States by Accidents — {year_sel}",
                     color="accident_count", color_continuous_scale="Blues",
                     text=states.head(20)["accident_count"].apply(lambda x: f"{x:,}"))
        fig.update_traces(textposition="outside")
        fig.update_layout(height=620, yaxis=dict(autorange="reversed"),
                          coloraxis_showscale=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with tab2:
        sk = states.dropna(subset=["persons_killed"]).sort_values("persons_killed", ascending=False)
        fig2 = px.bar(sk.head(20), x="persons_killed", y="state_name", orientation="h",
                      title=f"Top 20 States by Persons Killed — {year_sel}",
                      color="persons_killed", color_continuous_scale="Reds",
                      text=sk.head(20)["persons_killed"].apply(lambda x: f"{int(x):,}"))
        fig2.update_traces(textposition="outside")
        fig2.update_layout(height=620, yaxis=dict(autorange="reversed"),
                           coloraxis_showscale=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    with tab3:
        yoy = query(engine, "SELECT state_name, year, accident_count, yoy_pct_change FROM vw_state_yoy_comparison WHERE yoy_pct_change IS NOT NULL ORDER BY year, yoy_pct_change DESC")
        year_yoy = st.selectbox("Year for YoY Comparison", [2020,2021,2022,2023], index=3)
        yoy_f = yoy[yoy["year"]==year_yoy].sort_values("yoy_pct_change", ascending=False)
        colors = ["#f87171" if v>0 else "#34d399" for v in yoy_f["yoy_pct_change"]]
        fig3 = go.Figure(go.Bar(x=yoy_f["state_name"], y=yoy_f["yoy_pct_change"],
                                marker_color=colors,
                                text=[f"{v:+.1f}%" for v in yoy_f["yoy_pct_change"]],
                                textposition="outside"))
        fig3.update_layout(title=f"YoY % Change in Accidents — {year_yoy} vs {year_yoy-1}",
                           height=440, xaxis_tickangle=-45, yaxis_title="% Change")
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

    with st.expander("📋 Full State Data Table"):
        st.dataframe(
            states.rename(columns={"state_name":"State","state_type":"Type","accident_count":"Accidents",
                                   "persons_killed":"Killed","accident_rank":"Acc Rank","killed_rank":"Kill Rank"}),
            use_container_width=True, hide_index=True
        )


# ══════════════════════════════════════════════
# PAGE 4 — CITY RANKINGS
# ══════════════════════════════════════════════
elif page == "🏙️ City Rankings":
    st.markdown('<div class="hero-banner"><div class="hero-title">🏙️ City Rankings</div><div class="hero-sub">Road safety profile for 50 major Indian cities (2022–2023)</div></div>', unsafe_allow_html=True)

    year_c = st.radio("Year", [2022, 2023], horizontal=True, index=1)
    cities = query(engine, f"""
        SELECT city_name, state_name, accident_count, persons_killed, persons_injured,
               accident_rank, killed_rank, injured_rank
        FROM vw_city_stats_full WHERE year={year_c} ORDER BY accident_count DESC
    """)

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Cities Covered", len(cities))
    with c2: st.metric("Most Dangerous City", cities.iloc[0]["city_name"] if not cities.empty else "—")
    with c3:
        fr = round(cities["persons_killed"].sum()/cities["accident_count"].sum()*100, 1)
        st.metric("Avg Fatality Rate", f"{fr}%")

    tab1, tab2, tab3 = st.tabs(["🏆 Rankings", "🔵 Bubble Chart", "🔍 City Deep Dive"])

    with tab1:
        col_l, col_r = st.columns(2)
        with col_l:
            top10 = cities.head(10)
            fig = px.bar(top10, x="accident_count", y="city_name", orientation="h",
                         title=f"Top 10 — Accidents ({year_c})",
                         color="accident_count", color_continuous_scale="Blues",
                         text=top10["accident_count"].apply(lambda x: f"{x:,}"))
            fig.update_traces(textposition="outside")
            fig.update_layout(height=400, yaxis=dict(autorange="reversed"),
                              coloraxis_showscale=False, xaxis_title="", yaxis_title="")
            st.plotly_chart(styled_fig(fig), use_container_width=True)
        with col_r:
            top10k = cities.dropna(subset=["persons_killed"]).sort_values("persons_killed", ascending=False).head(10)
            fig2 = px.bar(top10k, x="persons_killed", y="city_name", orientation="h",
                          title=f"Top 10 — Fatalities ({year_c})",
                          color="persons_killed", color_continuous_scale="Reds",
                          text=top10k["persons_killed"].apply(lambda x: f"{int(x):,}"))
            fig2.update_traces(textposition="outside")
            fig2.update_layout(height=400, yaxis=dict(autorange="reversed"),
                               coloraxis_showscale=False, xaxis_title="", yaxis_title="")
            st.plotly_chart(styled_fig(fig2), use_container_width=True)

    with tab2:
        cities["fatality_rate"] = (cities["persons_killed"]/cities["accident_count"]*100).round(2)
        fig3 = px.scatter(cities, x="accident_count", y="persons_killed",
                          size="persons_injured", color="fatality_rate",
                          hover_name="city_name",
                          hover_data={"state_name":True,"accident_count":True,"persons_killed":True,"fatality_rate":":.2f"},
                          color_continuous_scale="RdYlGn_r",
                          title=f"City Risk Profile — Accidents vs Fatalities ({year_c})",
                          labels={"accident_count":"Total Accidents","persons_killed":"Persons Killed","fatality_rate":"Fatality Rate %"})
        fig3.update_traces(marker=dict(opacity=0.85, line=dict(color="white", width=0.5)))
        fig3.update_layout(height=500)
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

    with tab3:
        city_sel = st.selectbox("Select City", cities["city_name"].tolist())
        row = cities[cities["city_name"]==city_sel].iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Accidents", f"{int(row['accident_count']):,}", f"Rank #{int(row['accident_rank']) if pd.notna(row['accident_rank']) else '—'}")
        with c2: st.metric("Killed", f"{int(row['persons_killed']):,}" if pd.notna(row['persons_killed']) else "—")
        with c3: st.metric("Injured", f"{int(row['persons_injured']):,}" if pd.notna(row['persons_injured']) else "—")
        with c4:
            fr = round(row["persons_killed"]/row["accident_count"]*100,1) if row["accident_count"]>0 else 0
            st.metric("Fatality Rate", f"{fr}%")

        vio = query(engine, f"SELECT violation_type_name, accident_count FROM vw_city_violation_summary WHERE city_name='{city_sel}' AND year=2023 ORDER BY accident_count DESC")
        if not vio.empty:
            fig4 = px.pie(vio, values="accident_count", names="violation_type_name",
                          title=f"Traffic Violations — {city_sel} (2023)",
                          hole=0.5, color_discrete_sequence=COLOR_QUAL)
            fig4.update_layout(height=380)
            st.plotly_chart(styled_fig(fig4), use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 5 — COLLISION & VIOLATIONS
# ══════════════════════════════════════════════
elif page == "💥 Collision & Violations":
    st.markdown('<div class="hero-banner"><div class="hero-title">💥 Collision Types & Traffic Violations</div><div class="hero-sub">National breakdown of how accidents happen and why — 2022 vs 2023</div></div>', unsafe_allow_html=True)

    coll = query(engine, "SELECT * FROM vw_collision_type_summary ORDER BY year, accident_count DESC")
    viol = query(engine, "SELECT * FROM vw_violation_type_summary ORDER BY year, accident_count DESC")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">💥 Collision Types</div>', unsafe_allow_html=True)
        yr_c = st.radio("Year ", [2022, 2023], horizontal=True, index=1, key="coll_yr")
        cf = coll[coll["year"]==yr_c]
        fig = px.bar(cf, x="collision_type_name", y="accident_count",
                     color="pct_of_total_killed", color_continuous_scale="Reds",
                     title=f"Accidents by Collision Type — {yr_c}",
                     text=cf["pct_of_total_accidents"].apply(lambda x: f"{x}%"),
                     labels={"collision_type_name":"","accident_count":"Accidents","pct_of_total_killed":"% of Deaths"})
        fig.update_traces(textposition="outside")
        fig.update_layout(height=400, xaxis_tickangle=-30)
        st.plotly_chart(styled_fig(fig), use_container_width=True)

        cf2 = cf.copy()
        cf2["severity"] = (cf2["persons_killed"]/cf2["accident_count"]*100).round(1)
        fig2 = px.bar(cf2.sort_values("severity", ascending=False),
                      x="collision_type_name", y="severity",
                      title=f"Fatality Rate by Collision Type — {yr_c} (%)",
                      color="severity", color_continuous_scale="YlOrRd",
                      text=cf2.sort_values("severity", ascending=False)["severity"].apply(lambda x: f"{x}%"))
        fig2.update_traces(textposition="outside")
        fig2.update_layout(height=360, xaxis_tickangle=-30, xaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">⚖️ Traffic Violations</div>', unsafe_allow_html=True)
        yr_v = st.radio("Year ", [2022, 2023], horizontal=True, index=1, key="viol_yr")
        vf = viol[viol["year"]==yr_v]
        fig3 = px.pie(vf, values="accident_count", names="violation_type_name",
                      title=f"Violation Share of Accidents — {yr_v}",
                      hole=0.55, color_discrete_sequence=COLOR_QUAL)
        fig3.update_traces(textposition="outside", textinfo="percent+label", pull=[0.07]+[0]*5)
        fig3.update_layout(height=380, showlegend=False,
                           annotations=[dict(text="Over-<br>speeding<br>dominates", x=0.5, y=0.5,
                                            font_size=10, font_color="#e2e8f0", showarrow=False)])
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

        fig4 = px.bar(vf, x="violation_type_name",
                      y=["accident_count","persons_killed","persons_injured"],
                      title=f"Violations — Accidents, Killed & Injured {yr_v}",
                      barmode="group", color_discrete_sequence=["#63b3ed","#f87171","#f59e0b"])
        fig4.update_layout(height=340, xaxis_tickangle=-25, xaxis_title="",
                           legend=dict(orientation="h", y=1.12))
        st.plotly_chart(styled_fig(fig4), use_container_width=True)

    # 2022 vs 2023 comparison
    st.markdown('<div class="section-header">📊 2022 vs 2023 — Side-by-Side Comparison</div>', unsafe_allow_html=True)
    c22 = coll[coll["year"]==2022][["collision_type_name","accident_count"]].rename(columns={"accident_count":"2022"})
    c23 = coll[coll["year"]==2023][["collision_type_name","accident_count"]].rename(columns={"accident_count":"2023"})
    comp = c22.merge(c23, on="collision_type_name")
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(name="2022", x=comp["collision_type_name"], y=comp["2022"], marker_color="#4b7fa3", opacity=0.8))
    fig5.add_trace(go.Bar(name="2023", x=comp["collision_type_name"], y=comp["2023"], marker_color="#63b3ed", opacity=0.9))
    fig5.update_layout(barmode="group", height=380, xaxis_tickangle=-25, xaxis_title="", yaxis_title="Accidents")
    st.plotly_chart(styled_fig(fig5), use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 6 — WEATHER & ROAD FEATURES
# ══════════════════════════════════════════════
elif page == "🌧️ Weather & Road Features":
    st.markdown('<div class="hero-banner"><div class="hero-title">🌧️ Weather & Road Features</div><div class="hero-sub">Environmental and infrastructure analysis — impact on accidents across 50 cities (2019)</div></div>', unsafe_allow_html=True)

    weather = query(engine, """
        SELECT weather_condition_name,
               SUM(accident_count) AS total_accidents, SUM(persons_killed) AS total_killed,
               SUM(persons_total_injured) AS total_injured, ROUND(AVG(fatality_rate_pct),2) AS avg_fatality_rate
        FROM vw_city_weather_summary GROUP BY weather_condition_name ORDER BY total_accidents DESC
    """)
    roads = query(engine, """
        SELECT road_feature_name,
               SUM(accident_count) AS total_accidents, SUM(persons_killed) AS total_killed,
               SUM(persons_total_injured) AS total_injured, ROUND(AVG(fatality_rate_pct),2) AS avg_fatality_rate
        FROM vw_city_road_feature_summary GROUP BY road_feature_name ORDER BY total_accidents DESC
    """)

    tab1, tab2, tab3 = st.tabs(["🌤️ Weather Conditions", "🛣️ Road Features", "🔍 City Detail"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(weather, x="weather_condition_name", y="total_accidents",
                         title="Total Accidents by Weather Condition (2019)",
                         color="avg_fatality_rate", color_continuous_scale="RdYlGn_r",
                         text=weather["total_accidents"].apply(lambda x: f"{x:,}"),
                         labels={"weather_condition_name":"","total_accidents":"Accidents","avg_fatality_rate":"Fatality Rate %"})
            fig.update_traces(textposition="outside")
            fig.update_layout(height=400, xaxis_tickangle=-15)
            st.plotly_chart(styled_fig(fig), use_container_width=True)
        with col2:
            fig2 = px.pie(weather, values="total_accidents", names="weather_condition_name",
                          title="Weather Distribution of Accidents", hole=0.5,
                          color_discrete_sequence=["#63b3ed","#a78bfa","#94a3b8","#f59e0b","#34d399"])
            fig2.update_layout(height=400)
            st.plotly_chart(styled_fig(fig2), use_container_width=True)

        fig3 = go.Figure(go.Bar(
            x=weather["weather_condition_name"], y=weather["avg_fatality_rate"],
            marker_color=["#f59e0b","#f87171","#94a3b8","#63b3ed","#34d399"],
            text=[f"{v}%" for v in weather["avg_fatality_rate"]], textposition="outside"
        ))
        fig3.update_layout(title="Average Fatality Rate % by Weather",
                           xaxis_title="", yaxis_title="Fatality Rate (%)", height=340)
        st.plotly_chart(styled_fig(fig3), use_container_width=True)
        st.info("☀️ **Key Insight**: Sunny/Clear weather has the MOST accidents — drivers are more reckless in good conditions. Hail/Sleet has the highest fatality rate despite far fewer accidents.")

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            fig4 = px.bar(roads, x="total_accidents", y="road_feature_name", orientation="h",
                          title="Accidents by Road Feature (2019)",
                          color="avg_fatality_rate", color_continuous_scale="YlOrRd",
                          text=roads["total_accidents"].apply(lambda x: f"{x:,}"))
            fig4.update_traces(textposition="outside")
            fig4.update_layout(height=440, yaxis=dict(autorange="reversed"),
                               xaxis_title="Accidents", yaxis_title="")
            st.plotly_chart(styled_fig(fig4), use_container_width=True)
        with col2:
            fig5 = px.scatter(roads, x="total_accidents", y="total_killed",
                              size="avg_fatality_rate", color="road_feature_name",
                              hover_name="road_feature_name",
                              color_discrete_sequence=COLOR_QUAL,
                              title="Road Feature Risk — Accidents vs Deaths")
            fig5.update_layout(height=440, showlegend=True)
            st.plotly_chart(styled_fig(fig5), use_container_width=True)
        st.warning("🛣️ **Key Insight**: Straight roads account for ~60% of all accidents — speed and overconfidence on open roads is the #1 risk factor, not road complexity.")

    with tab3:
        all_cities = query(engine, "SELECT DISTINCT city_name FROM vw_city_weather_summary ORDER BY city_name")
        city_sel = st.selectbox("Select City", all_cities["city_name"].tolist())

        w_city = query(engine, f"SELECT weather_condition_name, accident_count, persons_killed, persons_total_injured, fatality_rate_pct FROM vw_city_weather_summary WHERE city_name='{city_sel}' ORDER BY accident_count DESC")
        r_city = query(engine, f"SELECT road_feature_name, accident_count, persons_killed, persons_total_injured, fatality_rate_pct FROM vw_city_road_feature_summary WHERE city_name='{city_sel}' ORDER BY accident_count DESC")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🌤️ Weather Impact — {city_sel}**")
            fig6 = px.bar(w_city, x="weather_condition_name", y="accident_count",
                          color="fatality_rate_pct", color_continuous_scale="RdYlGn_r",
                          text=w_city["accident_count"], labels={"weather_condition_name":"","accident_count":"Accidents"})
            fig6.update_layout(height=340, xaxis_tickangle=-20)
            st.plotly_chart(styled_fig(fig6), use_container_width=True)
        with col2:
            st.markdown(f"**🛣️ Road Features — {city_sel}**")
            fig7 = px.bar(r_city, x="road_feature_name", y="accident_count",
                          color="fatality_rate_pct", color_continuous_scale="RdYlGn_r",
                          text=r_city["accident_count"], labels={"road_feature_name":"","accident_count":"Accidents"})
            fig7.update_layout(height=340, xaxis_tickangle=-30)
            st.plotly_chart(styled_fig(fig7), use_container_width=True)
