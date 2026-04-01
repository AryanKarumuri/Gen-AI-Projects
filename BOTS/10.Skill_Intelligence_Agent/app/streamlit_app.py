import sys
from pathlib import Path

# Add project root to path so 'app' can be imported
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from app.services.engine import run_engine

st.set_page_config(page_title="Skill Intelligence Engine", page_icon="🧠", layout="wide")

st.title("🧠 Skill Intelligence Engine")
st.markdown("Extract relevant skills, libraries, and tools for any topic using AI-powered web search and analysis.")

# Input section
col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "Enter your query:",
        placeholder="e.g., Python data science libraries, JavaScript web frameworks",
        help="Describe the topic you want to find skills for"
    )

with col2:
    num_results = st.slider(
        "Search results to analyze:",
        min_value=10,
        max_value=50,
        value=10,
        step=5,
        help="More results = more comprehensive analysis but slower processing"
    )

# Run button
if st.button("🔍 Extract Skills", type="primary", use_container_width=True):
    if not query.strip():
        st.error("Please enter a query first!")
    else:
        with st.spinner("Searching and analyzing... This may take a few moments."):
            try:
                result = run_engine(query.strip(), num_results=num_results)

                # Check for parse error
                if "parse_error" in result:
                    st.error("❌ Analysis failed: " + result["parse_error"])
                    with st.expander("🔧 Raw AI Response"):
                        st.code(result.get("raw_response", ""), language="json")
                else:
                    # Summary — always visible
                    if query in result:
                        st.success("✅ Analysis complete!")
                        st.info(result[query])

                    # Skills — collapsed by default
                    if "Relevant Skills" in result and result["Relevant Skills"]:
                        with st.expander("🛠️ Relevant Skills", expanded=False):
                            skills = result["Relevant Skills"]
                            cols = st.columns(2)
                            for i, (skill_name, description) in enumerate(skills.items()):
                                with cols[i % 2]:
                                    st.markdown(f"**{skill_name}**")
                                    st.caption(description)

                    # Skill names — compact one-liner
                    if "Skill Names Only" in result and result["Skill Names Only"]:
                        st.markdown("**📋 Skills:** " + ", ".join(result["Skill Names Only"]))

                    # Sources — collapsed by default
                    if "Sources" in result and result["Sources"]:
                        with st.expander("🔗 Sources", expanded=False):
                            for url in result["Sources"]:
                                st.markdown(f"- [{url}]({url})")

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("Try again or check your internet connection and API endpoints.")

st.caption("*Powered by SearXNG, Ollama & LangChain*")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    AI-powered skill extraction:
    - **Search:** SearXNG
    - **LLM:** Ollama + LangChain
    """)
