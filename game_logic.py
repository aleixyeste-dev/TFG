import os
import random
import re

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

def inicializar_juego():
    return {
        "ronda": 0,
        "historial": [],
        "mazos": {"1": [], "2": []},
        "proyectos": {},
        "finalizado": False,
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

def siguiente_ronda(estado, estructura, agrupaciones):
    nuevo_estado = copy.deepcopy(estado)
    eventos = []

    if nuevo_estado.get("finalizado"):
        return nuevo_estado, eventos

    nuevo_estado["ronda"] += 1

    # Reparto por equipo
    for equipo, proyecto in nuevo_estado["proyectos"].items():

        # Inicializar mazo si no existe
        nuevo_estado["mazos"].setdefault(equipo, [])

        # --- 1️⃣ OBTENER ACTIVIDADES DISPONIBLES ---
        actividades = estructura[proyecto]["actividades"]

        if not actividades:
            continue

        # Robar hasta 2 cartas por ronda
        robadas = random.sample(
            actividades,
            k=min(2, len(actividades))
        )

        nuevo_estado["mazos"][equipo].extend(robadas)

        eventos.append({
            "equipo": equipo,
            "accion": "robo",
            "cartas": robadas
        })

        # --- 2️⃣ APLICAR FUSIONES ---
        hubo_fusion = True

        while hubo_fusion:
            hubo_fusion = False
            mazo = nuevo_estado["mazos"][equipo]

            fusiones = fusiones_disponibles(mazo, agrupaciones)

            if not fusiones:
                break

            fusion = fusiones[0]  # aplicar la primera posible

            # Eliminar cartas consumidas
            for c in fusion["consume"]:
                if c in mazo:
                    mazo.remove(c)

            # Añadir carta resultante
            mazo.append(fusion["resultado"])

            eventos.append({
                "equipo": equipo,
                "accion": "fusion",
                "tipo": fusion["tipo"],
                "resultado": fusion["resultado"]
            })

            hubo_fusion = True

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

