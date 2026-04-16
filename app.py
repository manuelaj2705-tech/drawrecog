import os
import base64
import numpy as np
from PIL import Image
import openai
import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Tablero Inteligente", page_icon="✏️", layout="wide")

st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 2rem 3rem; }

    /* Título */
    .hero { padding: 1.2rem 0 1.8rem; border-bottom: 1px solid #ececec; margin-bottom: 1.5rem; }
    .hero-tag {
        display: inline-block;
        background: #EEEDFE; color: #3C3489;
        font-size: 11px; font-weight: 600;
        letter-spacing: 0.06em; text-transform: uppercase;
        padding: 3px 12px; border-radius: 99px;
        margin-bottom: 10px;
    }
    .hero-title { font-size: 2.2rem; font-weight: 700; color: #111; line-height: 1.1; margin: 0 0 6px; }
    .hero-sub { font-size: 1rem; color: #888; margin: 0; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background: #f7f7f5 !important; }
    section[data-testid="stSidebar"] .stMarkdown p { font-size: 0.85rem; }

    /* Etiquetas de sección */
    .sec-label {
        font-size: 0.72rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.08em;
        color: #bbb; margin: 1.2rem 0 0.5rem;
    }

    /* Paleta de colores */
    .palette { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 0.5rem; }
    .swatch {
        width: 30px; height: 30px; border-radius: 50%;
        border: 2.5px solid transparent; cursor: pointer;
        transition: transform 0.1s;
    }
    .swatch:hover { transform: scale(1.15); }

    /* Resultado */
    .resultado {
        background: #f4f4f4; border-radius: 12px;
        padding: 1.2rem 1.5rem; font-size: 0.97rem;
        color: #333; line-height: 1.75; margin-top: 0.8rem;
    }

    /* Botón analizar */
    div.stButton > button {
        background: #111; color: #fff;
        border: none; border-radius: 10px;
        padding: 0.65rem 1.5rem; font-size: 0.95rem;
        font-weight: 600; width: 100%;
        transition: background 0.2s;
    }
    div.stButton > button:hover { background: #333; }

    /* Input */
    .stTextInput input {
        border-radius: 8px; border: 1px solid #ddd;
        font-size: 0.9rem; background: #fff;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">✨ IA Visual</div>
    <h1 class="hero-title">Tablero inteligente</h1>
    <p class="hero-sub">Dibuja un boceto y la inteligencia artificial lo describirá en español.</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✏️ Herramientas")
    st.markdown("---")

    st.markdown('<p class="sec-label">Color del lápiz</p>', unsafe_allow_html=True)

    colores = {
        "Negro":    "#111111",
        "Rojo":     "#E24B4A",
        "Azul":     "#378ADD",
        "Verde":    "#1D9E75",
        "Naranja":  "#EF9F27",
        "Morado":   "#7F77DD",
        "Rosa":     "#D4537E",
        "Coral":    "#D85A30",
        "Gris":     "#888780",
    }

    opciones = list(colores.keys())
    color_elegido = st.radio(
        "Color",
        opciones,
        index=0,
        label_visibility="collapsed",
        format_func=lambda c: f"{'⬤'} {c}",
    )
    stroke_color = colores[color_elegido]

    st.markdown('<p class="sec-label">Color personalizado</p>', unsafe_allow_html=True)
    custom_color = st.color_picker("Elige un color", value=stroke_color, label_visibility="collapsed")
    if custom_color != stroke_color:
        stroke_color = custom_color

    st.markdown('<p class="sec-label">Grosor del trazo</p>', unsafe_allow_html=True)
    stroke_width = st.slider("Grosor", 1, 30, 5, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Cómo usar:**")
    st.markdown(
        "1. Elige el color del lápiz.\n"
        "2. Ajusta el grosor.\n"
        "3. Dibuja en el lienzo.\n"
        "4. Ingresa tu API key.\n"
        "5. Presiona **Analizar**."
    )
    st.markdown("---")
    st.caption("Modelo: GPT-4o mini · OpenAI")

# ── Canvas ────────────────────────────────────────────────────────────────────
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.0)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color="#FFFFFF",
    height=360,
    drawing_mode="freedraw",
    key="canvas",
)

# ── API key + botón ───────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    ke = st.text_input("API key de OpenAI", type="password", placeholder="sk-...", label_visibility="visible")
with col2:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    analyze = st.button("Analizar imagen")

os.environ["OPENAI_API_KEY"] = ke


def encode_image(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return ""


# ── Análisis ──────────────────────────────────────────────────────────────────
if analyze:
    if not ke:
        st.warning("⚠️ Ingresa tu API key para continuar.")
    elif canvas_result.image_data is None:
        st.warning("⚠️ Dibuja algo en el lienzo primero.")
    else:
        with st.spinner("Analizando tu boceto con IA..."):
            arr = np.array(canvas_result.image_data)
            img = Image.fromarray(arr.astype("uint8"), "RGBA")
            img.save("img.png")
            b64 = encode_image("img.png")

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe en español brevemente lo que ves en esta imagen."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                        ],
                    }],
                    max_tokens=500,
                )
                descripcion = response.choices[0].message.content or ""
                st.markdown(
                    f'<div class="resultado">🖼️ {descripcion}</div>',
                    unsafe_allow_html=True,
                )
                st.session_state["mi_respuesta"] = descripcion

            except Exception as e:
                st.error(f"Error al conectar con la API: {e}")
