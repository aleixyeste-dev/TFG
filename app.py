import streamlit as st
from game_logic import (
    cargar_estructura_proyecto,
    generar_diccionario_agrupaciones,
    inicializar_juego,
    siguiente_ronda
)
from db import init_db, get_estado, save_estado

st.set_page_config(layout="wide")
st.title("🧠 BIVRA – Partida compartida")

# -----------------------
# Inicializar base de datos
# -----------------------
init_db()

# -----------------------
# Cargar datos del juego
# -----------------------
@st.cache_data
def cargar_datos():
    return cargar_estructura_proyecto(), generar_diccionario_agrupaciones()

estructura, agrupaciones = cargar_datos()

# -----------------------
# Cargar o crear partida
# -----------------------
estado = get_estado()

if estado is None:
    estado = inicializar_juego()
    save_estado(estado)

# -----------------------
# Info general
# -----------------------
st.subheader(f"Ronda {estado['ronda']}")

if estado["finalizado"]:
    st.success("🏆 Proyecto completado – Fin de la partida")

# -----------------------
# Botón siguiente ronda
# -----------------------
if not estado["finalizado"]:
    if st.button("▶️ Siguiente ronda (acción compartida)"):
        estado, eventos = siguiente_ronda(estado, estructura, agrupaciones)
        save_estado(estado)
        for e in eventos:
            st.info(e)

st.markdown("---")

# -----------------------
# Mostrar equipos
# -----------------------
col1, col2 = st.columns(2)

def mostrar_equipo(col, equipo):
    col.subheader(f"Equipo {equipo}")
    mazo = estado["mazos"][equipo]

    if not mazo:
        col.info("Sin cartas")
        return

    filas = [mazo[i:i+6] for i in range(0, len(mazo), 6)]
    for fila in filas:
        cols = col.columns(len(fila))
        for c, carta in zip(cols, fila):
            c.image(carta, width=140)

mostrar_equipo(col1, 1)
mostrar_equipo(col2, 2)

# -----------------------
# Reset compartido
# -----------------------
st.markdown("---")
if st.button("🔄 Reiniciar partida (para todos)"):
    estado = inicializar_juego()
    save_estado(estado)
    st.experimental_rerun()
