"""
Configuración general del ecosistema CAC Risk Management.
Contiene constantes, umbrales de validación y parámetros del sistema.
"""

# ============================================================
# INFORMACIÓN DE LA ENTIDAD
# ============================================================
CODIGO_EPS = "EPS001"
NOMBRE_EPS = "Prestador Uno"

# ============================================================
# REGLAS DE VALIDACIÓN - UMBRALES BIOLÓGICOS
# Estos valores representan límites biológicamente plausibles.
# Valores fuera de estos rangos generan alertas o bloqueos.
# ============================================================
REGLAS_VALIDACION = {
    "creatinina": {
        "min": 0.1,
        "max": 15.0,
        "unidad": "mg/dL",
        "accion": "bloquear",
        "mensaje": "Creatinina fuera de rango biológico plausible (0.1-15 mg/dL)"
    },
    "hemoglobina_glucosilada": {
        "min": 3.0,
        "max": 20.0,
        "valor_invalido": 0,
        "unidad": "%",
        "accion": "bloquear",
        "mensaje": "HbA1c no puede ser 0 ni superar 20%"
    },
    "tasa_filtracion_glomerular": {
        "min": 1.0,
        "max": 200.0,
        "unidad": "mL/min/1.73m²",
        "accion": "alerta",
        "mensaje": "TFG fuera de rango esperado"
    },
    "presion_arterial_sistolica": {
        "min": 50,
        "max": 300,
        "unidad": "mmHg",
        "accion": "alerta",
        "mensaje": "PAS fuera de rango fisiológico"
    },
    "presion_arterial_diastolica": {
        "min": 30,
        "max": 200,
        "unidad": "mmHg",
        "accion": "alerta",
        "mensaje": "PAD fuera de rango fisiológico"
    },
    "hemoglobina": {
        "min": 3.0,
        "max": 22.0,
        "unidad": "g/dL",
        "accion": "alerta",
        "mensaje": "Hemoglobina fuera de rango"
    },
    "cd4": {
        "min": 0,
        "max": 3000,
        "unidad": "células/µL",
        "accion": "alerta",
        "mensaje": "Conteo CD4 fuera de rango"
    },
    "carga_viral": {
        "min": 0,
        "max": 10000000,
        "unidad": "copias/mL",
        "accion": "alerta",
        "mensaje": "Carga viral fuera de rango"
    },
    "factor_coagulacion_consumo_ui": {
        "min": 0,
        "max": 500000,
        "unidad": "UI",
        "accion": "alerta",
        "mensaje": "Consumo de factor fuera de rango esperado"
    }
}

# ============================================================
# CLASIFICACIÓN KDIGO - ERC
# ============================================================
ESTADIOS_ERC_KDIGO = {
    "G1": {"tfg_min": 90, "tfg_max": 999, "descripcion": "Normal o alta", "color": "#2ecc71"},
    "G2": {"tfg_min": 60, "tfg_max": 89, "descripcion": "Ligeramente disminuida", "color": "#f1c40f"},
    "G3a": {"tfg_min": 45, "tfg_max": 59, "descripcion": "Ligera a moderadamente disminuida", "color": "#e67e22"},
    "G3b": {"tfg_min": 30, "tfg_max": 44, "descripcion": "Moderada a gravemente disminuida", "color": "#e74c3c"},
    "G4": {"tfg_min": 15, "tfg_max": 29, "descripcion": "Gravemente disminuida", "color": "#9b59b6"},
    "G5": {"tfg_min": 0, "tfg_max": 14, "descripcion": "Falla renal", "color": "#1a1a2e"},
}

ALBUMINURIA_KDIGO = {
    "A1": {"rango": "<30 mg/g", "descripcion": "Normal a ligeramente elevada"},
    "A2": {"rango": "30-300 mg/g", "descripcion": "Moderadamente elevada"},
    "A3": {"rango": ">300 mg/g", "descripcion": "Gravemente elevada"},
}

# ============================================================
# PATOLOGÍAS DISPONIBLES EN EL SISTEMA
# ============================================================
PATOLOGIAS = [
    "CANCER",
    "ERC_HTA_DM",
    "ARTRITIS_REUMATOIDE",
    "VIH_SIDA",
    "HEPATITIS_C",
    "HEMOFILIA"
]

# ============================================================
# PLACEHOLDER: CONEXIÓN A MODELOS PREDICTIVOS
# En futuras versiones, aquí se configurarán los endpoints
# de modelos de Machine Learning para predicción de:
# - Progresión renal
# - Riesgo cardiovascular
# - Falla terapéutica en VIH
# - Recaída en cáncer
# ============================================================
MODELOS_ML_CONFIG = {
    "habilitado": False,
    "endpoint_prediccion": None,
    "modelos_disponibles": []
}
