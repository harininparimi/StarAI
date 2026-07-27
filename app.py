from pathlib import Path
import streamlit as st

from claude_client import research_and_score
from config import KNOWLEDGE_DIR, MODEL
from excel_export import dataframe_to_excel
from knowledge_loader import load_knowledge
from prompt_builder import build_prompt
from scoring import build_results_table

st.set_page_config(page_title="StarAI", page_icon="⭐", layout="wide")


def apply_styles():
    st.markdown("""
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    .hero {
      padding: 1.5rem 1.7rem; border-radius: 18px;
      background: linear-gradient(135deg,#111827 0%,#312e81 55%,#6d28d9 100%);
      color:white; margin-bottom:1.25rem;
    }
    .hero h1 {margin:0; font-size:2.25rem;}
    .hero p {margin:.4rem 0 0 0; opacity:.92;}
    .note {
      border-left:4px solid #6d28d9; padding:.8rem 1rem;
      background:#f5f3ff; border-radius:8px; margin:.8rem 0 1.2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def require_access():
    password = st.secrets.get("APP_PASSWORD", "")
    if not password or st.session_state.get("authenticated"):
        return

    st.markdown(
        '<div class="hero"><h1>StarAI</h1>'
        '<p>Corporate AI Training Opportunity Intelligence</p></div>',
        unsafe_allow_html=True,
    )
    entered = st.text_input("Pilot password", type="password")
    if st.button("Sign in", type="primary", use_container_width=True):
        if entered == password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


@st.cache_data(show_spinner=False)
def cached_knowledge(folder: str):
    return load_knowledge(Path(folder))


def api_key():
    key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is missing from Streamlit secrets.")
    return key


apply_styles()
require_access()

st.markdown(
    '<div class="hero"><h1>StarAI</h1>'
    '<p>StarNet Technologies · Corporate AI Training Opportunity Intelligence</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="note"><strong>Research-only agent:</strong>
StarAI uses public information to identify and prioritize opportunities.
It does not contact, call, message, post, connect, or submit forms.</div>
""", unsafe_allow_html=True)

try:
    knowledge, knowledge_files = cached_knowledge(str(KNOWLEDGE_DIR))
except Exception as exc:
    st.error(str(exc))
    st.stop()

with st.sidebar:
    st.header("Pilot information")
    st.write(f"Model: `{MODEL}`")
    st.write(f"Knowledge files: **{len(knowledge_files)}**")
    with st.expander("Loaded files"):
        for filename in knowledge_files:
            st.write(filename)
    st.caption("Human review is mandatory before any sales action.")
    if st.session_state.get("authenticated") and st.button(
        "Sign out", use_container_width=True
    ):
        st.session_state.clear()
        st.rerun()

default_request = (
    "Identify and score up to five large corporate AI training opportunities "
    "in Dubai. Prioritize organizations with recent AI, digital transformation, "
    "future-skills, workforce-development, or leadership-development signals. "
    "Identify publicly verifiable L&D, talent, HR, digital transformation, "
    "innovation, data, or AI decision-makers where available."
)

request = st.text_area(
    "Enter the StarAI research request",
    value=default_request,
    height=150,
)

if st.button(
    "Research and score opportunities",
    type="primary",
    use_container_width=True,
):
    if not request.strip():
        st.warning("Enter a research request.")
        st.stop()

    try:
        with st.spinner(
            "StarAI is researching public signals and scoring opportunities..."
        ):
            payload = research_and_score(
                api_key(),
                build_prompt(request.strip(), knowledge),
            )
            result = build_results_table(payload)

        st.session_state["latest_result"] = result
        st.success(f"Completed. {len(result)} opportunity(s) assessed.")
    except Exception as exc:
        st.error(f"Unable to complete the request: {exc}")

if "latest_result" in st.session_state:
    result = st.session_state["latest_result"]
    summary = [
        "Rank", "Company", "Sector", "Total Score", "Tier", "Recommendation"
    ]

    st.subheader("Ranked corporate training opportunities")
    st.dataframe(
        result[summary], use_container_width=True, hide_index=True
    )

    with st.expander("View evidence, decision-makers, scoring, and sources"):
        st.dataframe(result, use_container_width=True, hide_index=True)

    st.download_button(
        "Download Excel report",
        data=dataframe_to_excel(result),
        file_name="StarAI_Corporate_Training_Leads.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
