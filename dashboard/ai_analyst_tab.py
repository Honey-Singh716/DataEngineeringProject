"""
dashboard/ai_analyst_tab.py
Streamlit UI component for the Road Insight AI Analyst.
Provides a chat interface, suggested questions, SQL transparency expander,
interactive Plotly visualizations, CSV download, and domain-grounded explanations.
"""
from __future__ import annotations

import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ai_analyst.services.text_to_sql_service import run_text_to_sql, TextToSQLResponse
from ai_analyst.config import settings

logger = logging.getLogger(__name__)

# Re-use styling constants matching app.py theme
PAPER_BG = "rgba(15,23,42,0)"
GRID_COLOR = "rgba(99,179,237,0.08)"
COLOR_QUAL = ["#63b3ed", "#06b6d4", "#a78bfa", "#f59e0b", "#34d399", "#f87171", "#fb923c", "#e879f9", "#4ade80"]

SUGGESTED_QUESTIONS = [
    "Which states reported the highest number of accidents in 2023?",
    "Show national accident trends from 2019 to 2023.",
    "Which violation types have the highest accident counts?",
    "Compare accident counts across available states.",
    "What is the relationship between weather conditions and accidents?",
    "Which road features have the highest reported accident counts in cities?",
]


def _styled_chart(fig: go.Figure) -> go.Figure:
    """Apply Road Insight dark theme to any Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PAPER_BG,
        font=dict(family="Inter", color="#e2e8f0"),
        title_font=dict(family="Inter", color="#e2e8f0", size=14),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(99,179,237,0.2)",
            borderwidth=1,
            font=dict(color="#e2e8f0"),
        ),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zeroline=False, tickfont=dict(color="#cbd5e1"))
    fig.update_yaxes(gridcolor=GRID_COLOR, zeroline=False, tickfont=dict(color="#cbd5e1"))
    return fig


def _create_chart(df: pd.DataFrame, chart_type: str | None) -> go.Figure | None:
    """Generate a clean Plotly chart when the returned DataFrame is suitable."""
    if df is None or df.empty or len(df.columns) < 2 or chart_type in (None, "table"):
        return None

    cols = list(df.columns)
    numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c]) and not c.endswith("_id")]
    cat_cols = [c for c in cols if c not in numeric_cols and not c.endswith("_id")]

    # If all numeric, look for 'year' as category/x-axis
    if not cat_cols and "year" in cols:
        cat_cols = ["year"]
        numeric_cols = [c for c in numeric_cols if c != "year"]

    if not numeric_cols:
        return None

    try:
        # 1. Bar Chart
        if chart_type == "bar" and cat_cols and numeric_cols:
            x_col = cat_cols[0]
            y_col = numeric_cols[0]
            # Horizontal bar if more than 8 categories or long names
            if len(df) > 8 or df[x_col].astype(str).str.len().max() > 14:
                fig = px.bar(
                    df.head(15),
                    x=y_col,
                    y=x_col,
                    orientation="h",
                    color_discrete_sequence=["#38bdf8"],
                    text_auto=True,
                )
                fig.update_layout(yaxis=dict(autorange="reversed"))
            else:
                fig = px.bar(
                    df.head(15),
                    x=x_col,
                    y=y_col,
                    color_discrete_sequence=["#38bdf8"],
                    text_auto=True,
                )
            return _styled_chart(fig)

        # 2. Line Chart
        elif chart_type == "line" and ("year" in cols or cat_cols) and numeric_cols:
            x_col = "year" if "year" in cols else cat_cols[0]
            y_col = numeric_cols[0]
            fig = px.line(
                df,
                x=x_col,
                y=y_col,
                markers=True,
                color_discrete_sequence=["#06b6d4"],
            )
            return _styled_chart(fig)

        # 3. Pie Chart
        elif chart_type == "pie" and cat_cols and numeric_cols and len(df) <= 10:
            fig = px.pie(
                df,
                names=cat_cols[0],
                values=numeric_cols[0],
                color_discrete_sequence=COLOR_QUAL,
                hole=0.35,
            )
            return _styled_chart(fig)

    except Exception as exc:
        logger.warning("Auto-chart generation skipped: %s", exc)
        return None

    return None


def render_ai_analyst_page():
    """Render the full AI Analyst tab."""
    # Header Banner
    st.markdown(
        """
        <div class="hero-banner" style="padding: 1.8rem; margin-bottom: 1.2rem;">
            <div class="hero-title" style="font-size: 2rem;">🤖 Road Insight AI Analyst</div>
            <div class="hero-sub" style="font-size: 0.95rem;">
                Ask questions in plain English about Indian road accidents, state rankings, city violations, road features, and weather conditions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize Chat History in Session State
    if "ai_analyst_history" not in st.session_state:
        st.session_state.ai_analyst_history = []

    # Initialize Selected Prompt Trigger
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    # Top Controls Bar: Suggested Prompts & Clear History
    with st.expander("💡 Suggested Questions & Quick Prompts", expanded=len(st.session_state.ai_analyst_history) == 0):
        st.markdown("<div style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px;'>Click any prompt below to run it immediately:</div>", unsafe_allow_html=True)
        cols_q = st.columns(2)
        for idx, q_text in enumerate(SUGGESTED_QUESTIONS):
            col_target = cols_q[idx % 2]
            with col_target:
                if st.button(f"👉 {q_text}", key=f"btn_sug_{idx}", use_container_width=True):
                    st.session_state.pending_question = q_text

    col_btn_l, col_btn_r = st.columns([6, 1])
    with col_btn_r:
        if st.session_state.ai_analyst_history:
            if st.button("🗑️ Clear Chat", key="btn_clear_chat", use_container_width=True):
                st.session_state.ai_analyst_history = []
                st.session_state.pending_question = None
                st.rerun()

    # Display Conversation History
    for msg in st.session_state.ai_analyst_history:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"**{msg['content']}**")
        else:
            with st.chat_message("assistant", avatar="🚦"):
                _render_assistant_response(msg)

    # Question Input
    user_input = st.chat_input("Ask a question about road accidents (e.g. 'Top 5 states with most fatalities in 2023')...")

    # Handle input from text box or suggested buttons
    active_question = user_input or st.session_state.pending_question
    if active_question:
        st.session_state.pending_question = None  # Reset pending

        # 1. Add user message to history & render
        st.session_state.ai_analyst_history.append({"role": "user", "content": active_question})
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**{active_question}**")

        # 2. Process with AI Analyst backend
        with st.chat_message("assistant", avatar="🚦"):
            with st.spinner("🤖 Consulting Groq LLM & validating PostgreSQL query..."):
                resp: TextToSQLResponse = run_text_to_sql(active_question)

            # Build message payload
            asst_msg = {
                "role": "assistant",
                "status": resp.status,
                "question": active_question,
                "sql": resp.sql,
                "explanation": resp.explanation,
                "df": resp.data,
                "row_count": resp.row_count,
                "execution_time_ms": resp.execution_time_ms,
                "total_time_ms": resp.total_time_ms,
                "chart_type": resp.chart_type,
                "confidence": resp.confidence,
                "error": resp.error,
                "validation_warnings": resp.validation_warnings,
            }
            _render_assistant_response(asst_msg)
            st.session_state.ai_analyst_history.append(asst_msg)


def _render_assistant_response(msg: dict):
    """Render an assistant message card containing explanation, SQL, data, and charts."""
    status = msg.get("status", "success")

    # 1. Handle Unsupported or Clarification
    if status == "unsupported":
        st.warning(f"ℹ️ **Question Cannot Be Answered with Available Data**\n\n{msg.get('explanation')}")
        st.info("💡 **Supported Scope**: The database contains annual data for 37 States/UTs (2019–2023), 50 Cities (2022–2023), violation causes, weather (2019), and road features (2019). Try asking about state totals or city rankings!")
        return

    if status == "clarification_required":
        st.info(f"🤔 **Clarification Needed**\n\n{msg.get('explanation')}")
        return

    # 2. Handle Errors (Validation / DB / Config)
    if status == "validation_error":
        st.error(f"🛡️ **Query Blocked by Security Validator**\n\n{msg.get('error')}")
        if msg.get("sql"):
            with st.expander("🔍 View Rejected SQL", expanded=False):
                st.code(msg["sql"], language="sql")
        return

    if status == "db_not_configured":
        st.warning(f"⚠️ **Database Account Configuration Required**\n\n{msg.get('error')}")
        if msg.get("sql"):
            with st.expander("🔍 Generated & Validated SQL", expanded=True):
                st.code(msg["sql"], language="sql")
        return

    if status == "execution_error":
        st.error(f"❌ **Execution Error**: {msg.get('error')}")
        if msg.get("sql"):
            with st.expander("🔍 View SQL Query", expanded=False):
                st.code(msg["sql"], language="sql")
        return

    if status == "empty_result":
        st.info(f"ℹ️ Query executed successfully in {msg.get('execution_time_ms', 0):.1f} ms, but returned **0 rows** matching your filter.")
        if msg.get("sql"):
            with st.expander("🔍 View Generated SQL", expanded=False):
                st.code(msg["sql"], language="sql")
        return

    # 3. Successful Execution
    if status == "success":
        # AI Explanation
        if msg.get("explanation"):
            st.markdown(f"**Analysis:** {msg['explanation']}")

        # SQL Transparency Expander
        with st.expander(
            f"🔍 View Generated SQL • ⚡ {msg.get('execution_time_ms', 0):.1f} ms • 📊 {msg.get('row_count', 0)} rows",
            expanded=False,
        ):
            st.code(msg.get("sql", "-- No SQL"), language="sql")
            st.caption("✅ Validated via SQLGlot AST • Executed with `roadinsight_readonly` role (Read-Only Transaction)")
            if msg.get("validation_warnings"):
                for w in msg["validation_warnings"]:
                    st.caption(f"⚠️ {w}")

        df: pd.DataFrame | None = msg.get("df")
        if df is not None and not df.empty:
            # Layout: Visualization & Data Table
            fig = _create_chart(df, msg.get("chart_type"))
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)

            # Data Table
            st.dataframe(df, use_container_width=True)

