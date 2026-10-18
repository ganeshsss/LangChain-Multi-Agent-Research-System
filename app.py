import re
import streamlit as st
from src.pipelines.pipeline import run_research_pipeline

st.set_page_config(page_title="Multi-Agent Research System", page_icon="🔎", layout="wide")

st.title("🔎 Multi-Agent Research System")
st.caption("Search agent → Reader agent → Writer → Critic")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
1. **Search agent** finds sources on the web
2. **Reader agent** scrapes the best page
3. **Writer** drafts a structured report
4. **Critic** scores and reviews the report
"""
    )
    st.info("A full run makes several AI calls and can take a minute or two.")

# ---------- Input ----------
topic = st.text_input(
    "Research topic",
    placeholder="e.g. The impact of AI on the job market in 2026",
)
run = st.button("Generate report", type="primary", disabled=not topic.strip())

# ---------- Run pipeline ----------
if run:
    try:
        with st.status("Running pipeline...", expanded=True) as status:
            state = run_research_pipeline(topic.strip(), on_step=st.write)
            status.update(label="Done!", state="complete", expanded=False)
        # keep results so they survive Streamlit reruns (e.g. after clicking download)
        st.session_state["state"] = state
        st.session_state["topic"] = topic.strip()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")

# ---------- Show results ----------
state = st.session_state.get("state")
if state:
    st.subheader(f"Results: {st.session_state['topic']}")

    match = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", state["feedback"])
    col1, col2 = st.columns([1, 4])
    with col1:
        st.metric("Critic score", f"{match.group(1)}/10" if match else "N/A")
    with col2:
        st.download_button(
            "⬇️ Download report (.md)",
            data=state["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    tab_report, tab_critic, tab_search, tab_scrape = st.tabs(
        ["📝 Report", "🧐 Critic review", "🔎 Search results", "📄 Scraped content"]
    )
    with tab_report:
        st.markdown(state["report"])
    with tab_critic:
        st.text(state["feedback"])
    with tab_search:
        st.markdown(state["search_results"])
    with tab_scrape:
        st.markdown(state["scraped_content"])