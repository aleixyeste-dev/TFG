import os
import random
import re
import copy
# ==============================
# Utilidades
# ==============================

def natural_key(text):
    return [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", text)]


def normalizar_estado(estado):
    estado.setdefault("ronda", 0)
    estado.setdefault("historial", [])
    estado.setdefault("mazos", {"1": [], "2": []})
    estado.setdefault("proyectos", {})
    estado.setdefault("finalizado", False)
    return estado


# ==============================
# Inicialización
# ==============================

def inicializar_juego(estructura):
    proyectos_ids = list(estructura.keys())

    return {
        "ronda": 0,
        "historial": [],
        "mazos": {
            "1": [],
            "2": []
        },
        "proyectos": {
            "1": proyectos_ids[0],
            "2": proyectos_ids[1] if len(proyectos_ids) > 1 else proyectos_ids[0]
        },
        "finalizado": False
    }

# ==============================
# Carga estructura
# ==============================

def cargar_estructura_proyecto():
    base_path = "/mount/src/tfg/imagenes/Proyectos"

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
    return mazo, eventos


# ==============================
# Ronda
# ==============================

import copy
import random

def siguiente_ronda(estado, estructura, agrupaciones):
    nuevo_estado = copy.deepcopy(estado)
    eventos = []

    if nuevo_estado.get("finalizado"):
        return nuevo_estado, eventos

    # avanzar ronda
    nuevo_estado["ronda"] += 1

    # asegurar estructura de mazos
    for equipo in ["1", "2"]:
        if equipo not in nuevo_estado["mazos"]:
            nuevo_estado["mazos"][equipo] = []

    # 🔹 REPARTO DE CARTAS (CLARO Y DIRECTO)
    for equipo in ["1", "2"]:
        proyecto_id = nuevo_estado["proyectos"].get(equipo)

        if not proyecto_id:
            continue

        # cartas disponibles del proyecto
        cartas_proyecto = [
            info["carta"]
            for key, info in agrupaciones["actividades_a_paquete"].items()
            if key.startswith(f"{proyecto_id}_")
        ]

        if not cartas_proyecto:
            continue

        carta = random.choice(cartas_proyecto)
        nuevo_estado["mazos"][equipo].append(carta)

        eventos.append({
            "tipo": "robo",
            "equipo": equipo,
            "carta": carta
        })

    return nuevo_estado, eventos




def fusiones_disponibles(mazo, agrupaciones):
    """
    Devuelve una lista de fusiones posibles a partir del mazo actual
    """
    fusiones = []

    if not mazo:
        return fusiones

    # Convertimos el mazo a IDs
    ids_mazo = {obtener_id_carta(carta): carta for carta in mazo}

    # ACTIVIDADES -> PAQUETE
    for key, info in agrupaciones["actividades_a_paquete"].items():
        actividades = info["actividades"]

        if all(a in ids_mazo for a in actividades):
            fusiones.append({
                "tipo": "actividades_a_paquete",
                "resultado": info["carta"],
                "consume": [ids_mazo[a] for a in actividades]
            })

    # PAQUETES -> ENTREGABLE
    for key, info in agrupaciones["paquetes_a_entregable"].items():
        paquetes = info["paquetes"]

        if all(p in mazo for p in paquetes):
            fusiones.append({
                "tipo": "paquetes_a_entregable",
                "resultado": info["carta"],
                "consume": paquetes
            })

    return fusiones




def obtener_id_carta(ruta):
    """
    Extrae el ID de la carta a partir de la ruta de la imagen
    Ejemplo: /path/Actividades/76.jpg -> 76
    """
    return ruta.split("/")[-1].replace(".jpg", "")

