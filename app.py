import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# ── Página ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tablero Inteligente",
    page_icon="✏️",
    layout="centered",
)

# ── Estilos globales ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fondo y tipografía general */
    .main { background-color: #fafafa; }
    .block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 720px; }

    /* Ocultar elementos de Streamlit por defecto */
    #MainMenu, footer, header { visibility: hidden; }

    /* Título principal */
    .titulo { font-size: 2rem; font-weight: 600; color: #111; margin-bottom: 0.15rem; }
    .subtitulo { font-size: 1rem; color: #888; margin-bottom: 2rem; }

    /* Etiquetas de sección */
    .label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #aaa;
        margin-bottom: 0.4rem;
    }

    /* Tarjeta contenedora */
    .card {
        background: #fff;
        border: 1px solid #ececec;
        border-radius: 14px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1.2rem;
    }

    /* Resultado del análisis */
    .resultado {
        background: #f4f4f4;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        font-size: 1rem;
        color: #333;
        line-height: 1.7;
        margin-top: 1rem;
    }

    /* Botón principal */
    div.stButton > button {
        background-color: #111;
        color: #fff;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.8rem;
        font-size: 0.95rem;
        font-weight: 500;
        width: 100%;
        transition: background 0.2s;
        cursor: pointer;
    }
    div.stButton > button:hover { background-color: #333; }

    /* Slider */
    .stSlider > div > div > div { color: #111; }
    .stSlider [data-baseweb="slider"] { padding-top: 0.2rem; }

    /* Input de texto */
    .stTextInput input {
        border-radius: 8px;
        border: 1px solid #ddd;
        padding: 0.55rem 0.9rem;
        font-size: 0.95rem;
        background: #fff;
    }
    .stTextInput input:focus { border-color: #111; box-shadow: none; }
</style>
""", unsafe_allow_html=True)

# ── Encabezado ────────────────────────────────────────────────────────────────
st.markdown('<p class="titulo">✏️ Tablero inteligente</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitulo">Dibuja un boceto y la IA lo describirá en español.</p>',
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Acerca de")
    st.info(
        "Esta aplicación demuestra la capacidad de una IA para "
        "interpretar y describir bocetos dibujados a mano.",
        icon="ℹ️",
    )
    st.markdown("---")
    st.markdown("**Instrucciones**")
    st.markdown(
        "1. Ajusta el grosor del trazo.\n"
        "2. Dibuja tu boceto en el lienzo.\n"
        "3. Ingresa tu API key de OpenAI.\n"
        "4. Presiona **Analizar imagen**."
    )

# ── Controles del lienzo ──────────────────────────────────────────────────────
st.markdown('<p class="label">Grosor del trazo</p>', unsafe_allow_html=True)
stroke_width = st.slider("", min_value=1, max_value=30, value=5, label_visibility="collapsed")

# ── Canvas ────────────────────────────────────────────────────────────────────
st.markdown('<p class="label">Lienzo de dibujo</p>', unsafe_allow_html=True)
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color="#111111",
    background_color="#FFFFFF",
    height=320,
    width=660,
    drawing_mode="freedraw",
    key="canvas",
)

# ── API Key ───────────────────────────────────────────────────────────────────
st.markdown('<p class="label" style="margin-top:1.2rem">API key de OpenAI</p>', unsafe_allow_html=True)
ke = st.text_input("", type="password", placeholder="sk-...", label_visibility="collapsed")
os.environ["OPENAI_API_KEY"] = ke
api_key = ke

# ── Botón y análisis ──────────────────────────────────────────────────────────
st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
analyze_button = st.button("Analizar imagen")

def encode_image_to_base64(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return ""

if analyze_button:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu API key para continuar.")
    elif canvas_result.image_data is None:
        st.warning("⚠️ Dibuja algo en el lienzo primero.")
    else:
        with st.spinner("Analizando tu boceto..."):
            arr = np.array(canvas_result.image_data)
            img = Image.fromarray(arr.astype("uint8"), "RGBA")
            img.save("img.png")
            b64 = encode_image_to_base64("img.png")

            prompt = "Describe en español brevemente lo que ves en esta imagen."

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{b64}"},
                                },
                            ],
                        }
                    ],
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
