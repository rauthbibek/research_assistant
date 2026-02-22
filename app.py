"""
Streamlit UI for the Agentic Research Assistant.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
from src.graph import build_graph, run_research
from src.config import MAX_ITERATIONS


# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="🔬 Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }

    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1.05rem;
        margin: 0;
    }

    .status-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }

    .report-container {
        background: #fafbfc;
        border: 1px solid #e1e4e8;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 1rem;
    }

    .source-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 2px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.7rem 2.5rem;
        font-size: 1.05rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    .sidebar .stTextInput > div > div > input,
    .sidebar .stTextArea > div > div > textarea {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🔬 Agentic Research Assistant</h1>
    <p>Powered by LangGraph — Multi-agent research pipeline with web search &amp; blog analysis</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar: Inputs ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Research Configuration")

    topic = st.text_input(
        "📌 Research Topic",
        placeholder="e.g. Transformer architectures in NLP",
        help="Enter the topic you want to research",
    )

    blog_urls_text = st.text_area(
        "📄 Blog / Article URLs (optional)",
        placeholder="https://example.com/blog-post-1\nhttps://example.com/blog-post-2",
        help="Enter blog or article URLs, one per line. These will be scraped and included in the research.",
        height=120,
    )

    st.divider()
    st.subheader("🎛️ Advanced Settings")

    max_iterations = st.slider(
        "Max research iterations",
        min_value=1,
        max_value=5,
        value=MAX_ITERATIONS,
        help="Maximum number of planner→researcher loops before moving to analysis",
    )

    st.divider()

    run_button = st.button("🚀 Start Research", use_container_width=True, type="primary")

    st.divider()
    st.caption(
        "**Pipeline:** Planner → Researcher → Analyzer → Writer\n\n"
        "The researcher may loop back to the planner if insufficient data is collected."
    )


# ── Main content ─────────────────────────────────────────────────
if run_button:
    if not topic.strip():
        st.error("⚠️ Please enter a research topic.")
        st.stop()

    blog_urls = [u.strip() for u in blog_urls_text.strip().split("\n") if u.strip()]

    # ── Progress tracking ────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📌 Topic", topic[:40] + "..." if len(topic) > 40 else topic)
    with col2:
        st.metric("📄 Blog URLs", len(blog_urls))
    with col3:
        st.metric("🔄 Max Iterations", max_iterations)

    st.divider()

    # Run the pipeline with status updates
    progress = st.progress(0, text="Initializing research pipeline...")

    status_container = st.container()

    with st.spinner("🔬 Research in progress..."):
        try:
            # Build graph and run step by step for progress updates
            app = build_graph()

            initial_state = {
                "topic": topic,
                "blog_urls": blog_urls,
                "sources": [],
                "errors": [],
                "messages": [],
                "iteration": 0,
                "max_iterations": max_iterations,
                "enough_data": False,
                "analysis": "",
                "report": "",
            }

            # Stream events for real-time progress
            final_state = None
            node_progress = {
                "planner": 0.20,
                "researcher": 0.50,
                "analyzer": 0.75,
                "writer": 0.95,
            }

            for event in app.stream(initial_state, stream_mode="updates"):
                for node_name, node_output in event.items():
                    pct = node_progress.get(node_name, 0.5)
                    labels = {
                        "planner": "📋 Planning research strategy...",
                        "researcher": "🔍 Collecting data from sources...",
                        "analyzer": "🔬 Analyzing collected research...",
                        "writer": "📝 Writing research report...",
                    }
                    progress.progress(pct, text=labels.get(node_name, f"Running {node_name}..."))

                    # Show messages from nodes
                    msgs = node_output.get("messages", [])
                    if msgs:
                        with status_container:
                            for msg in msgs:
                                st.markdown(f'<div class="status-card">{msg}</div>', unsafe_allow_html=True)

                    final_state = node_output

            progress.progress(1.0, text="✅ Research complete!")

            # Get the full final state by re-invoking (stream only gives deltas)
            # Use the last state from streaming
            full_state = app.invoke(initial_state)

        except Exception as e:
            st.error(f"❌ Research pipeline failed: {e}")
            st.exception(e)
            st.stop()

    st.divider()

    # ── Display results ──────────────────────────────────────────
    report = full_state.get("report", "")
    sources = full_state.get("sources", [])
    errors = full_state.get("errors", [])

    if report:
        st.subheader("📄 Research Report")
        st.markdown(f'<div class="report-container">', unsafe_allow_html=True)
        st.markdown(report)
        st.markdown('</div>', unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=report,
            file_name=f"research_report_{topic[:30].replace(' ', '_')}.md",
            mime="text/markdown",
        )
    else:
        st.warning("⚠️ No report was generated.")

    # ── Sources panel ────────────────────────────────────────────
    with st.expander(f"📚 Sources Used ({len(sources)})", expanded=False):
        for i, source in enumerate(sources, 1):
            source_type = source.get("source_type", "unknown")
            title = source.get("title", "Untitled")
            url = source.get("url", "")
            word_count = source.get("word_count", 0)
            st.markdown(
                f"**{i}.** [{title}]({url}) "
                f'<span class="source-badge">{source_type}</span> '
                f"({word_count} words)",
                unsafe_allow_html=True,
            )

    # ── Errors panel ─────────────────────────────────────────────
    if errors:
        with st.expander(f"⚠️ Errors ({len(errors)})", expanded=False):
            for err in errors:
                st.warning(err)

else:
    # ── Landing state ────────────────────────────────────────────
    st.markdown("### 👋 Welcome!")
    st.markdown(
        "Enter a **research topic** in the sidebar and optionally add **blog URLs** "
        "to include as sources. Click **Start Research** to begin.\n\n"
        "**How it works:**"
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("#### 📋 Plan\nThe planner generates sub-questions and search queries")
    with col2:
        st.markdown("#### 🔍 Research\nThe researcher searches the web and scrapes blogs")
    with col3:
        st.markdown("#### 🔬 Analyze\nThe analyzer synthesizes findings across sources")
    with col4:
        st.markdown("#### 📝 Report\nThe writer produces a polished markdown report")
