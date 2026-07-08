"""
Streamlit frontend for the Multi-Agent AI Research Assistant.

Run locally on your PC:
    streamlit run app.py

The backend runs on Google Colab with a local LLM.
Set the ngrok URL in the sidebar to connect.
"""

import os
import streamlit as st
import requests
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Multi-Agent AI Research Assistant",
    page_icon=":mag:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar — ngrok URL + branding + system info
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title(":mag: Research Assistant")

    # ngrok URL input — paste your Colab ngrok URL here
    ngrok_url = st.text_input(
        "Backend URL (ngrok)",
        value=os.getenv("API_URL", "https://transgressive-archimedes-vixenly.ngrok-free.dev"),
        help="Your Colab ngrok URL is already filled. Change only if you get a new one.",
        key="api_url_input",
    )
    API_URL = ngrok_url.rstrip("/")

    st.divider()
    st.markdown(
        "An agentic system that automates market research, competitive "
        "intelligence, customer insights, product strategy, and business "
        "analysis for any AI product idea."
    )
    st.markdown(
        "**Architecture:**\n"
        "- Backend: Google Colab (local LLM via Ollama)\n"
        "- LLM: Qwen2.5-7B-Instruct (free, no API key)\n"
        "- Frontend: This Streamlit app (your PC)\n"
        "- Connection: ngrok tunnel"
    )
    st.divider()
    st.markdown("### Pipeline")
    st.markdown(
        "1. **Market Research Specialist**\n"
        "2. **Competitive Intelligence Analyst**\n"
        "3. **Customer Insights Researcher**\n"
        "4. **Product Strategy Advisor**\n"
        "5. **Business Analyst** (final report)"
    )
    st.divider()

    # Backend status check
    st.markdown(f"### Backend\n`{API_URL}`")
    try:
        health = requests.get(f"{API_URL}/", timeout=10).json()
        st.success(f"Status: {health.get('status', 'unknown')}")
        llm_info = health.get("llm", {})
        if llm_info:
            st.caption(f"LLM: {llm_info.get('model', 'unknown')}")
            st.caption(f"Provider: {llm_info.get('provider', 'unknown')}")
    except requests.exceptions.ConnectionError:
        st.error(
            "Backend not reachable!\n\n"
            "1. Make sure Google Colab is running\n"
            "2. Check the ngrok URL is correct\n"
            "3. Make sure ngrok tunnel is active in Colab"
        )
    except Exception as e:
        st.warning(f"Backend check failed: {e}")


# ---------------------------------------------------------------------------
# Main panel — input + output
# ---------------------------------------------------------------------------
st.title("Multi-Agent AI Research Assistant")
st.markdown(
    "Enter an AI product idea below. Five specialized CrewAI agents will "
    "research it sequentially and produce a business analysis report. "
    "The LLM runs locally on Google Colab — completely free, no API key needed."
)

default_idea = "an AI-powered resume builder for fresh graduates"
product_idea = st.text_input(
    "AI product idea",
    value=default_idea,
    help="Describe the product you want researched. Be specific about the "
    "target user, problem, and any industry context.",
)

col1, col2 = st.columns([1, 5])
with col1:
    generate = st.button(":rocket: Generate Report", type="primary", use_container_width=True)
with col2:
    verbose = st.checkbox("Verbose agent logs (in Colab console)")

# ---------------------------------------------------------------------------
# Run pipeline
# ---------------------------------------------------------------------------
if generate:
    if not product_idea.strip():
        st.error("Please enter a product idea first.")
        st.stop()

    if not API_URL:
        st.error("Please enter the backend URL (ngrok URL) in the sidebar.")
        st.stop()

    with st.status("Running 5-agent research pipeline on local LLM...", expanded=True) as status:
        st.write(":hourglass: Connecting to Colab backend...")
        try:
            resp = requests.post(
                f"{API_URL}/generate-report",
                json={"product_idea": product_idea, "verbose": verbose},
                timeout=900,  # 15 min — local LLM is slower than API
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            st.error(
                f"Could not reach backend at {API_URL}.\n\n"
                f"Steps to fix:\n"
                f"1. Open Google Colab\n"
                f"2. Run all cells (Ollama + backend + ngrok)\n"
                f"3. Copy the ngrok URL from Colab output\n"
                f"4. Paste it in the sidebar above"
            )
            st.stop()
        except requests.exceptions.HTTPError as e:
            st.error(f"Backend error: {e}\n\n{resp.text}")
            st.stop()
        except requests.exceptions.Timeout:
            st.error(
                "Request timed out after 15 minutes.\n\n"
                "The local LLM may be slow. Try again or check Colab logs."
            )
            st.stop()

        st.write(":white_check_mark: Pipeline complete.")
        status.update(label="Report ready!", state="complete", expanded=False)

    # Cache the result in session_state so tab switches don't lose it
    st.session_state["last_result"] = data

# ---------------------------------------------------------------------------
# Render results
# ---------------------------------------------------------------------------
if "last_result" in st.session_state:
    data = st.session_state["last_result"]

    st.divider()
    st.subheader("Reports")

    tabs = st.tabs(
        [
            "Final Business Report",
            "1. Market Research",
            "2. Competitive Intelligence",
            "3. Customer Insights",
            "4. Product Strategy",
            "5. Business Analysis",
        ]
    )

    sections = [
        ("final_report", "Final Business Report"),
        ("market_research", "Market Research"),
        ("competitive_intelligence", "Competitive Intelligence"),
        ("customer_insights", "Customer Insights"),
        ("product_strategy", "Product Strategy"),
        ("business_analysis", "Business Analysis"),
    ]

    for tab, (key, label) in zip(tabs, sections):
        with tab:
            content = data.get(key, "")
            if not content:
                st.info(f"No content for {label}.")
                continue
            st.markdown(content)
            st.divider()
            filename = f"{key}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
            st.download_button(
                label=f":arrow_down: Download {label} (.md)",
                data=content.encode("utf-8"),
                file_name=filename,
                mime="text/markdown",
                key=f"dl_{key}",
            )

    # Footer with metadata
    st.divider()
    with st.expander("Run metadata"):
        st.json(
            {
                "product_idea": data.get("product_idea"),
                "generated_at": data.get("generated_at"),
                "output_path": data.get("output_path"),
            }
        )
else:
    st.info("Enter a product idea above and click **Generate Report** to start.")