import json
import os

ESTADO_FILE = "estado.json"


def load_estado():
    """
    Carga el estado desde disco.
    Si no existe, devuelve None.
    """
    if not os.path.exists(ESTADO_FILE):
        return None

    try:
        with open(ESTADO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_estado(estado):
    """
    Guarda el estado actual en disco.
    """
    try:
        with open(ESTADO_FILE, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2)
    except Exception as e:
        print("Error guardando estado:", e)

