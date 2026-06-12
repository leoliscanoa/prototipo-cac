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
    Funciona para todas las patologias detectando las variables disponibles.

    Args:
        paciente: Diccionario con datos clinicos del paciente

    Returns:
        Tuple de (score_numerico, nivel_riesgo, factores_explicabilidad)
    """
    score = 25.0  # Base (ligeramente por debajo de Medio)
    factores = []

    # === VARIABLES GENERALES ===

    # Edad
    edad = paciente.get("edad", None)
    if edad is not None and isinstance(edad, (int, float)):
        if edad > 65:
            contribucion = (edad - 65) * 0.8
            score += contribucion
            factores.append({"variable": "Edad", "valor": edad, "contribucion": round(contribucion, 1), "direccion": "aumenta"})
        elif edad < 40:
            score -= 3

    # === ERC / HTA / DM ===

    # Creatinina
    creat = paciente.get("creatinina", None)
    if creat is not None and isinstance(creat, (int, float)) and creat > 0:
        if creat > 2.0:
            contribucion = (creat - 1.0) * 8
            score += contribucion
            factores.append({"variable": "Creatinina", "valor": f"{creat} mg/dL", "contribucion": round(contribucion, 1), "direccion": "aumenta"})
        elif creat < 1.0:
            score -= 3

    # TFG
    tfg = paciente.get("tasa_filtracion_glomerular", None)
    if tfg is not None and isinstance(tfg, (int, float)) and tfg > 0:
        if tfg < 30:
            contribucion = (60 - tfg) * 0.7
            score += contribucion
            factores.append({"variable": "TFG", "valor": f"{tfg} mL/min", "contribucion": round(contribucion, 1), "direccion": "aumenta"})
        elif tfg < 60:
            contribucion = (60 - tfg) * 0.4
            score += contribucion
            factores.append({"variable": "TFG", "valor": f"{tfg} mL/min", "contribucion": round(contribucion, 1), "direccion": "aumenta"})
        elif tfg > 90:
            score -= 5

    # HbA1c
    hba1c = paciente.get("hemoglobina_glucosilada", None)
    if hba1c is not None and isinstance(hba1c, (int, float)) and hba1c > 0:
        if hba1c > 7.0:
            contribucion = (hba1c - 7.0) * 6
            score += contribucion
            factores.append({"variable": "HbA1c", "valor": f"{hba1c}%", "contribucion": round(contribucion, 1), "direccion": "aumenta"})

    # Albuminuria
    alb = paciente.get("albuminuria", None)
    if alb is not None and isinstance(alb, (int, float)) and alb > 0:
        if alb > 30:
            contribucion = min((alb - 30) * 0.05, 15)
            score += contribucion
            factores.append({"variable": "Albuminuria", "valor": f"{alb} mg/g", "contribucion": round(contribucion, 1), "direccion": "aumenta"})

    # Dialisis
    dialisis = str(paciente.get("dialisis", "NO")).upper()
    if dialisis == "SI":
        score += 20
        factores.append({"variable": "Dialisis", "valor": "SI", "contribucion": 20, "direccion": "aumenta"})

    # === VIH / SIDA ===

    # CD4
    cd4 = paciente.get("cd4", None)
    if cd4 is not None and isinstance(cd4, (int, float)) and cd4 >= 0:
        if cd4 < 200:
            contribucion = (200 - cd4) * 0.15
            score += contribucion
            factores.append({"variable": "CD4", "valor": f"{int(cd4)} cel/uL", "contribucion": round(contribucion, 1), "direccion": "aumenta"})
        elif cd4 > 500:
            score -= 8
            factores.append({"variable": "CD4", "valor": f"{int(cd4)} cel/uL", "contribucion": -8, "direccion": "disminuye"})

    # Carga viral
    cv = paciente.get("carga_viral", None)
    if cv is not None and isinstance(cv, (int, float)):
        if cv > 1000:
            contribucion = min(25, cv / 5000)
            score += contribucion
            factores.append({"variable": "Carga viral", "valor": f"{int(cv)} cop/mL", "contribucion": round(contribucion, 1), "direccion": "aumenta"})
        elif cv == 0 or cv < 50:
            score -= 10
            factores.append({"variable": "Carga viral", "valor": "Indetectable", "contribucion": -10, "direccion": "disminuye"})

    # === CANCER ===

    # Estadio
    estadio = str(paciente.get("estadio", "")).upper()
    if estadio in ["IV", "IIIB"]:
        score += 30
        factores.append({"variable": "Estadio", "valor": estadio, "contribucion": 30, "direccion": "aumenta"})
    elif estadio in ["IIIA", "III"]:
        score += 18
        factores.append({"variable": "Estadio", "valor": estadio, "contribucion": 18, "direccion": "aumenta"})
    elif estadio in ["IIA", "IIB", "II"]:
        score += 8
        factores.append({"variable": "Estadio", "valor": estadio, "contribucion": 8, "direccion": "aumenta"})
    elif estadio in ["I", "IA", "IB"]:
        score -= 5

    # Estado vital
    estado_vital = str(paciente.get("estado_vital", "")).upper()
    if estado_vital == "FALLECIDO":
        score = 100
        factores.append({"variable": "Estado vital", "valor": "Fallecido", "contribucion": 75, "direccion": "aumenta"})

    # === ARTRITIS REUMATOIDE ===

    # Adherencia porcentaje
    adherencia = paciente.get("adherencia_porcentaje", paciente.get("adherencia", None))
    if adherencia is not None and isinstance(adherencia, (int, float)):
        if adherencia < 60:
            contribucion = (80 - adherencia) * 0.5
            score += contribucion
            factores.append({"variable": "Adherencia", "valor": f"{adherencia}%", "contribucion": round(contribucion, 1), "direccion": "aumenta"})
        elif adherencia < 80:
            contribucion = (80 - adherencia) * 0.3
            score += contribucion
            factores.append({"variable": "Adherencia", "valor": f"{adherencia}%", "contribucion": round(contribucion, 1), "direccion": "aumenta"})
        elif adherencia >= 95:
            score -= 5

    # === HEMOFILIA ===

    # Episodios hemorragicos
    episodios = paciente.get("episodios_hemorragicos", None)
    if episodios is not None and isinstance(episodios, (int, float)):
        if episodios > 12:
            contribucion = min(25, episodios * 1.5)
            score += contribucion
            factores.append({"variable": "Episodios hemorragicos", "valor": str(int(episodios)), "contribucion": round(contribucion, 1), "direccion": "aumenta"})
        elif episodios > 6:
            contribucion = episodios * 0.8
            score += contribucion
            factores.append({"variable": "Episodios hemorragicos", "valor": str(int(episodios)), "contribucion": round(contribucion, 1), "direccion": "aumenta"})
        elif episodios <= 2:
            score -= 5

    # Consumo de factores
    consumo = paciente.get("factor_coagulacion_consumo_ui", None)
    if consumo is not None and isinstance(consumo, (int, float)):
        if consumo > 150000:
            contribucion = 12
            score += contribucion
            factores.append({"variable": "Consumo factores", "valor": f"{int(consumo)} UI", "contribucion": contribucion, "direccion": "aumenta"})

    # === HEPATITIS C ===

    # Respuesta virologica
    rvs = str(paciente.get("respuesta_virologica", "")).upper()
    if "SIN RVS" in rvs or "RECAIDA" in rvs:
        score += 20
        factores.append({"variable": "Respuesta virologica", "valor": "Sin RVS/Recaida", "contribucion": 20, "direccion": "aumenta"})
    elif "RVS" in rvs and "ALCANZADA" in rvs:
        score -= 15
        factores.append({"variable": "Respuesta virologica", "valor": "RVS alcanzada", "contribucion": -15, "direccion": "disminuye"})

    # Fibrosis
    evolucion = str(paciente.get("evolucion_clinica", "")).upper()
    if "F4" in evolucion or "CIRROSIS" in evolucion:
        score += 18
        factores.append({"variable": "Fibrosis", "valor": "F4/Cirrosis", "contribucion": 18, "direccion": "aumenta"})
    elif "F3" in evolucion:
        score += 10
        factores.append({"variable": "Fibrosis", "valor": "F3 avanzada", "contribucion": 10, "direccion": "aumenta"})

    # === NORMALIZAR Y CLASIFICAR ===
    score = max(0, min(100, score))

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


def calcular_riesgo_historico(df_historico: pd.DataFrame, col_periodo: str = "periodo") -> pd.DataFrame:
    """
    Calcula el riesgo para un DataFrame que contiene multiples periodos
    (meses) de un mismo paciente o grupo de pacientes.

    Args:
        df_historico: DataFrame con columna de periodo/mes y datos clinicos
        col_periodo: Nombre de la columna que identifica el periodo

    Returns:
        DataFrame con score_riesgo y nivel_riesgo por cada fila/periodo
    """
    df = df_historico.copy()
    scores = []
    niveles = []
    factores_list = []

    for _, row in df.iterrows():
        paciente = row.to_dict()
        score, nivel, factores = calcular_score_riesgo(paciente)
        scores.append(score)
        niveles.append(nivel)
        top3 = "; ".join([f"{f['variable']}={f['valor']}" for f in factores[:3]])
        factores_list.append(top3)

    df["score_riesgo"] = scores
    df["nivel_riesgo"] = niveles
    df["factores_riesgo"] = factores_list
    return df


def calcular_tendencia_paciente(scores_por_periodo: list) -> str:
    """
    Determina la tendencia de un paciente comparando su score actual
    con el periodo anterior.

    Args:
        scores_por_periodo: Lista de scores ordenados cronologicamente

    Returns:
        "AUMENTO", "DISMINUYO" o "ESTABLE"
    """
    if len(scores_por_periodo) < 2:
        return "SIN HISTORICO"

    actual = scores_por_periodo[-1]
    anterior = scores_por_periodo[-2]
    diferencia = actual - anterior

    if diferencia > 5:
        return "AUMENTO"
    elif diferencia < -5:
        return "DISMINUYO"
    else:
        return "ESTABLE"


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
