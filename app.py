"""
PaperLens — Scientific Paper Summarizer
Powered by LivAI · Built for LLNL

Deploy to Streamlit Community Cloud:
  1. Push this repo to GitHub
  2. Go to share.streamlit.io
  3. Connect repo → deploy
  4. Open the URL on any device
"""

import io
import requests
import streamlit as st

# ── PDF extraction ────────────────────────────────────────────────────────────
try:
    import pypdf
    def extract_pdf_text(file_bytes: bytes) -> tuple[str, int]:
        """Extract text from PDF bytes. Returns (text, page_count)."""
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages = []
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"--- Page {i} ---\n{text}")
        return "\n\n".join(pages), len(reader.pages)
except ImportError:
    st.error("pypdf not installed. Run: pip install pypdf")
    st.stop()

# ── Constants ─────────────────────────────────────────────────────────────────
LIVAI_URL  = "https://livai-api.llnl.gov/v1/chat/completions"
MAX_CHARS  = 80_000   # ~60k tokens — context window safety

SYSTEM = """You are an expert scientific paper summarizer. Produce a structured, \
scientifically precise summary for a domain-literate scientist — \
Nature News & Views style: authoritative, concise, zero padding.

Use EXACTLY this Markdown structure:

## [Full paper title]
*[First Author et al., Journal, Vol, Pages (Year)]*
**DOI:** [linked DOI if available]

### Science background
- Problem and why it matters
- Core mechanism with key equations inline (e.g. ΔE = hν)
- Essential terminology (define acronyms at first use)

### Methods
- Platform, instrument, or system used
- Measurement/analysis approach; key innovations
- Limitations the paper explicitly notes

### Main results
- Primary findings — lead every bullet with numbers
- Comparison to prior work, models, or simulations
- Caveats and unresolved issues

### Key references
4–6 central references:
Author et al., *Journal* Vol, Page (Year) — [doi link]

Style: state science directly, never "this paper shows…". \
Lead with numbers. Peer-to-peer tone between scientists."""

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "PaperLens",
    page_icon  = "🔬",
    layout     = "centered",
    initial_sidebar_state = "expanded",
)

# ── Mobile-first CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* ── Hide Streamlit chrome on mobile ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Top padding reduction for mobile ── */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 720px !important;
}

/* ── App header bar ── */
.app-header {
    background: #001e62;
    color: white;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}
.app-header h1 {
    margin: 0;
    font-size: 1.3rem;
    font-weight: 700;
    color: white;
}
.app-header .pill {
    margin-left: auto;
    background: #fcb317;
    color: #001e62;
    font-size: 0.65rem;
    font-weight: 800;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}

/* ── Result box ── */
.result-box {
    background: #f4f7ff;
    border-left: 4px solid #0032a1;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-top: 0.75rem;
    line-height: 1.75;
    font-size: 0.92rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #f8f9ff;
    border-right: 1px solid #dde6ff;
}
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #001e62;
    font-size: 1rem;
}

/* ── Buttons — bigger tap targets for mobile ── */
.stButton > button {
    width: 100%;
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
}

/* ── File uploader — larger touch zone ── */
[data-testid="stFileUploader"] {
    border-radius: 12px;
}
[data-testid="stFileUploaderDropzone"] {
    padding: 2rem !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <span style="font-size:1.6rem">🔬</span>
  <h1>PaperLens</h1>
  <span class="pill">LivAI</span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar — credentials ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ LivAI Config")
    st.caption("Your key is used only for this session and never stored.")

    api_key = st.text_input(
        "API key",
        type        = "password",
        placeholder = "your LivAI token",
    )
    model = st.text_input(
        "Model",
        value       = "claude-sonnet-4-6",
        placeholder = "e.g. claude-sonnet-4-6",
    )

    if api_key:
        st.success("Key set ✓")
    else:
        st.warning("Enter your LivAI API key")

    st.divider()
    st.caption(
        "PDF text is extracted on the server before being sent to LivAI. "
        "Only plain text leaves this app."
    )

# ── Main — two tabs ───────────────────────────────────────────────────────────
tab_pdf, tab_url = st.tabs(["📄  Upload PDF", "🔗  Paper URL"])

def run_summary(user_msg: str) -> str | None:
    """Validate config, call LivAI, return markdown summary or None on error."""
    if not api_key:
        st.error("Enter your LivAI API key in the sidebar ←")
        return None
    if not model:
        st.error("Enter the model name in the sidebar ←")
        return None

    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model":      model,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": user_msg},
        ],
    }

    try:
        resp = requests.post(LIVAI_URL, headers=headers, json=payload, timeout=120)
    except requests.exceptions.ConnectionError:
        st.error(
            "❌ Cannot reach LivAI. "
            "Make sure you're on the LLNL network or connected to VPN."
        )
        return None

    if resp.status_code == 401:
        st.error("❌ Invalid API key — check your LivAI token.")
        return None
    if resp.status_code == 403:
        st.error("❌ Access denied — check your LivAI permissions.")
        return None
    if resp.status_code == 429:
        st.error("❌ Rate limit hit — wait a moment and retry.")
        return None
    if not resp.ok:
        detail = resp.json().get("error", {}).get("message", resp.text)
        st.error(f"❌ LivAI error {resp.status_code}: {detail}")
        return None

    content = resp.json()["choices"][0]["message"]["content"]
    if not content:
        st.error("❌ Empty response — check model name.")
        return None

    return content

# ── Tab 1: PDF upload ─────────────────────────────────────────────────────────
with tab_pdf:
    uploaded = st.file_uploader(
        "Drag a PDF here, or tap to browse",
        type             = ["pdf"],
        label_visibility = "collapsed",
    )

    if uploaded:
        size_mb = uploaded.size / 1024 / 1024
        st.info(f"**{uploaded.name}** · {size_mb:.1f} MB loaded")

    if st.button("✦  Summarize PDF", type="primary",
                 disabled=not uploaded, key="btn_pdf"):
        with st.spinner("Extracting text from PDF…"):
            try:
                text, n_pages = extract_pdf_text(uploaded.read())
            except Exception as e:
                st.error(f"Could not read PDF: {e}")
                st.stop()

        if not text or len(text.strip()) < 100:
            st.error(
                "No readable text found. "
                "PDF may be image-only (scanned). Try an OCR tool first."
            )
            st.stop()

        if len(text) > MAX_CHARS:
            st.warning(
                f"Paper is large ({len(text):,} chars). "
                f"Using first {MAX_CHARS:,} characters."
            )
            text = text[:MAX_CHARS]

        user_msg = (
            f"Below is text extracted from a {n_pages}-page scientific paper. "
            "Summarize it using the structured format in your instructions. "
            "Lead every bullet with quantitative data.\n\n"
            f"--- PAPER TEXT ---\n{text}"
        )

        with st.spinner("Sending to LivAI…"):
            summary = run_summary(user_msg)

        if summary:
            st.success("Summary complete!")
            st.markdown(summary)
            st.download_button(
                label     = "⬇  Download summary (.md)",
                data      = summary,
                file_name = uploaded.name.replace(".pdf", "_summary.md"),
                mime      = "text/markdown",
            )

# ── Tab 2: URL ────────────────────────────────────────────────────────────────
with tab_url:
    st.caption(
        "Best for arXiv abstract pages. "
        "For paywalled journals, download and use the PDF tab."
    )
    url = st.text_input(
        "Paper URL",
        placeholder      = "https://arxiv.org/abs/2301.00001",
        label_visibility = "collapsed",
    )

    if st.button("✦  Summarize URL", type="primary",
                 disabled=not url, key="btn_url"):
        if not url.startswith("http"):
            st.error("Enter a URL starting with https://")
        else:
            user_msg = (
                f"Summarize the scientific paper at: {url}\n\n"
                "Use the structured format in your instructions. "
                "If the full text is unavailable, summarize from your knowledge "
                "and note that uploading the PDF gives a more complete result."
            )

            with st.spinner("Sending to LivAI…"):
                summary = run_summary(user_msg)

            if summary:
                st.success("Summary complete!")
                st.markdown(summary)
                st.download_button(
                    label     = "⬇  Download summary (.md)",
                    data      = summary,
                    file_name = "summary.md",
                    mime      = "text/markdown",
                )
