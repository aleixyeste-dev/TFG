import copy
import os
import random
import re

import fusiones


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "imagenes")


FUSIONES_PAQUETES = fusiones.FUSIONES_PAQUETES
# ==============================
# Utilidades
# ==============================

def natural_key(text):
    return [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", text)]


def normalizar_estado(estado):
    estado.setdefault("ronda", 0)
    estado.setdefault("historial", [])
    estado.setdefault("mazos", {"1": [], "2": []})
    estado.setdefault("proyectos", {})  # paquetes completados por equipo
    estado.setdefault("proyectos_asignados", {})
    estado.setdefault("finalizado", False)
    return estado



def cargar_proyectos_desde_txt():
    proyectos = {}

    with open("relacionesproyectos.txt", "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or ":" not in linea:
                continue

            izquierda, derecha = linea.split(":")

            # "Proyecto 1" -> 1
            proyecto_id = int(izquierda.replace("Proyecto", "").strip())

            entregables = [int(x.strip()) for x in derecha.split(",")]

            proyectos[proyecto_id] = entregables

    return proyectos




PROYECTOS = cargar_proyectos_desde_txt()


# ==============================
# Inicialización
# ==============================

def inicializar_juego():
    return {
        "ronda": 0,
        "historial": [],
        "mazos": {"1": [], "2": []},
        "proyectos": {},
        "proyectos_asignados": {},
        "finalizado": False,
    }


# ==============================
# Carga estructura
# ==============================

def cargar_estructura_proyecto():
    base_path = os.path.join(IMG_DIR, "Proyectos")

    if not os.path.exists(base_path):
        raise RuntimeError(f"No existe la ruta {base_path}")

    estructura = {}
    for pid in sorted(os.listdir(base_path)):
        ruta_proyecto = os.path.join(base_path, pid)
        if not os.path.isdir(ruta_proyecto):
            continue

        actividades = []
        ruta_actividades = os.path.join(
            ruta_proyecto, "Entregables", "Paquete trabajo", "Actividades"
        )

        if os.path.exists(ruta_actividades):
            for f in os.listdir(ruta_actividades):
                if f.lower().endswith(".jpg"):
                    actividades.append(os.path.join(ruta_actividades, f))

        estructura[pid] = {
            "actividades": actividades
        }

    return estructura



# ==============================
# Agrupaciones (placeholder)
# ==============================

def generar_diccionario_agrupaciones(estructura):
    return {
        "actividades_a_paquete": {},
        "paquetes_a_entregable": {},
        "entregables_a_proyecto": {},
    }


# ==============================
# Fusión SAFE
# ==============================

def fusionar_cartas(mazo, agrupaciones):
    eventos = []
    fusiones = fusiones_disponibles(mazo, agrupaciones)

    if not fusiones:
        return mazo, eventos

    # Ejecutar SOLO una fusión por ronda
    fusion = fusiones[0]

    for carta in fusion["cartas"]:
        mazo.remove(carta)

    carta_fusionada = fusion["resultado"]
    mazo.append(carta_fusionada)

    eventos.append(
        f"Fusión realizada: {len(fusion['cartas'])} cartas → paquete"
    )

    return mazo, eventos



# ==============================
# Ronda
# ==============================

def siguiente_ronda(estado, estructura, agrupaciones):
    estado = normalizar_estado(estado.copy())
    eventos = []

    # Asignar proyectos si no existen
    if not estado["proyectos_asignados"]:
        proyectos = list(estructura.keys())
        estado["proyectos_asignados"] = {
            "1": random.choice(proyectos),
            "2": random.choice(proyectos),
        }

    estado["ronda"] += 1

    for equipo, proyecto in estado["proyectos_asignados"].items():
        actividades = estructura.get(proyecto, {}).get("actividades", [])

        disponibles = [a for a in actividades if a not in estado["historial"]]
        if not disponibles:
            disponibles = actividades.copy()

        if disponibles:
            robadas = random.sample(disponibles, min(4, len(disponibles)))
            estado["mazos"][equipo].extend(robadas)
            estado["historial"].extend(robadas)
            eventos.append(f"Equipo {equipo} roba {len(robadas)} cartas")

    return estado, eventos



def obtener_id_carta(ruta):
    """
    Extrae el ID numérico de una carta desde la ruta de la imagen
    """
    return int(ruta.split("/")[-1].replace(".jpg", ""))


def fusiones_disponibles(mazo):
    """
    Devuelve una lista de paquetes que pueden fusionarse con el mazo actual
    """
    ids_mazo = {obtener_id_carta(c) for c in mazo}
    disponibles = []

    for paquete_id, actividades in FUSIONES_PAQUETES.items():
        if set(actividades).issubset(ids_mazo):
            disponibles.append({
                "paquete": paquete_id,
                "actividades": actividades
            })

    return disponibles


def proyecto_asignado(estado, equipo):
    return estado.get("proyectos_asignados", {}).get(str(equipo), "1")


def ruta_paquete(paquete_id, proyecto_id):
    return os.path.join(
        IMG_DIR,
        "Proyectos",
        str(proyecto_id),
        "Entregables",
        "Paquete trabajo",
        f"{paquete_id}.jpg",
    )




def aplicar_fusion(estado, equipo, paquete_id):
    """
    Aplica una fusión:
    - Elimina las actividades del paquete
    - Añade la carta del paquete
    """
    mazo = estado["mazos"][str(equipo)]
    actividades = FUSIONES_PAQUETES[paquete_id]

    nuevo_mazo = []
    for carta in mazo:
        if obtener_id_carta(carta) not in actividades:
            nuevo_mazo.append(carta)

    proyecto_id = proyecto_asignado(estado, equipo)
    nuevo_mazo.append(ruta_paquete(paquete_id, proyecto_id))
    estado["mazos"][str(equipo)] = nuevo_mazo

    return estado

def ejecutar_fusion(estado, equipo, paquete_id):
    nuevo_estado = copy.deepcopy(estado)
    equipo = str(equipo)
    paquete_id = int(paquete_id)

    actividades_necesarias = FUSIONES_PAQUETES[paquete_id]

    # eliminar actividades usadas
    nuevo_estado["mazos"][equipo] = [
        c for c in nuevo_estado["mazos"][equipo]
        if extraer_id(c) not in actividades_necesarias
    ]

    proyecto_id = proyecto_asignado(estado, equipo)
    ruta = ruta_paquete(paquete_id, proyecto_id)

    # guardar paquete completado
    # Asegurar tipos correctos
    equipo = str(equipo)

    if "proyectos" not in nuevo_estado or not isinstance(nuevo_estado["proyectos"], dict):
        nuevo_estado["proyectos"] = {}

    if equipo not in nuevo_estado["proyectos"] or not isinstance(nuevo_estado["proyectos"][equipo], list):
        nuevo_estado["proyectos"][equipo] = []

    nuevo_estado["proyectos"][equipo].append(ruta)



    return nuevo_estado, True






def extraer_id_actividad(ruta):
    """
    Extrae el número de actividad desde la ruta de la imagen
    Ej: Actividades/128.jpg -> 128
    """
    nombre = ruta.split("/")[-1]
    return int(nombre.replace(".jpg", ""))

def extraer_id(ruta):
    """
    Extrae el ID numérico desde una ruta de imagen.
    Ejemplo:
    imagenes/Proyectos/1/Entregables/Paquete trabajo/24.jpg -> 24
    """
    try:
        return int(os.path.splitext(os.path.basename(ruta))[0])
    except Exception:
        return None


from entregables import ENTREGABLES

def entregables_disponibles(paquetes_del_equipo):
    ids_paquetes = {extraer_id_desde_ruta(p) for p in paquetes_del_equipo}
    posibles = []

    for entregable_id, paquetes_necesarios in ENTREGABLES.items():
        if paquetes_necesarios.issubset(ids_paquetes):
            posibles.append(entregable_id)

    return posibles


def ejecutar_entregable(estado, equipo, entregable_id):
    nuevo_estado = copy.deepcopy(estado)
    equipo = str(equipo)
    entregable_id = int(entregable_id)

    paquetes_necesarios = ENTREGABLES.get(entregable_id)
    if not paquetes_necesarios:
        return estado, False

    # paquetes del equipo (son rutas)
    paquetes_equipo = nuevo_estado["proyectos"].get(equipo, [])

    # 🔑 convertir rutas a IDs
    ids_paquetes_equipo = {extraer_id_desde_ruta(p) for p in paquetes_equipo}

    # comprobar requisitos
    if not set(paquetes_necesarios).issubset(ids_paquetes_equipo):
        return estado, False

    # eliminar paquetes usados
    nuevo_estado["proyectos"][equipo] = [
        p for p in paquetes_equipo
        if extraer_id_desde_ruta(p) not in paquetes_necesarios
    ]

    # añadir entregable
    proyecto_id = proyecto_asignado(estado, equipo)
    ruta_entregable = os.path.join(
        IMG_DIR,
        "Proyectos",
        str(proyecto_id),
        "Entregables",
        f"{entregable_id}.jpg",
    )

    nuevo_estado.setdefault("entregables", {}).setdefault(equipo, []).append(ruta_entregable)

    return nuevo_estado, True




def extraer_id_desde_ruta(ruta):
    """
    Devuelve el número del archivo sin extensión.
    Ej: imagenes/.../24.jpg -> 24
    """

    if isinstance(ruta, int):
        return ruta

    nombre = os.path.basename(str(ruta))
    return int(os.path.splitext(nombre)[0])


def proyectos_disponibles(entregables_equipo):
    """
    Determina qué proyectos se pueden completar a partir de los entregables del equipo.

    Los entregables almacenan rutas a imágenes (p. ej. imagenes/Proyectos/1/Entregables/3.jpg),
    por lo que primero se extraen los IDs numéricos antes de validar los requisitos.
    """
    disponibles = []

    ids_entregables = set(
        extraer_id_desde_ruta(e)
        for e in entregables_equipo
    )

    for proyecto_id, necesarios in PROYECTOS.items():
        if set(necesarios).issubset(ids_entregables):
            disponibles.append(proyecto_id)

    return disponibles

def ejecutar_proyecto(estado, equipo, proyecto_id):
    nuevo_estado = copy.deepcopy(estado)
    equipo = str(equipo)

    necesarios = PROYECTOS.get(proyecto_id)
    if not necesarios:
        return estado, False

    entregables_equipo = set(
        extraer_id_desde_ruta(e)
        for e in nuevo_estado.get("entregables", {}).get(equipo, [])
    )

    if not set(necesarios).issubset(entregables_equipo):
        return estado, False

    # eliminar entregables usados
    nuevo_estado["entregables"][equipo] = [
        e
        for e in nuevo_estado["entregables"][equipo]
        if extraer_id_desde_ruta(e) not in necesarios
    ]

    # añadir proyecto final
    ruta = f"imagenes/Proyectos/{proyecto_id}.jpg"
    nuevo_estado.setdefault("proyecto_final", {}).setdefault(equipo, []).append(ruta)

    return nuevo_estado, True


