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


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # carpeta TFG (donde están los scripts)

def ruta_proyecto(proyecto_id: int) -> str | None:
    # tus proyectos están aquí: imagenes/Proyectos/<id>/<id>.<ext>
    for ext in ("jpg", "png", "jpeg", "webp"):
        rel = f"imagenes/Proyectos/{proyecto_id}/{proyecto_id}.{ext}"
        if (BASE_DIR / rel).exists():
            return rel
    return None



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
    import os
    
    if isinstance(ruta, int):
        return ruta

    nombre = os.path.basename(str(ruta))
    return int(os.path.splitext(nombre)[0])  # 24

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
    ruta = f"imagenes/Proyectos/{proyecto_id}/{proyecto_id}.jpg"

    nuevo_estado.setdefault("proyectos_finales", {})
    nuevo_estado["proyectos_finales"].setdefault(str(equipo), []).append(ruta)

    if not nuevo_estado.get("finalizado", False) and comprobar_fin_partida(nuevo_estado, equipo):
        finalizar_partida(nuevo_estado, equipo)
    
    return nuevo_estado, True


def finalizar_partida(estado: dict, equipo) -> dict:
    """
    Marca la partida como finalizada y guarda el equipo ganador.
    Devuelve el estado modificado (in-place, pero lo devolvemos por comodidad).
    """
    estado["finalizado"] = True
    estado["ganador"] = str(equipo)
    return estado


def comprobar_fin_partida(estado: dict, equipo) -> bool:
    """
    Devuelve True si este equipo ya tiene al menos 1 proyecto final creado.
    (Condición de victoria).
    """
    equipo = str(equipo)
    proyectos_finales = estado.get("proyectos_finales", {})
    lista = proyectos_finales.get(equipo, [])
    return len(lista) >= 1

def resetear_fin_partida(estado: dict) -> dict:
    estado["finalizado"] = False
    estado.pop("ganador", None)
    return estado

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

PARTIDAS_DIR = Path(__file__).resolve().parent / "partidas"
PARTIDAS_DIR.mkdir(exist_ok=True)

def _path_partida(codigo: str) -> Path:
    codigo = codigo.strip().upper()
    return PARTIDAS_DIR / f"{codigo}.json"

def _path_lock(codigo: str) -> Path:
    codigo = codigo.strip().upper()
    return PARTIDAS_DIR / f"{codigo}.lock"

def _adquirir_lock(codigo: str, timeout_s: float = 3.0) -> None:
    """Lock simple por archivo (evita escrituras simultáneas)."""
    lock_path = _path_lock(codigo)
    inicio = time.time()
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return
        except FileExistsError:
            if time.time() - inicio > timeout_s:
                # si se queda colgado por un lock viejo, lo rompemos
                try:
                    lock_path.unlink()
                except Exception:
                    pass
                return
            time.sleep(0.05)

def _liberar_lock(codigo: str) -> None:
    try:
        _path_lock(codigo).unlink()
    except Exception:
        pass

def cargar_partida(codigo: str) -> Optional[Dict[str, Any]]:
    path = _path_partida(codigo)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def guardar_partida(codigo: str, estado: Dict[str, Any]) -> None:
    codigo = codigo.strip().upper()
    _adquirir_lock(codigo)
    try:
        path = _path_partida(codigo)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)  # escritura atómica
    finally:
        _liberar_lock(codigo)

def crear_partida_si_no_existe(codigo: str) -> Dict[str, Any]:
    codigo = codigo.strip().upper()
    estado = cargar_partida(codigo)
    if estado is None:
        estado = inicializar_juego()  # <-- tu función existente
        # opcional: guarda el código dentro del estado
        estado["codigo_partida"] = codigo
        guardar_partida(codigo, estado)
    return estado

def existe_partida(codigo: str) -> bool:
    return _path_partida(codigo.strip().upper()).exists()


import copy

def ejecutar_fusion_con_seleccion(estado, equipo, paquete_id, cartas_seleccionadas):
    """
    cartas_seleccionadas: lista de rutas (strings) de actividades elegidas por el usuario
    """
    nuevo_estado = copy.deepcopy(estado)
    equipo = str(equipo)
    paquete_id = int(paquete_id)

    # requisitos del paquete
    actividades_necesarias = FUSIONES_PAQUETES.get(paquete_id)
    if not actividades_necesarias:
        return estado, False, "Paquete no existe en FUSIONES_PAQUETES"

    # validar selección: convertir rutas a ids
    ids_sel = [extraer_id(c) for c in cartas_seleccionadas]

    # 1) que todas las seleccionadas pertenezcan al mazo
    mazo = nuevo_estado["mazos"].get(equipo, [])
    if any(c not in mazo for c in cartas_seleccionadas):
        return estado, False, "Has seleccionado cartas que no están en tu mazo"

    # 2) que la selección sea EXACTAMENTE la necesaria (mismo conjunto)
    if set(ids_sel) != set(actividades_necesarias):
        return estado, False, "La selección no coincide con las actividades requeridas"

    # eliminar SOLO las seleccionadas
    nuevo_estado["mazos"][equipo] = [c for c in mazo if c not in cartas_seleccionadas]

    # añadir paquete completado
    nuevo_estado.setdefault("proyectos", {})
    nuevo_estado["proyectos"].setdefault(equipo, []).append(str(paquete_id))

    return nuevo_estado, True, "Fusión realizada"

def paquetes_que_coinciden(ids_actividades):
    ids = set(ids_actividades)
    return [pid for pid, req in FUSIONES_PAQUETES.items() if set(req) == ids]

