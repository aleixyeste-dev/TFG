import streamlit as st
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "imagenes")


from game_logic import (
    inicializar_juego,
    siguiente_ronda,
    cargar_estructura_proyecto,
    generar_diccionario_agrupaciones,
    fusiones_disponibles,
    aplicar_fusion,
    ejecutar_fusion,
    entregables_disponibles,
    ejecutar_entregable
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

        mazo = estado["mazos"].get(str(equipo), [])

        if not mazo:
            st.info("Sin cartas todavía")
            return

        for carta in mazo:
            st.image(carta, width=160)


def mostrar_fusiones(col, equipo):
    with col:
        st.subheader("Fusiones posibles")

        mazo = estado["mazos"].get(str(equipo), [])
        posibles = fusiones_disponibles(mazo)

        if not posibles:
            st.info("No hay cartas para fusionar")
            return

        for fusion in posibles:
            paquete_id = fusion["paquete"]

            if st.button(
                f"Fusionar Paquete {paquete_id}",
                key=f"fusion_{equipo}_{paquete_id}"
            ):
                nuevo_estado, ok = ejecutar_fusion(
                    estado,
                    equipo,
                    paquete_id
                )

                if ok:
                    st.session_state.estado = nuevo_estado
                    st.rerun()


import os

def mostrar_proyectos(col, equipo):
    with col:
        st.subheader("Paquetes completados")

        proyectos = estado["proyectos"].get(str(equipo), [])

        if not proyectos:
            st.info("Todavía no hay paquetes completados")
            return

        for ruta in proyectos:
            if isinstance(ruta, str) and os.path.exists(ruta):
                st.image(ruta, width=180)
            else:
                st.error(f"Imagen no encontrada: {ruta}")





def mostrar_entregables(col, equipo):
    with col:
        st.subheader("Entregables posibles")

        paquetes = estado["proyectos"].get(str(equipo), [])
        posibles = entregables_disponibles(paquetes)

        if not posibles:
            st.info("No hay entregables disponibles")
            return

        for entregable_id in posibles:
            if st.button(
                f"Crear Entregable {entregable_id}",
                key=f"entregable_{equipo}_{entregable_id}"
            ):
                nuevo_estado, ok = ejecutar_entregable(
                    estado,
                    equipo,
                    int(entregable_id)   # 👈 MUY IMPORTANTE
                )

                if ok:
                    st.session_state.estado = nuevo_estado
                    st.rerun()
                else:
                    st.warning("❌ No se cumplen los requisitos para este entregable")


def mostrar_entregables_creados(col, equipo):
    with col:
        st.subheader("📦 Entregables creados")

        entregables = estado.get("entregables", {}).get(str(equipo), [])

        if not entregables:
            st.info("No hay entregables creados todavía")
            return

        for ruta in entregables:
            if os.path.exists(ruta):
                st.image(ruta, width=180)
            else:
                st.error(f"Imagen no encontrada: {ruta}")



col1, col2 = st.columns(2)

mostrar_equipo(col1, 1)
mostrar_fusiones(col1, 1)
mostrar_proyectos(col1, 1)
mostrar_entregables_creados(col1, 1)

mostrar_equipo(col2, 2)
mostrar_fusiones(col2, 2)
mostrar_proyectos(col2, 2)
mostrar_entregables_creados(col2, 2)

# ---------------------------------
# DEBUG
# ---------------------------------
with st.expander("ℹ️ Estado interno (debug)"):
    st.json(estado)



