import base64
import os

import streamlit as st
from dotenv import load_dotenv

from functions import (
    create_vectorstore_from_texts,
    get_pdf_text,
    query_document,
)

load_dotenv()

APP_NAME = "Lumen"
APP_TAGLINE = "AI Document Intelligence"

st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-base: #0b0d17;
    --bg-elevated: #141826;
    --bg-card: rgba(20, 24, 38, 0.6);
    --border-soft: rgba(167, 139, 250, 0.18);
    --border-strong: rgba(167, 139, 250, 0.35);
    --accent-1: #a78bfa;
    --accent-2: #22d3ee;
    --accent-3: #f472b6;
    --text-primary: #e5e7eb;
    --text-muted: #9ca3af;
    --text-faint: #6b7280;
    --success: #34d399;
    --danger: #f87171;
}

html, body, [class*="css"], .stApp, .stMarkdown, .stTextInput, .stTextArea, .stButton {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background:
        radial-gradient(1200px 600px at 10% -10%, rgba(167, 139, 250, 0.15), transparent 60%),
        radial-gradient(1000px 500px at 110% 10%, rgba(34, 211, 238, 0.10), transparent 55%),
        radial-gradient(900px 700px at 50% 110%, rgba(244, 114, 182, 0.08), transparent 60%),
        var(--bg-base);
    color: var(--text-primary);
}

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1400px; }

/* ---------- HERO ---------- */
.hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.6rem;
    border-radius: 22px;
    border: 1px solid var(--border-soft);
    background: linear-gradient(135deg, rgba(167, 139, 250, 0.08), rgba(34, 211, 238, 0.05));
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 12px 40px -10px rgba(0, 0, 0, 0.55);
}
.hero-left { display: flex; align-items: center; gap: 1rem; }
.hero-logo {
    width: 56px; height: 56px;
    border-radius: 16px;
    display: grid; place-items: center;
    background: conic-gradient(from 200deg, #a78bfa, #22d3ee, #f472b6, #a78bfa);
    box-shadow: 0 0 30px rgba(167, 139, 250, 0.45), inset 0 0 0 2px rgba(11, 13, 23, 0.85);
    font-size: 26px; color: #ffffff;
    animation: spin 14s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.hero-title {
    font-size: 1.85rem; font-weight: 800; letter-spacing: -0.02em;
    background: linear-gradient(90deg, #ffffff 0%, #c4b5fd 40%, #67e8f9 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.hero-subtitle { color: var(--text-muted); font-size: 0.92rem; margin-top: 2px; letter-spacing: 0.02em; }
.hero-badge {
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.72rem; font-weight: 600;
    color: var(--accent-1);
    background: rgba(167, 139, 250, 0.10);
    border: 1px solid var(--border-soft);
    letter-spacing: 0.08em; text-transform: uppercase;
}

/* ---------- GLASS CARDS ---------- */
.glass {
    background: var(--bg-card);
    border: 1px solid var(--border-soft);
    border-radius: 18px;
    padding: 1.1rem 1.25rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 10px 30px -12px rgba(0, 0, 0, 0.5);
}
.glass + .glass { margin-top: 1rem; }
.section-label {
    font-size: 0.72rem; font-weight: 700;
    color: var(--accent-1);
    letter-spacing: 0.16em; text-transform: uppercase;
    margin-bottom: 0.6rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.section-label::before {
    content: ""; width: 6px; height: 6px; border-radius: 50%;
    background: var(--accent-1);
    box-shadow: 0 0 10px var(--accent-1);
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(20, 24, 38, 0.95), rgba(11, 13, 23, 0.95));
    border-right: 1px solid var(--border-soft);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }

/* ---------- INPUTS ---------- */
.stTextInput > div > div > input,
.stTextArea textarea {
    background: rgba(11, 13, 23, 0.6) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 12px !important;
    padding: 0.7rem 0.9rem !important;
    font-size: 0.92rem !important;
    transition: all 0.18s ease;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent-1) !important;
    box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.18) !important;
    outline: none !important;
}

/* ---------- FILE UPLOADER ---------- */
[data-testid="stFileUploader"] section {
    background: rgba(11, 13, 23, 0.5);
    border: 1.5px dashed var(--border-strong);
    border-radius: 14px;
    padding: 1.2rem;
    transition: all 0.2s ease;
}
[data-testid="stFileUploader"] section:hover {
    border-color: var(--accent-2);
    background: rgba(34, 211, 238, 0.04);
}
[data-testid="stFileUploader"] button {
    background: rgba(167, 139, 250, 0.12) !important;
    color: var(--accent-1) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
}

/* ---------- BUTTONS ---------- */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #a78bfa 0%, #22d3ee 100%) !important;
    color: #0b0d17 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.2rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em;
    transition: all 0.2s ease !important;
    box-shadow: 0 8px 24px -8px rgba(167, 139, 250, 0.5) !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 14px 32px -10px rgba(167, 139, 250, 0.7) !important;
    filter: brightness(1.08);
}
.stButton > button:active { transform: translateY(0); }

/* ---------- LABELS ---------- */
.stTextInput label, .stTextArea label, [data-testid="stFileUploader"] label {
    color: var(--text-muted) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em;
}

/* ---------- ALERTS ---------- */
.stAlert {
    border-radius: 12px !important;
    border: 1px solid var(--border-soft) !important;
    backdrop-filter: blur(8px);
}

/* ---------- DATAFRAME ---------- */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--border-soft);
}

/* ---------- SPINNER ---------- */
.stSpinner > div { border-top-color: var(--accent-1) !important; }

/* ---------- PDF FRAME ---------- */
.pdf-wrapper {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid var(--border-soft);
    box-shadow: 0 14px 40px -16px rgba(0, 0, 0, 0.7);
    background: #1a1d2a;
}
.pdf-wrapper iframe { display: block; border: 0; width: 100%; }

/* ---------- EMPTY STATE ---------- */
.empty-state {
    text-align: center;
    padding: 3.5rem 2rem;
    border-radius: 18px;
    border: 1px dashed var(--border-soft);
    background: var(--bg-card);
}
.empty-state .icon {
    font-size: 3rem;
    margin-bottom: 0.8rem;
    background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
}
.empty-state .title { font-size: 1.15rem; font-weight: 600; color: var(--text-primary); }
.empty-state .desc { color: var(--text-muted); font-size: 0.9rem; margin-top: 0.4rem; }

/* ---------- STATUS PILL ---------- */
.status-pill {
    display: inline-flex; align-items: center; gap: 0.45rem;
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 0.78rem; font-weight: 600;
    background: rgba(52, 211, 153, 0.12);
    border: 1px solid rgba(52, 211, 153, 0.3);
    color: var(--success);
}
.status-pill .dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 8px var(--success);
    animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

/* ---------- SIDEBAR FOOTER ---------- */
.sidebar-footer {
    margin-top: 2rem; padding-top: 1rem;
    border-top: 1px solid var(--border-soft);
    color: var(--text-faint); font-size: 0.75rem;
    text-align: center;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""


def render_hero():
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-left">
            <div class="hero-logo">✦</div>
            <div>
              <div class="hero-title">{APP_NAME}</div>
              <div class="hero-subtitle">{APP_TAGLINE} · Extract structured insight from any PDF</div>
            </div>
          </div>
          <div class="hero-badge">RAG · Groq · Llama 3.3</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1.2rem;">
              <div style="width:34px;height:34px;border-radius:10px;
                          background:conic-gradient(from 200deg,#a78bfa,#22d3ee,#f472b6,#a78bfa);
                          display:grid;place-items:center;font-size:16px;color:#fff;">✦</div>
              <div style="font-weight:700;font-size:1.05rem;letter-spacing:-0.01em;">Control Panel</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-label">Authentication</div>', unsafe_allow_html=True)
        st.text_input(
            "Groq API Key",
            type="password",
            key="api_key",
            placeholder="gsk_•••••••••••••••",
            help="Leave empty to use GROQ_API_KEY from your .env file.",
        )

        st.markdown('<div class="section-label" style="margin-top:1rem;">Upload Document</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drop a PDF here",
            type="pdf",
            label_visibility="collapsed",
        )

        st.markdown('<div class="section-label" style="margin-top:1rem;">Query</div>', unsafe_allow_html=True)
        query = st.text_area(
            "Extraction prompt",
            value="Give me the title, summary, publication year, and authors of the research paper.",
            height=130,
            key="query",
            label_visibility="collapsed",
        )

        run = st.button("✦  Extract Insights", use_container_width=True)

        st.markdown(
            f'<div class="sidebar-footer">{APP_NAME} v1.0 · powered by LangChain + Chroma</div>',
            unsafe_allow_html=True,
        )

        return uploaded_file, query, run


def display_pdf(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    base64_pdf = base64.b64encode(bytes_data).decode("utf-8")
    st.markdown(
        f"""
        <div class="pdf-wrapper">
          <iframe src="data:application/pdf;base64,{base64_pdf}"
                  height="820" type="application/pdf"></iframe>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state():
    st.markdown(
        """
        <div class="empty-state">
          <div class="icon">◈</div>
          <div class="title">No document loaded</div>
          <div class="desc">Upload a PDF from the sidebar to begin extracting structured insights.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    render_hero()
    uploaded_file, query, run = render_sidebar()

    left, right = st.columns([0.55, 0.45], gap="large")

    with left:
        st.markdown('<div class="section-label">Document Preview</div>', unsafe_allow_html=True)
        if uploaded_file is not None:
            display_pdf(uploaded_file)
        else:
            render_empty_state()

    with right:
        st.markdown('<div class="section-label">Extraction Results</div>', unsafe_allow_html=True)

        if uploaded_file is not None and "last_indexed" not in st.session_state.get("_meta", {"last_indexed": None}):
            pass

        if uploaded_file is not None:
            meta = st.session_state.setdefault("_meta", {})
            if meta.get("last_indexed") != uploaded_file.name:
                with st.spinner("Indexing document…"):
                    documents = get_pdf_text(uploaded_file)
                    st.session_state.vector_store = create_vectorstore_from_texts(
                        documents, file_name=uploaded_file.name
                    )
                    meta["last_indexed"] = uploaded_file.name

            st.markdown(
                f'<div class="status-pill"><span class="dot"></span>Indexed · {uploaded_file.name}</div>',
                unsafe_allow_html=True,
            )

        if run:
            effective_key = st.session_state.api_key or os.getenv("GROQ_API_KEY")
            if not effective_key:
                st.error("No Groq API key found. Set GROQ_API_KEY in .env or enter it in the sidebar.")
            elif "vector_store" not in st.session_state:
                st.warning("Upload a PDF before running extraction.")
            else:
                with st.spinner("Reasoning over document…"):
                    answer = query_document(
                        vectorstore=st.session_state.vector_store,
                        query=query,
                        api_key=effective_key,
                    )
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.dataframe(answer, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        elif uploaded_file is None:
            st.markdown(
                """
                <div class="empty-state" style="padding:2.5rem 1.5rem;">
                  <div class="icon">⟡</div>
                  <div class="title">Awaiting input</div>
                  <div class="desc">Results will appear here after extraction.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


main()
