import streamlit as st

from game_logic import (
    inicializar_juego,
    cargar_estructura_proyecto,
    siguiente_ronda
)

from db import load_estado, save_estado

# ===============================
# CONFIG STREAMLIT
# ===============================

st.set_page_config(page_title="BIVRA – Partida compartida", layout="wide")

# ===============================
# CARGA DE DATOS (CACHE)
# ===============================

@st.cache_data
def cargar_datos():
    estructura = cargar_estructura_proyecto()
    agrupaciones = None  # ya no se usa en esta versión
    return estructura, agrupaciones

estructura, agrupaciones = cargar_datos()

# ===============================
# CARGA / INICIALIZACIÓN ESTADO
# ===============================

estado = load_estado()
if estado is None:
    estado = inicializar_juego()
    save_estado(estado)

# ===============================
# ACCIONES GLOBALES
# ===============================

col_top1, col_top2 = st.columns([1, 3])

with col_top1:
    if st.button("▶️ Siguiente ronda (acción compartida)"):
        estado, eventos = siguiente_ronda(estado, estructura, agrupaciones)
        save_estado(estado)
        st.experimental_rerun()

with col_top2:
    if st.button("🔄 Reiniciar partida (para todos)"):
        estado = inicializar_juego()
        save_estado(estado)
        st.experimental_rerun()

st.divider()

# ===============================
# MOSTRAR EQUIPOS
# ===============================

col1, col2 = st.columns(2)


def mostrar_equipo(col, equipo):
    col.subheader(f"Equipo {equipo}")
    mazo = estado.get("mazos", {}).get(equipo, [])

    if not mazo:
        col.info("Sin cartas todavía")
        return

    cols = col.columns(4)
    for i, carta in enumerate(mazo):
        with cols[i % 4]:
            col.image(carta, width=160)


mostrar_equipo(col1, 1)
mostrar_equipo(col2, 2)

# ===============================
# INFO DEBUG (OPCIONAL)
# ===============================

with st.expander("ℹ️ Estado interno (debug)"):
    st.json(estado)

