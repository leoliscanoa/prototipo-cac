"""
=================================================================
GENERADOR DE DATOS DE PRUEBA (MOCK DATA) - CAC Risk Management
=================================================================
Script de QA que genera 6 archivos .txt delimitados por tabulaciones,
uno por cada cohorte exigida por la Cuenta de Alto Costo.

Cada archivo incluye:
- Registros válidos (Happy Path)
- Registros con outliers biológicamente imposibles (para validar motor de reglas)

Los outliers están marcados con comentarios en el código para trazabilidad.

Nomenclatura: AAAAMMDD_CODEPS_[PATOLOGIA].txt
Formato: Tab-separated, sin comillas, sin caracteres especiales.

Ejecución:
    python scripts/generar_datos_prueba.py

Autor: QA / Ingeniería de Datos
=================================================================
"""

import csv
import os
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================
FECHA = "20260611"
CODIGO_EPS = "EPS001"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "test")


def asegurar_directorio():
    """Crea el directorio de salida si no existe."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📁 Directorio de salida: {OUTPUT_DIR}")


def escribir_archivo(nombre_archivo: str, cabeceras: list, registros: list):
    """
    Escribe un archivo .txt delimitado por tabulaciones.
    Sin comillas (quoting=QUOTE_NONE), sin caracteres especiales.
    """
    ruta = os.path.join(OUTPUT_DIR, nombre_archivo)
    with open(ruta, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        writer.writerow(cabeceras)
        for registro in registros:
            writer.writerow(registro)
    print(f"  ✅ {nombre_archivo} — {len(registros)} registros generados")


# ============================================================
# 1. ARCHIVO CÁNCER
# ============================================================
def generar_cancer():
    nombre = f"{FECHA}_{CODIGO_EPS}_CANCER.txt"
    cabeceras = [
        "TIPO_ID", "NUM_ID", "TIPO_CANCER", "FECHA_DX", "ESTADIO_CLINICO",
        "HISTOLOGIA", "RIESGO", "IPS_TRATANTE", "ESTADO_VITAL",
        "CIRUGIA", "QUIMIOTERAPIA", "RADIOTERAPIA", "MED_ONCOLOGICOS"
    ]
    registros = [
        # --- REGISTROS VÁLIDOS (Happy Path) ---
        ["CC", "1001234501", "MAMA", "2025-03-15", "IIA",
         "CARCINOMA DUCTAL INFILTRANTE", "ALTO", "IPS SAN JOSE", "VIVO",
         "SI", "SI", "NO", "TAMOXIFENO"],

        ["CC", "1001234502", "PROSTATA", "2024-11-20", "I",
         "ADENOCARCINOMA ACINAR", "BAJO", "CLINICA MARLY", "VIVO",
         "SI", "NO", "SI", "BICALUTAMIDA"],

        ["CC", "1001234503", "COLON", "2025-01-08", "IIIB",
         "ADENOCARCINOMA MUCINOSO", "ALTO", "HOSPITAL KENNEDY", "VIVO",
         "SI", "SI", "NO", "CAPECITABINA"],

        ["TI", "1001234504", "CERVIX", "2024-08-10", "IIB",
         "CARCINOMA ESCAMOSO", "INTERMEDIO", "IPS NUEVA VIDA", "VIVO",
         "NO", "SI", "SI", "CISPLATINO"],

        ["CC", "1001234505", "PULMON", "2025-05-22", "IV",
         "CARCINOMA CELULAS PEQUENAS", "MUY ALTO", "FUNDACION SANTA FE", "VIVO",
         "NO", "SI", "SI", "PEMBROLIZUMAB"],

        ["CC", "1001234506", "GASTRICO", "2024-06-30", "IIIA",
         "ADENOCARCINOMA DIFUSO", "ALTO", "HOSPITAL SAN IGNACIO", "FALLECIDO",
         "SI", "SI", "NO", "TRASTUZUMAB"],

        ["CE", "1001234507", "MAMA", "2025-02-14", "IIB",
         "CARCINOMA LOBULILLAR", "INTERMEDIO", "CLINICA COUNTRY", "VIVO",
         "SI", "SI", "NO", "LETROZOL"],

        # --- REGISTRO CON DATOS INCOMPLETOS (para validar campos obligatorios) ---
        ["CC", "1001234508", "COLON", "2025-04-01", "",
         "", "ALTO", "IPS CENTRO MEDICO", "VIVO",
         "SI", "NO", "NO", "5-FLUOROURACILO"],

        # --- REGISTRO CON FECHA FUTURA IMPOSIBLE (outlier temporal) ---
        # >>> OUTLIER: FECHA_DX en el futuro lejano, imposible diagnóstico
        ["CC", "1001234509", "PULMON", "2030-12-31", "IV",
         "CARCINOMA NO MICROCÍTICO", "ALTO", "HOSPITAL EL TUNAL", "VIVO",
         "NO", "SI", "NO", "ERLOTINIB"],

        # --- REGISTRO CON ESTADIO INVÁLIDO (outlier clínico) ---
        # >>> OUTLIER: ESTADIO_CLINICO = "VII" no existe en TNM
        ["CC", "1001234510", "PROSTATA", "2025-01-15", "VII",
         "ADENOCARCINOMA", "BAJO", "IPS COLSANITAS", "VIVO",
         "SI", "NO", "NO", "ENZALUTAMIDA"],
    ]
    escribir_archivo(nombre, cabeceras, registros)


# ============================================================
# 2. ARCHIVO ERC / HTA / DM
# ============================================================
def generar_erc_hta_dm():
    nombre = f"{FECHA}_{CODIGO_EPS}_ERC_HTA_DM.txt"
    cabeceras = [
        "TIPO_ID", "NUM_ID", "DX_ERC", "ESTADIO_ERC", "CREATININA",
        "TFG", "ALBUMINURIA", "PRESION_ARTERIAL", "DIABETES_ASOCIADA",
        "DIALISIS", "TRASPLANTE", "MEDICAMENTOS"
    ]
    registros = [
        # --- REGISTROS VÁLIDOS (Happy Path) ---
        ["CC", "2001234501", "N18.3", "G3a", "1.8",
         "52.0", "45.0", "130/85", "SI",
         "NO", "NO", "LOSARTAN METFORMINA"],

        ["CC", "2001234502", "N18.4", "G4", "3.2",
         "24.0", "320.0", "150/95", "SI",
         "NO", "NO", "ENALAPRIL INSULINA GLARGINA"],

        ["CC", "2001234503", "N18.2", "G2", "1.1",
         "72.0", "18.0", "125/80", "NO",
         "NO", "NO", "AMLODIPINO"],

        ["TI", "2001234504", "N18.5", "G5", "6.8",
         "10.0", "580.0", "165/100", "SI",
         "SI", "NO", "ERITROPOYETINA CALCIO"],

        ["CC", "2001234505", "N18.1", "G1", "0.9",
         "95.0", "12.0", "120/78", "SI",
         "NO", "NO", "METFORMINA"],

        ["CC", "2001234506", "N18.3", "G3b", "2.4",
         "38.0", "180.0", "145/92", "SI",
         "NO", "NO", "VALSARTAN SITAGLIPTINA"],

        # >>> OUTLIER LÍNEA 8: CREATININA = 200 mg/dL (biológicamente imposible, máx ~15)
        ["CC", "2001234507", "N18.4", "G4", "200",
         "5.0", "400.0", "160/100", "SI",
         "SI", "NO", "FUROSEMIDA BICARBONATO"],

        # >>> OUTLIER LÍNEA 9: TFG = -15 (valor negativo imposible)
        ["CC", "2001234508", "N18.5", "G5", "8.5",
         "-15", "600.0", "175/110", "SI",
         "SI", "NO", "DIALISIS PERITONEAL"],

        # >>> OUTLIER LÍNEA 10: CREATININA = 0.01 (demasiado baja, sospechosa)
        ["CE", "2001234509", "N18.2", "G2", "0.01",
         "110.0", "10.0", "118/72", "NO",
         "NO", "NO", "HIDROCLOROTIAZIDA"],

        # --- REGISTRO VÁLIDO ADICIONAL ---
        ["CC", "2001234510", "N18.3", "G3a", "1.6",
         "48.0", "65.0", "138/88", "SI",
         "NO", "NO", "IRBESARTAN DAPAGLIFLOZINA"],
    ]
    escribir_archivo(nombre, cabeceras, registros)


# ============================================================
# 3. ARCHIVO ARTRITIS REUMATOIDE
# ============================================================
def generar_artritis():
    nombre = f"{FECHA}_{CODIGO_EPS}_ARTRITIS_REUMATOIDE.txt"
    cabeceras = [
        "TIPO_ID", "NUM_ID", "DX_AR", "FECHA_DX", "ESTADO_FUNCIONAL",
        "ACTIVIDAD_ENFERMEDAD", "DMARD", "TERAPIA_BIOLOGICA",
        "EVENTOS_ADVERSOS", "CONTINUIDAD_TRATAMIENTO"
    ]
    registros = [
        # --- REGISTROS VÁLIDOS (Happy Path) ---
        ["CC", "3001234501", "M05.9", "2022-03-10", "CLASE I",
         "DAS28 2.4 REMISION", "METOTREXATO 15MG SEMANAL", "NO",
         "NINGUNO", "CONTINUO 36 MESES"],

        ["CC", "3001234502", "M06.0", "2021-07-22", "CLASE II",
         "DAS28 3.8 MODERADA", "LEFLUNOMIDA 20MG DIARIO", "ADALIMUMAB",
         "INFECCION URINARIA", "CONTINUO 24 MESES"],

        ["CC", "3001234503", "M05.8", "2023-01-15", "CLASE II",
         "DAS28 4.5 MODERADA", "SULFASALAZINA 1G BID", "NO",
         "NAUSEAS", "CONTINUO 18 MESES"],

        ["TI", "3001234504", "M06.9", "2020-11-05", "CLASE III",
         "DAS28 6.2 ALTA", "METOTREXATO 25MG SEMANAL", "RITUXIMAB",
         "HEPATOTOXICIDAD", "CONTINUO 48 MESES"],

        ["CC", "3001234505", "M05.9", "2024-05-18", "CLASE I",
         "DAS28 1.9 REMISION", "METOTREXATO 10MG SEMANAL", "NO",
         "NINGUNO", "CONTINUO 12 MESES"],

        ["CC", "3001234506", "M06.0", "2023-09-01", "CLASE II",
         "DAS28 3.1 BAJA", "HIDROXICLOROQUINA 400MG", "NO",
         "RETINOPATIA LEVE", "CONTINUO 15 MESES"],

        # >>> OUTLIER LÍNEA 8: DAS28 = 15.0 (imposible, máximo teórico ~9.4)
        ["CC", "3001234507", "M05.9", "2024-02-20", "CLASE IV",
         "DAS28 15.0 ALTA", "METOTREXATO 25MG", "TOCILIZUMAB",
         "NEUTROPENIA SEVERA", "DISCONTINUO"],

        # >>> OUTLIER LÍNEA 9: ACTIVIDAD_ENFERMEDAD = DAS28 -3 (valor negativo imposible)
        ["CC", "3001234508", "M06.9", "2025-01-10", "CLASE I",
         "DAS28 -3 REMISION", "LEFLUNOMIDA 20MG", "NO",
         "NINGUNO", "CONTINUO 6 MESES"],

        # --- REGISTRO CON CAMPO VACÍO (para validar obligatoriedad) ---
        ["CC", "3001234509", "M05.8", "2024-08-12", "",
         "DAS28 4.0 MODERADA", "", "NO",
         "NINGUNO", "CONTINUO 10 MESES"],
    ]
    escribir_archivo(nombre, cabeceras, registros)


# ============================================================
# 4. ARCHIVO VIH / SIDA
# ============================================================
def generar_vih():
    nombre = f"{FECHA}_{CODIGO_EPS}_VIH_SIDA.txt"
    cabeceras = [
        "TIPO_ID", "NUM_ID", "POBLACION_CLAVE", "FECHA_INICIO_TAR",
        "ESQUEMA_MED", "CARGA_VIRAL", "CD4", "PROFILAXIS",
        "COINFECCION_TB", "COINFECCION_HEPB", "COINFECCION_HEPC",
        "GESTANTE", "RESULTADO_PARTO", "SEGUIMIENTO_MENOR_12M"
    ]
    registros = [
        # --- REGISTROS VÁLIDOS (Happy Path) ---
        ["CC", "4001234501", "HSH", "2023-06-15",
         "TDF/FTC/DTG", "INDETECTABLE", "520", "NO",
         "NO", "NO", "NO",
         "NO", "NO APLICA", "NO APLICA"],

        ["CC", "4001234502", "HETEROSEXUAL", "2022-01-20",
         "TDF/FTC/EFV", "48", "380", "TMP/SMX",
         "SI", "NO", "NO",
         "NO", "NO APLICA", "NO APLICA"],

        ["CC", "4001234503", "TRANS", "2024-03-10",
         "ABC/3TC/DTG", "INDETECTABLE", "650", "NO",
         "NO", "NO", "NO",
         "NO", "NO APLICA", "NO APLICA"],

        ["CC", "4001234504", "HETEROSEXUAL", "2021-09-05",
         "TAF/FTC/BIC", "INDETECTABLE", "780", "NO",
         "NO", "SI", "NO",
         "SI", "VIVO SIN VIH", "SI COMPLETO"],

        ["TI", "4001234505", "PERINATAL", "2020-04-18",
         "AZT/3TC/LPV-r", "250", "310", "TMP/SMX",
         "NO", "NO", "SI",
         "NO", "NO APLICA", "NO APLICA"],

        ["CC", "4001234506", "UDI", "2023-11-22",
         "TDF/FTC/DTG", "85000", "180", "TMP/SMX",
         "SI", "SI", "SI",
         "NO", "NO APLICA", "NO APLICA"],

        ["CC", "4001234507", "HETEROSEXUAL", "2024-08-01",
         "TAF/FTC/BIC", "INDETECTABLE", "420", "NO",
         "NO", "NO", "NO",
         "SI", "VIVO SIN VIH", "SI COMPLETO"],

        # >>> OUTLIER LÍNEA 9: CD4 = 5000 (biológicamente improbable, máx ~3000)
        ["CC", "4001234508", "HSH", "2025-02-14",
         "TDF/FTC/DTG", "INDETECTABLE", "5000", "NO",
         "NO", "NO", "NO",
         "NO", "NO APLICA", "NO APLICA"],

        # >>> OUTLIER LÍNEA 10: CARGA_VIRAL = 99999999 (extremadamente alta, sospechosa >10M)
        ["CC", "4001234509", "HETEROSEXUAL", "2024-05-30",
         "AZT/3TC/EFV", "99999999", "15", "TMP/SMX FLUCONAZOL",
         "SI", "NO", "NO",
         "NO", "NO APLICA", "NO APLICA"],

        # >>> OUTLIER LÍNEA 11: CD4 = -50 (valor negativo imposible)
        ["CE", "4001234510", "TRANS", "2025-01-10",
         "TDF/FTC/DTG", "350", "-50", "NO",
         "NO", "NO", "NO",
         "NO", "NO APLICA", "NO APLICA"],
    ]
    escribir_archivo(nombre, cabeceras, registros)


# ============================================================
# 5. ARCHIVO HEPATITIS C
# ============================================================
def generar_hepatitis_c():
    nombre = f"{FECHA}_{CODIGO_EPS}_HEPATITIS_C.txt"
    cabeceras = [
        "TIPO_ID", "NUM_ID", "DX_CONFIRMADO", "GENOTIPO_VIRAL",
        "MEDICAMENTO", "FECHA_INICIO_TRAT", "ADHERENCIA",
        "RESPUESTA_VIROLOGICA", "EVOLUCION_CLINICA", "REGISTRO_DISPENSACION"
    ]
    registros = [
        # --- REGISTROS VÁLIDOS (Happy Path) ---
        ["CC", "5001234501", "B18.2", "1A",
         "SOFOSBUVIR/VELPATASVIR", "2025-01-15", "100",
         "RVS12 ALCANZADA", "ESTABLE SIN FIBROSIS", "COMPLETO 12 SEMANAS"],

        ["CC", "5001234502", "B18.2", "1B",
         "SOFOSBUVIR/LEDIPASVIR", "2024-10-20", "95",
         "RVS12 ALCANZADA", "F2 FIBROSIS ESTABLE", "COMPLETO 12 SEMANAS"],

        ["CC", "5001234503", "B18.2", "3",
         "GLECAPREVIR/PIBRENTASVIR", "2025-03-01", "88",
         "EN TRATAMIENTO SEMANA 8", "F3 FIBROSIS AVANZADA", "EN CURSO"],

        ["TI", "5001234504", "B18.2", "2",
         "SOFOSBUVIR/VELPATASVIR", "2024-07-10", "100",
         "RVS12 ALCANZADA", "F1 FIBROSIS LEVE", "COMPLETO 12 SEMANAS"],

        ["CC", "5001234505", "B18.2", "4",
         "ELBASVIR/GRAZOPREVIR", "2025-02-28", "75",
         "SIN RVS RECAIDA", "F4 CIRROSIS COMPENSADA", "COMPLETO 12 SEMANAS"],

        ["CC", "5001234506", "B18.2", "1A",
         "SOFOSBUVIR/VELPATASVIR", "2025-04-10", "92",
         "EN TRATAMIENTO SEMANA 4", "F0 SIN FIBROSIS", "EN CURSO"],

        ["CC", "5001234507", "B18.2", "3",
         "GLECAPREVIR/PIBRENTASVIR", "2024-12-01", "100",
         "RVS24 ALCANZADA", "F2 FIBROSIS ESTABLE", "COMPLETO 16 SEMANAS"],

        # >>> OUTLIER LÍNEA 9: ADHERENCIA = 250% (imposible, máximo 100%)
        ["CC", "5001234508", "B18.2", "1B",
         "SOFOSBUVIR/LEDIPASVIR", "2025-05-01", "250",
         "EN TRATAMIENTO SEMANA 6", "F1 FIBROSIS LEVE", "EN CURSO"],

        # >>> OUTLIER LÍNEA 10: ADHERENCIA = -10 (valor negativo imposible)
        ["CE", "5001234509", "B18.2", "2",
         "SOFOSBUVIR/VELPATASVIR", "2025-03-20", "-10",
         "PENDIENTE EVALUACION", "F0 SIN FIBROSIS", "INCOMPLETO"],

        # --- REGISTRO CON GENOTIPO INVÁLIDO ---
        # >>> OUTLIER: GENOTIPO_VIRAL = "9" (solo existen genotipos 1-6)
        ["CC", "5001234510", "B18.2", "9",
         "GLECAPREVIR/PIBRENTASVIR", "2025-04-25", "90",
         "EN TRATAMIENTO SEMANA 2", "F1 FIBROSIS LEVE", "EN CURSO"],
    ]
    escribir_archivo(nombre, cabeceras, registros)


# ============================================================
# 6. ARCHIVO HEMOFILIA
# ============================================================
def generar_hemofilia():
    nombre = f"{FECHA}_{CODIGO_EPS}_HEMOFILIA.txt"
    cabeceras = [
        "TIPO_ID", "NUM_ID", "TIPO_HEMOFILIA", "FACTOR_DEFICIENTE",
        "SEVERIDAD", "INHIBIDORES", "EPISODIOS_HEMORRAGICOS",
        "PROFILAXIS", "TRATAMIENTO", "CONSUMO_FACTORES", "COMPLICACIONES"
    ]
    registros = [
        # --- REGISTROS VÁLIDOS (Happy Path) ---
        ["CC", "6001234501", "A", "FACTOR VIII",
         "SEVERA", "NEGATIVO", "8",
         "PROFILAXIS PRIMARIA", "FACTOR VIII RECOMBINANTE", "45000", "ARTROPATIA RODILLA"],

        ["CC", "6001234502", "A", "FACTOR VIII",
         "MODERADA", "NEGATIVO", "3",
         "PROFILAXIS SECUNDARIA", "FACTOR VIII PLASMATICO", "22000", "NINGUNA"],

        ["CC", "6001234503", "B", "FACTOR IX",
         "SEVERA", "POSITIVO 8 UB", "12",
         "PROFILAXIS PRIMARIA", "FACTOR IX RECOMBINANTE", "65000", "ARTROPATIA CODO"],

        ["TI", "6001234504", "A", "FACTOR VIII",
         "LEVE", "NEGATIVO", "1",
         "A DEMANDA", "DESMOPRESINA", "5000", "NINGUNA"],

        ["CC", "6001234505", "A", "FACTOR VIII",
         "SEVERA", "POSITIVO 25 UB", "15",
         "PROFILAXIS PRIMARIA", "EMICIZUMAB", "0", "ARTROPATIA TOBILLO RODILLA"],

        ["CC", "6001234506", "B", "FACTOR IX",
         "MODERADA", "NEGATIVO", "4",
         "PROFILAXIS SECUNDARIA", "FACTOR IX RECOMBINANTE", "35000", "HEMATOMA MUSCULAR"],

        ["CC", "6001234507", "A", "FACTOR VIII",
         "SEVERA", "NEGATIVO", "6",
         "PROFILAXIS PRIMARIA", "FACTOR VIII VIDA MEDIA EXTENDIDA", "80000", "ARTROPATIA CODO"],

        # >>> OUTLIER LÍNEA 9: CONSUMO_FACTORES = 999999 (>500000 UI, extremo)
        ["CC", "6001234508", "A", "FACTOR VIII",
         "SEVERA", "NEGATIVO", "20",
         "PROFILAXIS PRIMARIA", "FACTOR VIII RECOMBINANTE", "999999", "ARTROPATIA MULTIPLE"],

        # >>> OUTLIER LÍNEA 10: EPISODIOS_HEMORRAGICOS = -5 (valor negativo imposible)
        ["CC", "6001234509", "B", "FACTOR IX",
         "MODERADA", "NEGATIVO", "-5",
         "PROFILAXIS SECUNDARIA", "FACTOR IX PLASMATICO", "28000", "NINGUNA"],

        # >>> OUTLIER LÍNEA 11: CONSUMO_FACTORES = 0 con SEVERIDAD SEVERA y SIN Emicizumab
        # (inconsistencia clínica: paciente severo sin profilaxis alternativa con consumo 0)
        ["CE", "6001234510", "A", "FACTOR VIII",
         "SEVERA", "NEGATIVO", "18",
         "PROFILAXIS PRIMARIA", "FACTOR VIII RECOMBINANTE", "0", "HEMORRAGIA INTRACRANEAL"],
    ]
    escribir_archivo(nombre, cabeceras, registros)


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
def main():
    print("=" * 65)
    print(" GENERADOR DE DATOS DE PRUEBA - CAC RISK MANAGEMENT")
    print(f" Fecha: {FECHA} | EPS: {CODIGO_EPS}")
    print("=" * 65)
    print()

    asegurar_directorio()
    print()
    print("Generando archivos de prueba...")
    print()

    generar_cancer()
    generar_erc_hta_dm()
    generar_artritis()
    generar_vih()
    generar_hepatitis_c()
    generar_hemofilia()

    print()
    print("=" * 65)
    print(" RESUMEN DE OUTLIERS INYECTADOS")
    print("=" * 65)
    print()
    print("  📄 CANCER:")
    print("     - Fila 9: FECHA_DX = 2030-12-31 (fecha futura imposible)")
    print("     - Fila 10: ESTADIO_CLINICO = VII (no existe en TNM)")
    print()
    print("  📄 ERC_HTA_DM:")
    print("     - Fila 7: CREATININA = 200 mg/dL (máx biológico ~15)")
    print("     - Fila 8: TFG = -15 (valor negativo imposible)")
    print("     - Fila 9: CREATININA = 0.01 (sospechosamente baja)")
    print()
    print("  📄 ARTRITIS_REUMATOIDE:")
    print("     - Fila 7: DAS28 = 15.0 (máx teórico ~9.4)")
    print("     - Fila 8: DAS28 = -3 (valor negativo imposible)")
    print()
    print("  📄 VIH_SIDA:")
    print("     - Fila 8: CD4 = 5000 (máx esperado ~3000)")
    print("     - Fila 9: CARGA_VIRAL = 99999999 (extrema, >10M)")
    print("     - Fila 10: CD4 = -50 (valor negativo imposible)")
    print()
    print("  📄 HEPATITIS_C:")
    print("     - Fila 8: ADHERENCIA = 250% (máx 100%)")
    print("     - Fila 9: ADHERENCIA = -10 (valor negativo imposible)")
    print("     - Fila 10: GENOTIPO_VIRAL = 9 (solo existen 1-6)")
    print()
    print("  📄 HEMOFILIA:")
    print("     - Fila 8: CONSUMO_FACTORES = 999999 UI (>500000)")
    print("     - Fila 9: EPISODIOS_HEMORRAGICOS = -5 (negativo)")
    print("     - Fila 10: CONSUMO = 0 con SEVERA sin alternativa (inconsistencia)")
    print()
    print("=" * 65)
    print(f" ✅ 6 archivos generados en: {OUTPUT_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
