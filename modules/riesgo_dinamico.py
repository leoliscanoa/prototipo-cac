"""
Motor de riesgo dinamico.

Evalua y recalcula el nivel de riesgo de un paciente cada vez
que ingresan nuevos datos clinicos. El riesgo NO es estatico:
cambia con la evolucion del paciente.

Logica de negocio:
- Se calcula un score numerico (0-100) basado en variables clinicas
- Se clasifica en 4 niveles: Bajo, Medio, Alto, Muy Alto
- Se genera explicabilidad tipo SHAP (factores que mas contribuyen)

# PLACEHOLDER: En produccion este modulo se conectara con un modelo
# entrenado (XGBoost/LightGBM) via pickle/ONNX. Por ahora usa
# un sistema de reglas ponderadas como proxy.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


# Pesos de variables para el calculo de riesgo (simulando SHAP values)
PESOS_RIESGO = {
    "edad": 0.12,
    "creatinina": 0.18,
    "tasa_filtracion_glomerular": -0.20,  # Negativo: mayor TFG = menor riesgo
    "hemoglobina_glucosilada": 0.15,
    "presion_arterial_sistolica": 0.10,
    "albuminuria": 0.13,
    "adherencia": -0.08,  # Negativo: mayor adherencia = menor riesgo
    "episodios_hospitalizacion": 0.04,
}

UMBRALES_RIESGO = {
    "Bajo": (0, 25),
    "Medio": (26, 50),
    "Alto": (51, 75),
    "Muy Alto": (76, 100),
}


def calcular_score_riesgo(paciente: Dict) -> Tuple[float, str, List[Dict]]:
    """
    Calcula el score de riesgo de un paciente y genera explicabilidad.

    Args:
        paciente: Diccionario con datos clinicos del paciente

    Returns:
        Tuple de (score_numerico, nivel_riesgo, factores_explicabilidad)
    """
    score = 30.0  # Base
    factores = []

    # Edad
    edad = paciente.get("edad", 50)
    if edad > 65:
        contribucion = (edad - 65) * 0.8
        score += contribucion
        factores.append({"variable": "Edad", "valor": edad, "contribucion": round(contribucion, 1), "direccion": "aumenta"})
    elif edad < 40:
        contribucion = -5
        score += contribucion
        factores.append({"variable": "Edad", "valor": edad, "contribucion": round(contribucion, 1), "direccion": "disminuye"})

    # Creatinina
    creat = paciente.get("creatinina", 1.0)
    if creat > 2.0:
        contribucion = (creat - 1.0) * 8
        score += contribucion
        factores.append({"variable": "Creatinina", "valor": f"{creat} mg/dL", "contribucion": round(contribucion, 1), "direccion": "aumenta"})

    # TFG
    tfg = paciente.get("tasa_filtracion_glomerular", 90)
    if tfg < 60:
        contribucion = (60 - tfg) * 0.5
        score += contribucion
        factores.append({"variable": "TFG", "valor": f"{tfg} mL/min", "contribucion": round(contribucion, 1), "direccion": "aumenta"})
    elif tfg > 90:
        contribucion = -5
        score += contribucion
        factores.append({"variable": "TFG", "valor": f"{tfg} mL/min", "contribucion": round(contribucion, 1), "direccion": "disminuye"})

    # HbA1c
    hba1c = paciente.get("hemoglobina_glucosilada", 5.5)
    if hba1c > 7.0:
        contribucion = (hba1c - 7.0) * 6
        score += contribucion
        factores.append({"variable": "HbA1c", "valor": f"{hba1c}%", "contribucion": round(contribucion, 1), "direccion": "aumenta"})

    # Presion arterial
    pas = paciente.get("presion_arterial_sistolica", 120)
    if pas > 140:
        contribucion = (pas - 140) * 0.3
        score += contribucion
        factores.append({"variable": "PAS", "valor": f"{pas} mmHg", "contribucion": round(contribucion, 1), "direccion": "aumenta"})

    # Albuminuria
    alb = paciente.get("albuminuria", 20)
    if alb > 30:
        contribucion = min((alb - 30) * 0.05, 15)
        score += contribucion
        factores.append({"variable": "Albuminuria", "valor": f"{alb} mg/g", "contribucion": round(contribucion, 1), "direccion": "aumenta"})

    # Adherencia (reduce riesgo)
    adherencia = paciente.get("adherencia", 90)
    if adherencia < 80:
        contribucion = (80 - adherencia) * 0.4
        score += contribucion
        factores.append({"variable": "Adherencia", "valor": f"{adherencia}%", "contribucion": round(contribucion, 1), "direccion": "aumenta"})

    # Normalizar score 0-100
    score = max(0, min(100, score))

    # Clasificar nivel
    nivel = "Bajo"
    for nombre, (low, high) in UMBRALES_RIESGO.items():
        if low <= score <= high:
            nivel = nombre
            break

    # Ordenar factores por contribucion absoluta
    factores.sort(key=lambda x: abs(x["contribucion"]), reverse=True)

    return round(score, 1), nivel, factores


def recalcular_riesgo_cohorte(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recalcula el riesgo de toda la cohorte. Esta funcion se ejecuta
    cada vez que ingresan nuevos datos clinicos.

    Args:
        df: DataFrame con datos de pacientes

    Returns:
        DataFrame con columnas score_riesgo y nivel_riesgo actualizadas
    """
    scores = []
    niveles = []
    explicaciones = []

    for _, row in df.iterrows():
        paciente = row.to_dict()
        score, nivel, factores = calcular_score_riesgo(paciente)
        scores.append(score)
        niveles.append(nivel)
        # Guardar top 3 factores como texto
        top3 = "; ".join([f"{f['variable']}={f['valor']}" for f in factores[:3]])
        explicaciones.append(top3)

    df = df.copy()
    df["score_riesgo"] = scores
    df["nivel_riesgo"] = niveles
    df["factores_riesgo"] = explicaciones
    df["fecha_calculo_riesgo"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    return df


def calcular_score_elegibilidad(paciente: Dict, patologia: str) -> Tuple[float, str]:
    """
    Calcula un score de elegibilidad para ingreso/egreso de cohorte.

    Args:
        paciente: Datos del paciente
        patologia: Patologia de la cohorte

    Returns:
        Tuple (score 0-100, recomendacion: INGRESAR/MANTENER/EGRESAR)
    """
    score_riesgo, nivel, _ = calcular_score_riesgo(paciente)

    # Logica de elegibilidad
    if nivel in ["Alto", "Muy Alto"]:
        return score_riesgo, "INGRESAR"
    elif nivel == "Medio":
        return score_riesgo, "MANTENER"
    else:
        # Bajo riesgo por 2+ periodos consecutivos -> egresar
        return score_riesgo, "EGRESAR"


def generar_datos_demo_riesgo(n: int = 50) -> pd.DataFrame:
    """Genera datos demo con riesgo calculado para visualizacion."""
    np.random.seed(99)
    datos = {
        "documento": [f"{10000000 + i}" for i in range(n)],
        "nombres": [f"Paciente_{i}" for i in range(n)],
        "edad": np.random.randint(30, 80, n),
        "creatinina": np.round(np.random.uniform(0.6, 6.0, n), 2),
        "tasa_filtracion_glomerular": np.round(np.random.uniform(15, 120, n), 1),
        "hemoglobina_glucosilada": np.round(np.random.uniform(4.5, 11.0, n), 1),
        "presion_arterial_sistolica": np.random.randint(100, 190, n),
        "albuminuria": np.round(np.random.exponential(80, n), 1),
        "adherencia": np.round(np.random.uniform(40, 100, n), 1),
    }
    df = pd.DataFrame(datos)
    return recalcular_riesgo_cohorte(df)
