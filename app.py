import streamlit as st

from game_logic import (
    inicializar_juego,
    siguiente_ronda,
    cargar_estructura_proyecto,
    generar_diccionario_agrupaciones
)
# ---------------------------------
# CONFIGURACIÓN
# ---------------------------------
st.set_page_config(
    page_title="BIVRA – Partida compartida",
    layout="wide",
)

st.title("🧠 BIVRA – Partida compartida")

# ---------------------------------
# CARGA DE DATOS (una sola vez)
# ---------------------------------
@st.cache_data
def cargar_datos():
    estructura = cargar_estructura_proyecto()
    agrupaciones = generar_diccionario_agrupaciones(estructura)
    return estructura, agrupaciones

estructura, agrupaciones = cargar_datos()

# ---------------------------------
# ESTADO GLOBAL
# ---------------------------------
if "estado" not in st.session_state:
    st.session_state.estado = inicializar_juego()

estado = st.session_state.estado

# ---------------------------------
# ACCIONES
# ---------------------------------
col_a, col_b = st.columns(2)

with col_a:
    if st.button("▶️ Siguiente ronda (acción compartida)"):
        estado, eventos = siguiente_ronda(
            estado,
            estructura,
            agrupaciones
        )
        st.session_state.estado = estado
        st.rerun()

with col_b:
    if st.button("🔄 Reiniciar partida (para todos)"):
        st.session_state.estado = inicializar_juego()
        st.rerun()

# ---------------------------------
# VISUALIZACIÓN DE EQUIPOS
# ---------------------------------
def mostrar_equipo(col, equipo):
    with col:
        st.subheader(f"Equipo {equipo}")

        mazo = estado["mazos"].get(equipo, [])

        if not mazo:
            st.info("Sin cartas todavía")
            return

        for carta in mazo:
            st.image(carta, width=160)

col1, col2 = st.columns(2)
mostrar_equipo(col1, 1)
mostrar_equipo(col2, 2)

# ---------------------------------
# DEBUG
# ---------------------------------
with st.expander("ℹ️ Estado interno (debug)"):
    st.json(estado)

