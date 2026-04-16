import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

Expert=" "
profile_imgenh=" "

# 🎨 Fuente bonita
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# 🎨 Título bonito centrado
st.markdown("""
<h1 style='text-align: center; font-family: "Fredoka", sans-serif; color: #6C63FF;'>
🧠✨ Tablero Inteligente
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style='text-align: center; font-size:18px;'>
Dibuja lo que quieras y deja que interpretemos tu creatividad 🎨
</p>
""", unsafe_allow_html=True)


def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# Streamlit config
st.set_page_config(page_title='Tablero Inteligente')

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("Esta aplicación permite que una IA interprete tus dibujos.")

    # 🎨 Personalización del marcador
    stroke_width = st.slider('Grosor del marcador', 1, 30, 5)
    stroke_color = st.color_picker("Color del marcador", "#000000")

st.subheader("Dibuja tu boceto y presiona el botón para analizarlo")

# Canvas config
drawing_mode = "freedraw"
bg_color = '#FFFFFF'

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,  # 👈 ahora es dinámico
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# API KEY
ke = st.text_input('Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=api_key)

analyze_button = st.button("Analiza la imagen", type="secondary")

# Procesamiento
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('img.png')
        
        base64_image = encode_image_to_base64("img.png")
        prompt_text = "Describe en español brevemente la imagen"

        try:
            full_response = ""
            message_placeholder = st.empty()

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

else:
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
