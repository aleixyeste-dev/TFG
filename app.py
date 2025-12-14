import streamlit as st

from game_logic import (
    inicializar_juego,
    siguiente_ronda,
    cargar_estructura_proyecto,
    generar_diccionario_agrupaciones,
)

from db import load_estado, save_estado


# -------------------------------
# CONFIGURACIÓN STREAMLIT
# -------------------------------
st.set_page_config(
    page_title="BIVRA – Partida compartida",
    layout="wide",
)


# -------------------------------
# CARGA DE DATOS (CACHE)
# -------------------------------
@st.cache_data
def cargar_datos_cache():
    estructura = cargar_estructura_proyecto()
    agrupaciones = generar_diccionario_agrupaciones()
    return estructura, agrupaciones


estructura, agrupaciones = cargar_datos_cache()


# -------------------------------
# CARGA / INICIALIZACIÓN DE ESTADO
# -------------------------------
estado = load_estado()
if estado is None:
    estado = inicializar_juego()
    save_estado(estado)


# -------------------------------
# TÍTULO
# -------------------------------
st.title("🧠 BIVRA – Partida compartida")


# -------------------------------
# BOTONES DE CONTROL
# -------------------------------
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("▶️ Siguiente ronda (acción compartida)"):
        estado, eventos = siguiente_ronda(estado, estructura, agrupaciones)
        save_estado(estado)
        st.rerun()

with col_btn2:
    if st.button("🔄 Reiniciar partida (para todos)"):
        estado = inicializar_juego()
        save_estado(estado)
        st.rerun()


st.divider()


# -------------------------------
# FUNCIÓN PARA MOSTRAR EQUIPOS
# -------------------------------
def mostrar_equipo(col, equipo):
    col.subheader(f"Equipo {equipo}")

    mazo = estado["mazos"].get(str(equipo), [])

    if not mazo:
        col.info("Sin cartas todavía")
        return

    for carta in mazo:
        col.image(carta, width=140)


# -------------------------------
# VISUALIZACIÓN DE EQUIPOS
# -------------------------------
col1, col2 = st.columns(2)

mostrar_equipo(col1, 1)
mostrar_equipo(col2, 2)


# -------------------------------
# DEBUG
# -------------------------------
with st.expander("ℹ️ Estado interno (debug)"):
    st.json(estado)
