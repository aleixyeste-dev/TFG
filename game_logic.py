import os
import re
import random

# ==============================
# CONFIGURACIÓN
# ==============================
BASE_PATH = os.path.join("imagenes", "Proyectos")

EMPAREJAMIENTOS = {
    "1": "2", "2": "1",
    "3": "4", "4": "3",
    "5": "6", "6": "5"
}

# ==============================
# UTILIDADES
# ==============================
def natural_key(s):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r'(\d+)', s)]

def listar_imagenes(carpeta):
    return sorted(
        [os.path.join(carpeta, f)
         for f in os.listdir(carpeta)
         if f.lower().endswith((".jpg", ".jpeg", ".png"))],
        key=lambda p: natural_key(os.path.basename(p))
    )

# ==============================
# CARGA DE DATOS
# ==============================
def cargar_estructura_proyecto():
    estructura = {}

    for proyecto_id in sorted(os.listdir(BASE_PATH), key=natural_key):
        proyecto_dir = os.path.join(BASE_PATH, proyecto_id)
        if not os.path.isdir(proyecto_dir):
            continue

        proyecto_img = os.path.join(proyecto_dir, f"{proyecto_id}.jpg")
        estructura[proyecto_id] = {
            "proyecto_img": proyecto_img,
            "actividades": []
        }

        entregables_dir = os.path.join(proyecto_dir, "Entregables")
        if not os.path.exists(entregables_dir):
            continue

        for root, _, files in os.walk(entregables_dir):
            if os.path.basename(root).lower() == "actividades":
                for f in files:
                    if f.lower().endswith((".jpg", ".jpeg", ".png")):
                        estructura[proyecto_id]["actividades"].append(
                            os.path.join(root, f)
                        )

        estructura[proyecto_id]["actividades"].sort(
            key=lambda p: natural_key(os.path.basename(p))
        )

    return estructura

# ==============================
# AGRUPACIONES AUTOMÁTICAS
# ==============================
def generar_diccionario_agrupaciones():
    agr_act = {}
    agr_paq = {}
    agr_ent = {}

    for proyecto_id in os.listdir(BASE_PATH):
        proyecto_dir = os.path.join(BASE_PATH, proyecto_id)
        entregables_dir = os.path.join(proyecto_dir, "Entregables")
        if not os.path.exists(entregables_dir):
            continue

        proyecto_img = os.path.join(proyecto_dir, f"{proyecto_id}.jpg")

        paquetes_dir = None
        for d in os.listdir(entregables_dir):
            if "paquete" in d.lower():
                paquetes_dir = os.path.join(entregables_dir, d)
                break
        if not paquetes_dir:
            continue

        actividades = []
        for root, _, files in os.walk(entregables_dir):
            if os.path.basename(root).lower() == "actividades":
                for f in files:
                    if f.lower().endswith((".jpg", ".jpeg", ".png")):
                        actividades.append(os.path.join(root, f))
        actividades.sort(key=lambda p: natural_key(os.path.basename(p)))

        paquetes = listar_imagenes(paquetes_dir)
        entregables = [
            os.path.join(entregables_dir, f)
            for f in os.listdir(entregables_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        entregables.sort(key=lambda p: natural_key(os.path.basename(p)))

        for i, pkg in enumerate(paquetes):
            bloque = actividades[i*4:(i+1)*4]
            if len(bloque) == 4:
                agr_act[pkg] = bloque

        for i, ent in enumerate(entregables):
            bloque = paquetes[i*4:(i+1)*4]
            if len(bloque) == 4:
                agr_paq[ent] = bloque

        for i in range(0, len(entregables), 4):
            bloque = entregables[i:i+4]
            if len(bloque) == 4:
                agr_ent[proyecto_img] = bloque

    return agr_act, agr_paq, agr_ent

# ==============================
# FUSIÓN MULTINIVEL
# ==============================
def fusionar_cartas(mazo, agr_act, agr_paq, agr_ent, eventos):
    cambio = True
    while cambio:
        cambio = False

        for paquete, acts in agr_act.items():
            if all(a in mazo for a in acts):
                for a in acts:
                    mazo.remove(a)
                mazo.append(paquete)
                eventos.append(f"✅ Formado paquete {os.path.basename(paquete)}")
                cambio = True

        for entregable, paquetes in agr_paq.items():
            if all(p in mazo for p in paquetes):
                for p in paquetes:
                    mazo.remove(p)
                mazo.append(entregable)
                eventos.append(f"🎯 Formado entregable {os.path.basename(entregable)}")
                cambio = True

        for proyecto, entregables in agr_ent.items():
            if all(e in mazo for e in entregables):
                mazo.clear()
                mazo.append(proyecto)
                eventos.append(f"🏆 PROYECTO COMPLETADO {os.path.basename(proyecto)}")
                cambio = False
                break

    return mazo

# ==============================
# ESTADO DEL JUEGO
# ==============================
def inicializar_juego():
    return {
        "ronda": 1,
        "historial": set(),
        "mazos": {1: [], 2: []},
        "proyectos": None,
        "finalizado": False
    }

# ==============================
# SIGUIENTE RONDA
# ==============================
def siguiente_ronda(estado, estructura, agrupaciones):
    eventos = []
    agr_act, agr_paq, agr_ent = agrupaciones

    if estado["finalizado"]:
        eventos.append("⛔ El juego ya ha terminado")
        return estado, eventos

    if estado["ronda"] == 1:
        proyectos = list(EMPAREJAMIENTOS.keys())
        random.shuffle(proyectos)
        p1 = proyectos[0]
        p2 = EMPAREJAMIENTOS[p1]
        estado["proyectos"] = (p1, p2)
    else:
        p1, p2 = estado["proyectos"]

    for equipo, proyecto in [(1, p1), (2, p2)]:
        disponibles = [
            a for a in estructura[proyecto]["actividades"]
            if a not in estado["historial"]
        ]

        if disponibles:
            robadas = random.sample(disponibles, min(16, len(disponibles)))
            estado["historial"].update(robadas)
            estado["mazos"][equipo].extend(robadas)

        estado["mazos"][equipo] = fusionar_cartas(
            estado["mazos"][equipo],
            agr_act, agr_paq, agr_ent,
            eventos
        )

        if len(estado["mazos"][equipo]) == 1:
            carta = estado["mazos"][equipo][0]
            if carta.endswith(".jpg") and os.path.basename(carta)[0].isdigit():
                estado["finalizado"] = True

    estado["ronda"] += 1
    return estado, eventos
