import os
import streamlit as st
import base64
import openai
from openai import OpenAI
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title='🎨 Tablero Inteligente',
    page_icon='🎨',
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1f1c2c, #928dab);
    color: white;
}

/* Título */
.title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    animation: fadeIn 1.5s ease-in-out;
}

/* Animación */
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

/* Tarjeta */
.card {
    background-color: #2b2b2b;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 0px 25px rgba(0,0,0,0.4);
}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCIONES ----------------
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# ---------------- UI ----------------
st.markdown('<div class="title">🧠 Tablero Inteligente con IA</div>', unsafe_allow_html=True)
st.write("Dibuja algo y deja que la IA lo interprete ✨")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Configuración")

    st.subheader("🖌️ Dibujo")
    stroke_width = st.slider('Grosor', 1, 30, 5)

    st.subheader("🔐 API")
    api_key = st.text_input('Ingresa tu API Key', type="password")

# ---------------- CANVAS ----------------
col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=300,
        width=400,
        drawing_mode="freedraw",
        key="canvas",
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BOTÓN ----------------
analyze_button = st.button("🔍 Analizar dibujo")

# ---------------- PROCESAMIENTO ----------------
if canvas_result.image_data is not None and api_key and analyze_button:

    os.environ['OPENAI_API_KEY'] = api_key
    client = OpenAI(api_key=api_key)

    with st.spinner("🧠 Analizando imagen..."):
        try:
            # Convertir imagen
            input_array = np.array(canvas_result.image_data)
            image = Image.fromarray(input_array.astype('uint8'), 'RGBA')
            image.save('img.png')

            # Base64
            base64_image = encode_image_to_base64("img.png")

            prompt = "Describe en español brevemente el dibujo"

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )

            resultado = response.choices[0].message.content

            # Mostrar resultado bonito
            st.success("✅ Resultado:")
            st.markdown(f"### 🧾 {resultado}")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ---------------- VALIDACIONES ----------------
elif not api_key:
    st.warning("⚠️ Ingresa tu API Key para usar la IA")
