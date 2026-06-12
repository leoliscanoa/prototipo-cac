"""
Módulo de Mapeo de Columnas.

Normaliza las cabeceras de los archivos CAC (que vienen con nombres
abreviados y en mayúsculas) a los nombres internos que usan los
módulos clínicos del sistema.

Esto permite que los archivos generados según la nomenclatura CAC
funcionen directamente con los dashboards clínicos.
"""

import pandas as pd

# Mapeo de nombres de columna: clave = nombre CAC (lowercase), valor = nombre interno
MAPEO_COLUMNAS = {
    # --- Identificación ---
    "tipo_id": "tipo_documento",
    "num_id": "documento",

    # --- ERC / HTA / DM ---
    "dx_erc": "diagnostico_erc",
    "estadio_erc": "estadio_erc",
    "creatinina": "creatinina",
    "tfg": "tasa_filtracion_glomerular",
    "albuminuria": "albuminuria",
    "presion_arterial": "presion_arterial",
    "diabetes_asociada": "diabetes",
    "dialisis": "dialisis",
    "trasplante": "trasplante",
    "medicamentos": "medicamentos",

    # --- Cáncer ---
    "tipo_cancer": "tipo_cancer",
    "fecha_dx": "fecha_diagnostico",
    "estadio_clinico": "estadio",
    "histologia": "histologia",
    "riesgo": "riesgo",
    "ips_tratante": "ips_tratante",
    "estado_vital": "estado_vital",
    "cirugia": "cirugia",
    "quimioterapia": "quimioterapia",
    "radioterapia": "radioterapia",
    "med_oncologicos": "tratamiento_actual",

    # --- VIH / SIDA ---
    "poblacion_clave": "poblacion_clave",
    "fecha_inicio_tar": "fecha_inicio_tar",
    "esquema_med": "esquema_tar",
    "carga_viral": "carga_viral",
    "cd4": "cd4",
    "profilaxis": "profilaxis",
    "coinfeccion_tb": "coinfeccion_tb",
    "coinfeccion_hepb": "coinfeccion_hepb",
    "coinfeccion_hepc": "coinfeccion_hepc",
    "gestante": "gestante",
    "resultado_parto": "resultado_parto",
    "seguimiento_menor_12m": "seguimiento_menor_12m",

    # --- Artritis Reumatoide ---
    "dx_ar": "diagnostico_ar",
    "estado_funcional": "estado_funcional",
    "actividad_enfermedad": "actividad_enfermedad",
    "dmard": "medicamento_dmard",
    "terapia_biologica": "terapia_biologica",
    "eventos_adversos": "eventos_adversos",
    "continuidad_tratamiento": "continuidad_tratamiento",

    # --- Hepatitis C ---
    "dx_confirmado": "diagnostico_hepc",
    "genotipo_viral": "genotipo",
    "medicamento": "medicamento_antiviral",
    "fecha_inicio_trat": "fecha_inicio_tratamiento",
    "adherencia": "adherencia_porcentaje",
    "respuesta_virologica": "respuesta_virologica",
    "evolucion_clinica": "evolucion_clinica",
    "registro_dispensacion": "registro_dispensacion",

    # --- Hemofilia ---
    "tipo_hemofilia": "tipo_hemofilia",
    "factor_deficiente": "factor_deficiente",
    "severidad": "severidad",
    "inhibidores": "inhibidores",
    "episodios_hemorragicos": "episodios_hemorragicos",
    "profilaxis": "tipo_profilaxis",
    "tratamiento": "tratamiento",
    "consumo_factores": "factor_coagulacion_consumo_ui",
    "complicaciones": "complicaciones",
}


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica el mapeo de columnas al DataFrame.
    Convierte cabeceras CAC a nombres internos del sistema.

    Args:
        df: DataFrame con columnas en formato CAC (ya en lowercase por ingesta)

    Returns:
        DataFrame con columnas renombradas al formato interno
    """
    # Las columnas ya llegan en lowercase por el módulo de ingesta
    columnas_actuales = df.columns.tolist()
    renombrar = {}

    for col in columnas_actuales:
        if col in MAPEO_COLUMNAS:
            renombrar[col] = MAPEO_COLUMNAS[col]

    if renombrar:
        df = df.rename(columns=renombrar)

    return df
