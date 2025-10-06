def ask_gpt_category(text):
    prompt = f"""
Clasifica este bloque de texto en una de las siguientes categorías, según las reglas de colores:
ROJO=Títulos, ROSA=Subtítulos/Subtemas, AMARILLO=Conceptos, CELESTE=Información importante/difícil de memorizar, VERDE=Clasificaciones/ítems/ejemplos, NARANJA=Datos numéricos, fórmulas, nombres de autores/leyes

Texto: \"\"\"{text}\"\"\"

Devuelve solo el nombre de la categoría (ROJO, ROSA, AMARILLO, CELESTE, VERDE, NARANJA)
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user", "content": prompt}],
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
