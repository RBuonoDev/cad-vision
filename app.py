from pathlib import Path
import re

import streamlit as st


st.set_page_config(page_title="3DE — Estúdio CAD", page_icon="🧊", layout="wide")

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp { background: #070c12; }
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], footer { display: none !important; }
    .block-container { max-width: none !important; padding: 0 !important; }
    [data-testid="stElementContainer"]:has(iframe) {
        width: 100vw !important; max-width: none !important;
    }
    iframe {
        display: block; border: 0; width: 100vw !important;
        min-width: 100vw !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

static_dir = Path(__file__).parent / "static" / "3de"
document = (static_dir / "index.html").read_text(encoding="utf-8")
runtime = (static_dir / "solidcraft-web-b255f1e00123e9da.js").read_text(encoding="utf-8")
styles = (static_dir / "loading-b2ddd872f1c0a1e5.css").read_text(encoding="utf-8")
module_start = document.index('<script type="module">') + len('<script type="module">')
module_end = document.index("</script>", module_start)
loader = document[module_start:module_end]
loader = loader.replace(
    "import init, * as bindings from './solidcraft-web-b255f1e00123e9da.js';",
    runtime + "\nconst init = __wbg_init; const bindings = {};",
)
document = document[:module_start] + loader + document[module_end:]
document = re.sub(
    r'<link rel="stylesheet" href="\./loading-[^"]+\.css"[^>]*>',
    f"<style>{styles}</style>",
    document,
    count=1,
)
document = document.replace("<head>", '<head><base href="app/static/3de/">', 1)
st.components.v1.html(document, width=1920, height=920, scrolling=False)
