import os
import random
import re

# ==============================
# CONFIGURACIÓN
# ==============================

BASE_PATH = os.path.join(os.path.dirname(__file__), "imagenes", "Proyectos")

EMPAREJAMIENTOS = {
    "1": "2", "2": "1",
    "3": "4", "4": "3",
    "5": "6", "6": "5"
}


# ==============================
# UTILIDADES
# ==============================

def natural_key(text):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", text)]


def inicializar_juego():
    return {
        "ronda": 1,
        "historial": [],
        "mazos": {1: [], 2: []},
        "proyectos": None,
        "finalizado": False
    }


def normalizar_estado(estado):
    estado.setdefault("historial", [])
    estado.setdefault("mazos", {1: [], 2: []})
    return estado


# ==============================
# CARGA DE ESTRUCTURA
# ==============================

def cargar_estructura_proyecto():
    estructura = {}

    for proyecto_id in sorted(os.listdir(BASE_PATH), key=natural_key):
        ruta_proyecto = os.path.join(BASE_PATH, proyecto_id)
        if not os.path.isdir(ruta_proyecto):
            continue

        entregables = {}
        ruta_entregables = os.path.join(ruta_proyecto, "Entregables")

        for ent_id in sorted(os.listdir(ruta_entregables), key=natural_key):
            ruta_ent = os.path.join(ruta_entregables, ent_id)
            if not os.path.isdir(ruta_ent):
                continue

            ruta_actividades = os.path.join(
                ruta_ent, "Paquete trabajo", "Actividades"
            )

            if not os.path.isdir(ruta_actividades):
                continue

            actividades = [
                os.path.join(ruta_actividades, f)
                for f in sorted(os.listdir(ruta_actividades), key=natural_key)
                if f.endswith(".jpg")
            ]

            entregables[ent_id] = {
                "paquetes": {
                    ent_id: {   # 1 paquete por entregable
                        "actividades": actividades,
                        "carta": os.path.join(ruta_ent, f"{ent_id}.jpg")
                    }
                },
                "carta": os.path.join(ruta_ent, f"{ent_id}.jpg")
            }

        estructura[proyecto_id] = {
            "entregables": entregables,
            "carta": os.path.join(ruta_proyecto, f"{proyecto_id}.jpg")
        }

    return estructura


# ==============================
# AGRUPACIONES AUTOMÁTICAS
# ==============================

def generar_diccionario_agrupaciones(estructura):
    agr = {
        "actividades_a_paquete": {},
        "paquetes_a_entregable": {},
        "entregables_a_proyecto": {}
    }

    for pid, pinfo in estructura.items():
        for eid, einfo in pinfo["entregables"].items():
            # Paquetes → Entregable
            paquetes = []
            for pqid, pqinfo in einfo["paquetes"].items():
                key_pq = f"{pid}_{eid}_{pqid}"
                agr["actividades_a_paquete"][key_pq] = {
                    "actividades": pqinfo["actividades"],
                    "carta": pqinfo["carta"]
                }
                paquetes.append(pqinfo["carta"])

            agr["paquetes_a_entregable"][f"{pid}_{eid}"] = {
                "paquetes": paquetes,
                "carta": einfo["carta"]
            }

        agr["entregables_a_proyecto"][pid] = {
            "entregables": [e["carta"] for e in pinfo["entregables"].values()],
            "carta": pinfo["carta"]
        }

    return agr


# ==============================
# FUSIÓN DE CARTAS
# ==============================

def fusionar_cartas(mazo, agrupaciones):
    eventos = []
    cambiado = True

    while cambiado:
        cambiado = False

        # Actividades → Paquete
        for info in agrupaciones["actividades_a_paquete"].values():
            if all(a in mazo for a in info["actividades"]):
                for a in info["actividades"]:
                    mazo.remove(a)
                mazo.append(info["carta"])
                eventos.append("🔧 Paquete de trabajo completado")
                cambiado = True
                break

        if cambiado:
            continue

        # Paquetes → Entregable
        for info in agrupaciones["paquetes_a_entregable"].values():
            if all(p in mazo for p in info["paquetes"]):
                for p in info["paquetes"]:
                    mazo.remove(p)
                mazo.append(info["carta"])
                eventos.append("📦 Entregable completado")
                cambiado = True
                break

        if cambiado:
            continue

        # Entregables → Proyecto
        for info in agrupaciones["entregables_a_proyecto"].values():
            if all(e in mazo for e in info["entregables"]):
                for e in info["entregables"]:
                    mazo.remove(e)
                mazo.append(info["carta"])
                eventos.append("🏆 Proyecto completado")
                cambiado = True
                break

    return mazo, eventos


# ==============================
# LÓGICA DE RONDA
# ==============================

def siguiente_ronda(estado, estructura, agrupaciones):
    estado = normalizar_estado(estado)
    eventos = []

    # Asignar proyectos en la primera ronda
    if estado["ronda"] == 1:
        proyectos = list(estructura.keys())
        p1 = random.choice(proyectos)
        p2 = EMPAREJAMIENTOS.get(p1, random.choice(proyectos))
        estado["proyectos"] = {1: p1, 2: p2}
        eventos.append(f"Proyecto equipo 1: {p1}")
        eventos.append(f"Proyecto equipo 2: {p2}")

    # Reparto de actividades
    for equipo, proyecto in estado["proyectos"].items():
        actividades = []
        for ent in estructura[proyecto]["entregables"].values():
            for pq in ent["paquetes"].values():
                actividades.extend(pq["actividades"])

        disponibles = [a for a in actividades if a not in estado["historial"]]
        robadas = random.sample(disponibles, min(16, len(disponibles)))

        estado["historial"].extend(robadas)
        estado["mazos"][equipo].extend(robadas)

        estado["mazos"][equipo], nuevos_eventos = fusionar_cartas(
            estado["mazos"][equipo], agrupaciones
        )
        eventos.extend(nuevos_eventos)

    estado["ronda"] += 1
    return estado, eventos
