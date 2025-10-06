import streamlit as st
import fitz  # PyMuPDF
import io
import openai
import os

# ----------------- CONFIG -----------------
st.set_page_config(page_title="IA Resaltador de Apuntes", layout="wide")
st.title("📘 IA para resaltar apuntes en PDF")
st.markdown("""
Sube tu PDF y la IA resaltará según tu código de colores:

🔴 **Rojo:** Títulos  
🌸 **Rosa:** Subtítulos / Subtemas  
💛 **Amarillo:** Conceptos  
💙 **Celeste:** Información importante o difícil de memorizar  
💚 **Verde:** Clasificaciones, ítems, ejemplos  
🧡 **Naranja:** Datos numéricos, leyes, fórmulas, autores
""")

# ----------------- CONFIGURAR OPENAI -----------------
if "OPENAI_API_KEY" not in os.environ:
    st.warning("⚠️ Necesitas configurar tu API Key de OpenAI en variables de entorno")
openai.api_key = os.getenv("OPENAI_API_KEY")

# ----------------- COLORES -----------------
COLOR_MAP = {
    "ROJO": (1, 0, 0),
    "ROSA": (1, 0.4, 0.8),
    "AMARILLO": (1, 0.93, 0.4),
    "CELESTE": (0.4, 0.8, 1),
    "VERDE": (0.4, 1, 0.6),
    "NARANJA": (1, 0.6, 0),
}

# ----------------- FUNCIONES -----------------
def ask_gpt_category(text):
    prompt = f"""
Clasifica este bloque de texto en una de las siguientes categorías, según las reglas de colores:
ROJO=Títulos, ROSA=Subtítulos/Subtemas, AMARILLO=Conceptos, CELESTE=Información importante/difícil de memorizar, VERDE=Clasificaciones/ítems/ejemplos, NARANJA=Datos numéricos, fórmulas, nombres de autores/leyes

Texto: \"\"\"{text}\"\"\"

Devuelve solo el nombre de la categoría (ROJO, ROSA, AMARILLO, CELESTE, VERDE, NARANJA)
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user", "content":prompt}],
            max_tokens=10,
            temperature=0
        )
        category = response.choices[0].message.content.strip().upper()
        if category not in COLOR_MAP:
            category = "CELESTE"
        return category
    except Exception as e:
        st.error(f"Error con GPT: {e}")
        return "CELESTE"

def highlight_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        for block in page.get_text("blocks"):
            text = block[4].strip()
            if not text:
                continue
            category = ask_gpt_category(text)
            color = COLOR_MAP[category]
            rect = fitz.Rect(block[:4])
            highlight = page.add_highlight_annot(rect)
            highlight.set_colors(stroke=color)
            highlight.update()
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()

# ----------------- INTERFAZ -----------------
uploaded = st.file_uploader("Sube tu PDF", type=["pdf"])
if uploaded:
    st.info("Procesando tu PDF con IA… esto puede tardar un poco ⏳")
    highlighted = highlight_pdf(uploaded.read())
    st.success("✅ PDF resaltado listo para descargar")
    st.download_button(
        "Descargar PDF resaltado",
        highlighted,
        file_name="resaltado.pdf",
        mime="application/pdf"
    )
