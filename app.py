import os

import streamlit as st

from game_logic import (
    cargar_estructura_proyecto,
    generar_diccionario_agrupaciones,
    inicializar_juego,
    siguiente_ronda,

    ejecutar_fusion_con_seleccion,
    ejecutar_entregable,
    ejecutar_proyecto,

    entregables_disponibles,
    proyectos_disponibles,
    proyecto_asignado,
    ruta_paquete,
    _extraer_id_carta,
    _normalizar_fusiones,

    cargar_partida,
    guardar_partida,
    crear_partida_si_no_existe,
    existe_partida,
)


st.set_page_config(
    page_icon="🧠",
    page_title="🧠 BIVRA – Partida compartida",
    layout="wide",
    initial_sidebar_state="expanded",
)

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def abs_path(ruta_relativa: str) -> str:
    p = Path(ruta_relativa)
    if p.is_absolute():
        return str(p)
    return str((BASE_DIR / p).resolve())


def mostrar_fin_partida(estado: dict):
    if estado.get("finalizado", False):
        ganador = estado.get("ganador", "?")
        st.success(f"🏆 Partida finalizada. ¡Gana el Equipo {ganador}!")

def bloquear_si_finalizado(estado: dict):
    if estado.get("finalizado", False):
        mostrar_fin_partida(estado)
        st.stop()
# ---------------------------------
# ESTADO GLOBAL (ANTES de leer estado)
# ---------------------------------
# ---------------------------------
# SIDEBAR: Crear / Unirse
# ---------------------------------
def codigo_valido(c: str) -> bool:
    c = c.strip().upper()
    return len(c) >= 4 and c.isalnum()

with st.sidebar:
    st.header("🎮 Partidas")
    codigo = st.text_input(
        "Código de partida",
        value=st.session_state.get("codigo", ""),
        placeholder="Ej: ABC123",
        key="codigo_sidebar",
    ).strip().upper()

    equipo = st.radio("Tu equipo", [1, 2], index=0, key="equipo_sidebar")

    colA, colB = st.columns(2)
    crear = colA.button("Crear")
    unirse = colB.button("Unirse")

    if crear:
        if not codigo_valido(codigo):
            st.error("Código inválido (mínimo 4 caracteres alfanuméricos).")
        else:
            crear_partida_si_no_existe(codigo)
            st.session_state.codigo = codigo
            st.session_state.equipo = equipo
            st.success(f"Partida {codigo} creada / cargada.")
            st.rerun()

    if unirse:
        if not codigo_valido(codigo):
            st.error("Código inválido (mínimo 4 caracteres alfanuméricos).")
        elif not existe_partida(codigo):
            st.error("Esa partida no existe.")
        else:
            st.session_state.codigo = codigo
            st.session_state.equipo = equipo
            st.success(f"Unido a {codigo} como equipo {equipo}.")
            st.rerun()

# ---------------------------------
# SI NO HAY CÓDIGO, PARAMOS AQUÍ (PERO LA SIDEBAR YA EXISTE)
# ---------------------------------
if "codigo" not in st.session_state or not st.session_state.codigo:
    st.info("Introduce un código en la barra lateral para crear o unirte a una partida.")
    st.stop()

CODIGO = st.session_state.codigo

# ---------------------------------
# CARGA ESTADO PARTIDA
# ---------------------------------
estado = cargar_partida(CODIGO)
if estado is None:
    estado = crear_partida_si_no_existe(CODIGO)

bloquear_si_finalizado(estado)



# ---------------------------------
# CONFIGURACIÓN
# ---------------------------------

st.title("🧠 BIVRA - Partida compartida")


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
# ACCIONES
# ---------------------------------
col_a, col_b = st.columns(2)

with col_a:
    if st.button("▶️ Siguiente ronda (acción compartida)", key="btn_siguiente_ronda"):
        estado, eventos = siguiente_ronda(estado, estructura, agrupaciones)
        guardar_partida(CODIGO, estado)
        st.rerun()



with col_b:
    if st.button("🔄 Reiniciar partida (para todos)"):
        estado = inicializar_juego()
    # opcional: guardar el código dentro del estado
        estado["codigo_partida"] = CODIGO
        guardar_partida(CODIGO, estado)
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
        st.subheader("Fusiones (selecciona cartas)")

        equipo = str(equipo)
        sel_key = f"sel_fusion_{equipo}"
        clear_key = f"clear_sel_{equipo}"

        if clear_key not in st.session_state:
            st.session_state[clear_key] = False

        # Limpieza ANTES de crear el widget
        if st.session_state[clear_key]:
            st.session_state[sel_key] = []
            st.session_state[clear_key] = False

        actividades = estado["mazos"].get(equipo, [])
        if not actividades:
            st.info("No hay actividades para fusionar")
            return

        st.multiselect(
            "Selecciona las actividades a fusionar",
            options=actividades,
            format_func=lambda r: os.path.basename(str(r)),
            key=sel_key
        )

        seleccion = st.session_state.get(sel_key, [])

        if st.button("Fusionar selección", key=f"btn_fusion_sel_{equipo}"):
            nuevo_estado, ok, msg = ejecutar_fusion_con_seleccion(estado, equipo, seleccion)

            if ok:
                st.session_state.estado = nuevo_estado
                guardar_partida(CODIGO, nuevo_estado)
                st.session_state[clear_key] = True  # se limpia en el rerun
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)





def mostrar_proyectos(col, equipo):
    with col:
        st.subheader("Paquetes completados")

        equipo = str(equipo)
        paquetes_ids = estado.get("proyectos", {}).get(equipo, [])

        if not paquetes_ids:
            st.info("Todavía no hay paquetes completados")
            return

        proyecto_id = proyecto_asignado(estado, equipo)
        if not proyecto_id:
            st.error("No hay proyecto asignado a este equipo (proyecto_id es None).")
            return

        for pid in paquetes_ids:
            ruta = ruta_paquete(int(pid), int(proyecto_id))

            # DEBUG útil (puedes quitarlo luego):
            # st.write("DEBUG ruta paquete:", ruta)

            if os.path.exists(ruta):
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
                key=f"entregable_{equipo}_{entregable_id}",
            ):
                nuevo_estado, ok = ejecutar_entregable(
                    estado, equipo, int(entregable_id)  # 👈 MUY IMPORTANTE
                )

                if ok:
                    guardar_partida(CODIGO, nuevo_estado)
                    st.rerun()

                else:
                    st.warning("❌ No se cumplen los requisitos para este entregable")


def mostrar_entregables_creados(col, equipo):
    with col:
        st.subheader("Entregables creados")

        entregables = estado.get("entregables", {}).get(str(equipo), [])

        if not entregables:
            st.info("No hay entregables creados todavía")
            return

        for ruta in entregables:
            if os.path.exists(ruta):
                st.image(ruta, width=200)
            else:
                st.error(f"Imagen no encontrada: {ruta}")


def mostrar_proyectos2(col, equipo):
    with col:
        st.subheader("Proyecto final")

        entregables = estado.get("entregables", {}).get(str(equipo), [])
        posibles = proyectos_disponibles(entregables)

        if not posibles:
            st.info("No hay proyectos disponibles")
            return

        for proyecto_id in posibles:
            if st.button(
                f"Crear Proyecto {proyecto_id}",
                key=f"crear_proyecto_{equipo}_{proyecto_id}",
            ):
                nuevo_estado, ok = ejecutar_proyecto(estado, equipo, proyecto_id)
                if ok:
                    guardar_partida(CODIGO, nuevo_estado)
                    st.rerun()



                    


                    
def mostrar_proyecto_final(col, equipo):
    with col:
        st.subheader("Proyecto completado")

        equipo = str(equipo)
        proyectos_finales = estado.get("proyectos_finales", {})
        lista = proyectos_finales.get(equipo, [])

        if not lista:
            st.info("Aún no se ha completado el proyecto")
            return

        for ruta_rel in lista:
            ruta_abs = abs_path(ruta_rel)
            if not Path(ruta_abs).exists():
                st.error(f"Imagen no encontrada: {ruta_rel}")
            else:
                st.image(ruta_abs, width=220)

            






col1, col2 = st.columns(2)

mostrar_equipo(col1, 1)
mostrar_fusiones(col1, 1)
mostrar_proyectos(col1, 1)
mostrar_entregables(col1, 1)
mostrar_entregables_creados(col1, 1)
mostrar_proyectos2(col1, 1)
mostrar_proyecto_final(col1, 1)

mostrar_equipo(col2, 2)
mostrar_fusiones(col2, 2)
mostrar_proyectos(col2, 2)
mostrar_entregables(col2, 2)
mostrar_entregables_creados(col2, 2)
mostrar_proyectos2(col2, 2)
mostrar_proyecto_final(col2, 2)

# ---------------------------------
# DEBUG
# ---------------------------------
with st.expander("ℹ️ Estado interno (debug)"):
    st.json(estado)
