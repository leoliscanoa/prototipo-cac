"""
=================================================================
GENERADOR DE DATOS LONGITUDINALES - EVOLUCION CLINICA 3 MESES
=================================================================
Genera archivos .txt (tab-separated) que simulan la evolucion
clinica de los mismos pacientes a lo largo de 3 meses consecutivos
(Enero, Febrero, Marzo 2026).

Logica de evolucion por paciente:
- Paciente 1: DETERIORO/PROGRESION (empeora mes a mes)
- Paciente 2: MEJORIA/ADHERENCIA (mejora con tratamiento)
- Paciente 3: ESTABILIDAD (cronico controlado, sin cambios)
- Paciente 4: OUTLIER (datos normales en M1/M3, error en M2)

Patologias: ERC_HTA_DM, CANCER, VIH_SIDA
Total archivos: 9 (3 meses x 3 patologias)

Ejecucion:
    python scripts/generar_datos_longitudinales.py
=================================================================
"""

import csv
import os

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "longitudinal"
)

MESES = [
    {"fecha": "20260131", "nombre": "Enero 2026", "indice": 1},
    {"fecha": "20260228", "nombre": "Febrero 2026", "indice": 2},
    {"fecha": "20260331", "nombre": "Marzo 2026", "indice": 3},
]

CODIGO_EPS = "EPS001"


def asegurar_directorio():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def escribir_archivo(nombre: str, cabeceras: list, registros: list):
    """Escribe archivo .txt tab-separated sin comillas."""
    ruta = os.path.join(OUTPUT_DIR, nombre)
    with open(ruta, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        writer.writerow(cabeceras)
        for registro in registros:
            writer.writerow(registro)
    print(f"  {nombre} - {len(registros)} registros")


# =============================================================
# ERC / HTA / DM
# =============================================================
def generar_erc():
    """
    Genera 3 archivos mensuales de ERC/HTA/DM con evolucion clinica.

    Pacientes:
    - 7001001: DETERIORO - Progresion renal (G3a -> G4 -> G5 + dialisis)
    - 7001002: MEJORIA - Control metabolico mejora con tratamiento
    - 7001003: ESTABILIDAD - Cronico controlado sin cambios
    - 7001004: OUTLIER - Mes 2 inyecta Creatinina=200 (imposible)
    """
    cabeceras = [
        "TIPO_ID", "NUM_ID", "DX_ERC", "ESTADIO_ERC", "CREATININA",
        "TFG", "ALBUMINURIA", "PRESION_ARTERIAL", "DIABETES_ASOCIADA",
        "DIALISIS", "TRASPLANTE", "MEDICAMENTOS"
    ]

    # Definicion de evolucion por mes [mes1, mes2, mes3]
    pacientes = {
        # --- PACIENTE 1: DETERIORO PROGRESIVO ---
        # Creatinina sube, TFG baja, inicia dialisis en mes 3
        "7001001": [
            # Mes 1: Estadio G3a, creatinina moderada
            ["CC", "7001001", "N18.3", "G3a", "1.8", "48.0", "150.0",
             "145/92", "SI", "NO", "NO", "LOSARTAN METFORMINA"],
            # Mes 2: Progresa a G4, creatinina sube
            ["CC", "7001001", "N18.4", "G4", "3.2", "22.0", "380.0",
             "155/98", "SI", "NO", "NO", "ENALAPRIL INSULINA ERITROPOYETINA"],
            # Mes 3: Progresa a G5, inicia dialisis
            ["CC", "7001001", "N18.5", "G5", "5.8", "9.0", "620.0",
             "165/105", "SI", "SI", "NO", "DIALISIS ERITROPOYETINA CALCIO"],
        ],
        # --- PACIENTE 2: MEJORIA CON ADHERENCIA ---
        # HTA controlada, albuminuria baja, TFG estable
        "7001002": [
            # Mes 1: Mal control, PA alta
            ["CC", "7001002", "N18.3", "G3a", "1.6", "52.0", "180.0",
             "160/100", "SI", "NO", "NO", "LOSARTAN"],
            # Mes 2: Inicia IECA+ARAII, mejora PA
            ["CC", "7001002", "N18.3", "G3a", "1.4", "55.0", "95.0",
             "138/85", "SI", "NO", "NO", "LOSARTAN AMLODIPINO METFORMINA"],
            # Mes 3: Control logrado, albuminuria en meta
            ["CC", "7001002", "N18.2", "G2", "1.2", "62.0", "28.0",
             "125/78", "SI", "NO", "NO", "LOSARTAN AMLODIPINO DAPAGLIFLOZINA"],
        ],
        # --- PACIENTE 3: ESTABILIDAD ---
        # Cronico controlado, valores estables
        "7001003": [
            # Mes 1
            ["CC", "7001003", "N18.2", "G2", "1.1", "72.0", "22.0",
             "128/80", "NO", "NO", "NO", "HIDROCLOROTIAZIDA"],
            # Mes 2 (sin cambios significativos)
            ["CC", "7001003", "N18.2", "G2", "1.0", "74.0", "20.0",
             "126/78", "NO", "NO", "NO", "HIDROCLOROTIAZIDA"],
            # Mes 3 (estable)
            ["CC", "7001003", "N18.2", "G2", "1.1", "71.0", "24.0",
             "130/82", "NO", "NO", "NO", "HIDROCLOROTIAZIDA"],
        ],
        # --- PACIENTE 4: OUTLIER EN MES 2 ---
        # Mes 1 y 3 normales; Mes 2 tiene CREATININA=200 (imposible)
        "7001004": [
            # Mes 1: Normal
            ["CC", "7001004", "N18.3", "G3b", "2.2", "35.0", "210.0",
             "142/88", "SI", "NO", "NO", "VALSARTAN SITAGLIPTINA"],
            # Mes 2: >>> OUTLIER: CREATININA=200, PRESION_ARTERIAL=900/500 <<<
            ["CC", "7001004", "N18.3", "G3b", "200", "35.0", "210.0",
             "900/500", "SI", "NO", "NO", "VALSARTAN SITAGLIPTINA"],
            # Mes 3: Normal de nuevo
            ["CC", "7001004", "N18.3", "G3b", "2.4", "33.0", "230.0",
             "145/90", "SI", "NO", "NO", "VALSARTAN SITAGLIPTINA FUROSEMIDA"],
        ],
    }

    for mes in MESES:
        nombre = f"{mes['fecha']}_{CODIGO_EPS}_ERC_HTA_DM.txt"
        registros = []
        for doc_id, evoluciones in pacientes.items():
            registros.append(evoluciones[mes["indice"] - 1])
        escribir_archivo(nombre, cabeceras, registros)


# =============================================================
# CANCER
# =============================================================
def generar_cancer():
    """
    Genera 3 archivos mensuales de Cancer con evolucion clinica.

    Pacientes:
    - 8001001: DETERIORO - Progresion de estadio, fallecimiento en mes 3
    - 8001002: MEJORIA - Respuesta a quimio, reduccion de riesgo
    - 8001003: ESTABILIDAD - En seguimiento post-cirugia, sin cambios
    - 8001004: OUTLIER - Mes 2 tiene ESTADIO_CLINICO="XV" (no existe)
    """
    cabeceras = [
        "TIPO_ID", "NUM_ID", "TIPO_CANCER", "FECHA_DX", "ESTADIO_CLINICO",
        "HISTOLOGIA", "RIESGO", "IPS_TRATANTE", "ESTADO_VITAL",
        "CIRUGIA", "QUIMIOTERAPIA", "RADIOTERAPIA", "MED_ONCOLOGICOS"
    ]

    pacientes = {
        # --- PACIENTE 1: DETERIORO - Progresion hasta fallecimiento ---
        "8001001": [
            # Mes 1: Estadio IIIA, en quimio
            ["CC", "8001001", "PULMON", "2025-08-15", "IIIA",
             "CARCINOMA CELULAS NO PEQUENAS", "ALTO", "HOSPITAL KENNEDY",
             "VIVO", "NO", "SI", "SI", "CISPLATINO PEMETREXED"],
            # Mes 2: Progresa a IIIB, agrega tratamiento
            ["CC", "8001001", "PULMON", "2025-08-15", "IIIB",
             "CARCINOMA CELULAS NO PEQUENAS", "MUY ALTO", "HOSPITAL KENNEDY",
             "VIVO", "NO", "SI", "SI", "PEMBROLIZUMAB CISPLATINO"],
            # Mes 3: Progresa a IV, fallecimiento
            ["CC", "8001001", "PULMON", "2025-08-15", "IV",
             "CARCINOMA CELULAS NO PEQUENAS", "MUY ALTO", "HOSPITAL KENNEDY",
             "FALLECIDO", "NO", "SI", "SI", "PALIATIVO"],
        ],
        # --- PACIENTE 2: MEJORIA - Respuesta al tratamiento ---
        "8001002": [
            # Mes 1: Estadio IIA mama, inicia quimio neoadyuvante
            ["CC", "8001002", "MAMA", "2025-10-01", "IIA",
             "CARCINOMA DUCTAL INFILTRANTE", "INTERMEDIO", "CLINICA MARLY",
             "VIVO", "NO", "SI", "NO", "DOXORRUBICINA CICLOFOSFAMIDA"],
            # Mes 2: Respuesta parcial, se programa cirugia
            ["CC", "8001002", "MAMA", "2025-10-01", "IIA",
             "CARCINOMA DUCTAL INFILTRANTE", "INTERMEDIO", "CLINICA MARLY",
             "VIVO", "SI", "SI", "NO", "PACLITAXEL"],
            # Mes 3: Post-cirugia exitosa, riesgo baja
            ["CC", "8001002", "MAMA", "2025-10-01", "I",
             "CARCINOMA DUCTAL INFILTRANTE", "BAJO", "CLINICA MARLY",
             "VIVO", "SI", "SI", "SI", "TAMOXIFENO"],
        ],
        # --- PACIENTE 3: ESTABILIDAD - Seguimiento sin cambios ---
        "8001003": [
            # Mes 1
            ["CC", "8001003", "PROSTATA", "2024-03-20", "I",
             "ADENOCARCINOMA ACINAR", "BAJO", "IPS COLSANITAS",
             "VIVO", "SI", "NO", "NO", "VIGILANCIA ACTIVA"],
            # Mes 2
            ["CC", "8001003", "PROSTATA", "2024-03-20", "I",
             "ADENOCARCINOMA ACINAR", "BAJO", "IPS COLSANITAS",
             "VIVO", "SI", "NO", "NO", "VIGILANCIA ACTIVA"],
            # Mes 3
            ["CC", "8001003", "PROSTATA", "2024-03-20", "I",
             "ADENOCARCINOMA ACINAR", "BAJO", "IPS COLSANITAS",
             "VIVO", "SI", "NO", "NO", "VIGILANCIA ACTIVA"],
        ],
        # --- PACIENTE 4: OUTLIER EN MES 2 ---
        # Mes 2: ESTADIO_CLINICO="XV" (no existe en TNM)
        "8001004": [
            # Mes 1: Normal
            ["CC", "8001004", "COLON", "2025-06-10", "II",
             "ADENOCARCINOMA MUCINOSO", "INTERMEDIO", "HOSPITAL SAN IGNACIO",
             "VIVO", "SI", "SI", "NO", "CAPECITABINA"],
            # Mes 2: >>> OUTLIER: ESTADIO_CLINICO="XV", RIESGO vacio <<<
            ["CC", "8001004", "COLON", "2025-06-10", "XV",
             "ADENOCARCINOMA MUCINOSO", "", "HOSPITAL SAN IGNACIO",
             "VIVO", "SI", "SI", "NO", "CAPECITABINA"],
            # Mes 3: Normal
            ["CC", "8001004", "COLON", "2025-06-10", "II",
             "ADENOCARCINOMA MUCINOSO", "INTERMEDIO", "HOSPITAL SAN IGNACIO",
             "VIVO", "SI", "SI", "NO", "CAPECITABINA BEVACIZUMAB"],
        ],
    }

    for mes in MESES:
        nombre = f"{mes['fecha']}_{CODIGO_EPS}_CANCER.txt"
        registros = []
        for doc_id, evoluciones in pacientes.items():
            registros.append(evoluciones[mes["indice"] - 1])
        escribir_archivo(nombre, cabeceras, registros)


# =============================================================
# VIH / SIDA
# =============================================================
def generar_vih():
    """
    Genera 3 archivos mensuales de VIH/SIDA con evolucion clinica.

    Pacientes:
    - 9001001: DETERIORO - Falla virologica progresiva (CV sube, CD4 baja)
    - 9001002: MEJORIA - Supresion viral lograda con TAR
    - 9001003: ESTABILIDAD - Paciente suprimido estable
    - 9001004: OUTLIER - Mes 2 tiene CARGA_VIRAL="N/A" (texto invalido)
    """
    cabeceras = [
        "TIPO_ID", "NUM_ID", "POBLACION_CLAVE", "FECHA_INICIO_TAR",
        "ESQUEMA_MED", "CARGA_VIRAL", "CD4", "PROFILAXIS",
        "COINFECCION_TB", "COINFECCION_HEPB", "COINFECCION_HEPC",
        "GESTANTE", "RESULTADO_PARTO", "SEGUIMIENTO_MENOR_12M"
    ]

    pacientes = {
        # --- PACIENTE 1: DETERIORO - Falla virologica ---
        # CV sube progresivamente, CD4 cae -> falla TAR
        "9001001": [
            # Mes 1: Viremia baja, sospecha de falla
            ["CC", "9001001", "HETEROSEXUAL", "2023-05-10",
             "TDF/FTC/EFV", "850", "280", "TMP/SMX",
             "NO", "NO", "NO", "NO", "NO APLICA", "NO APLICA"],
            # Mes 2: CV sube, falla confirmada
            ["CC", "9001001", "HETEROSEXUAL", "2023-05-10",
             "TDF/FTC/EFV", "45000", "195", "TMP/SMX",
             "NO", "NO", "NO", "NO", "NO APLICA", "NO APLICA"],
            # Mes 3: Falla franca, switch a esquema de rescate
            ["CC", "9001001", "HETEROSEXUAL", "2023-05-10",
             "DRV/r/DTG/TDF/FTC", "125000", "120", "TMP/SMX FLUCONAZOL",
             "SI", "NO", "NO", "NO", "NO APLICA", "NO APLICA"],
        ],
        # --- PACIENTE 2: MEJORIA - Supresion lograda ---
        # Inicia TAR con CV alta, logra indetectabilidad
        "9001002": [
            # Mes 1: Recien inicia TAR, CV alta
            ["CC", "9001002", "HSH", "2026-01-05",
             "TAF/FTC/BIC", "180000", "210", "TMP/SMX",
             "NO", "NO", "NO", "NO", "NO APLICA", "NO APLICA"],
            # Mes 2: CV en descenso
            ["CC", "9001002", "HSH", "2026-01-05",
             "TAF/FTC/BIC", "1200", "340", "TMP/SMX",
             "NO", "NO", "NO", "NO", "NO APLICA", "NO APLICA"],
            # Mes 3: Supresion lograda (indetectable <50)
            ["CC", "9001002", "HSH", "2026-01-05",
             "TAF/FTC/BIC", "INDETECTABLE", "450", "NO",
             "NO", "NO", "NO", "NO", "NO APLICA", "NO APLICA"],
        ],
        # --- PACIENTE 3: ESTABILIDAD - Suprimido estable ---
        "9001003": [
            # Mes 1
            ["CC", "9001003", "TRANS", "2022-08-20",
             "ABC/3TC/DTG", "INDETECTABLE", "680", "NO",
             "NO", "NO", "NO", "NO", "NO APLICA", "NO APLICA"],
            # Mes 2
            ["CC", "9001003", "TRANS", "2022-08-20",
             "ABC/3TC/DTG", "INDETECTABLE", "710", "NO",
             "NO", "NO", "NO", "NO", "NO APLICA", "NO APLICA"],
            # Mes 3
            ["CC", "9001003", "TRANS", "2022-08-20",
             "ABC/3TC/DTG", "INDETECTABLE", "695", "NO",
             "NO", "NO", "NO", "NO", "NO APLICA", "NO APLICA"],
        ],
        # --- PACIENTE 4: OUTLIER EN MES 2 ---
        # Mes 2: CARGA_VIRAL="N/A" (texto cuando debe ser numerico)
        #         CD4="-50" (valor negativo imposible)
        "9001004": [
            # Mes 1: Normal
            ["CC", "9001004", "HETEROSEXUAL", "2024-11-15",
             "TDF/FTC/DTG", "INDETECTABLE", "520", "NO",
             "NO", "SI", "NO", "NO", "NO APLICA", "NO APLICA"],
            # Mes 2: >>> OUTLIER: CARGA_VIRAL="N/A", CD4="-50" <<<
            ["CC", "9001004", "HETEROSEXUAL", "2024-11-15",
             "TDF/FTC/DTG", "N/A", "-50", "NO",
             "NO", "SI", "NO", "NO", "NO APLICA", "NO APLICA"],
            # Mes 3: Normal
            ["CC", "9001004", "HETEROSEXUAL", "2024-11-15",
             "TDF/FTC/DTG", "INDETECTABLE", "540", "NO",
             "NO", "SI", "NO", "NO", "NO APLICA", "NO APLICA"],
        ],
    }

    for mes in MESES:
        nombre = f"{mes['fecha']}_{CODIGO_EPS}_VIH_SIDA.txt"
        registros = []
        for doc_id, evoluciones in pacientes.items():
            registros.append(evoluciones[mes["indice"] - 1])
        escribir_archivo(nombre, cabeceras, registros)


# =============================================================
# EJECUCION PRINCIPAL
# =============================================================
def main():
    print("=" * 65)
    print(" GENERADOR DE DATOS LONGITUDINALES - EVOLUCION 3 MESES")
    print(" Periodo: Enero - Marzo 2026 | EPS: EPS001")
    print("=" * 65)
    print()

    asegurar_directorio()
    print(f"Directorio: {OUTPUT_DIR}")
    print()

    print("--- ERC / HTA / DM ---")
    generar_erc()
    print()

    print("--- CANCER ---")
    generar_cancer()
    print()

    print("--- VIH / SIDA ---")
    generar_vih()
    print()

    print("=" * 65)
    print(" RESUMEN DE EVOLUCION CLINICA PROGRAMADA")
    print("=" * 65)
    print()
    print("  ERC_HTA_DM:")
    print("    7001001 - DETERIORO: G3a(1.8) -> G4(3.2) -> G5(5.8)+Dialisis")
    print("    7001002 - MEJORIA: PA 160/100 -> 138/85 -> 125/78, Alb baja")
    print("    7001003 - ESTABLE: G2 mantenido, sin cambios")
    print("    7001004 - OUTLIER MES 2: Creatinina=200, PA=900/500")
    print()
    print("  CANCER:")
    print("    8001001 - DETERIORO: IIIA -> IIIB -> IV + Fallecimiento")
    print("    8001002 - MEJORIA: IIA + Quimio -> Cirugia -> I (Bajo riesgo)")
    print("    8001003 - ESTABLE: Prostata I, vigilancia activa")
    print("    8001004 - OUTLIER MES 2: Estadio=XV (no existe), Riesgo vacio")
    print()
    print("  VIH_SIDA:")
    print("    9001001 - DETERIORO: CV 850 -> 45000 -> 125000, CD4 baja")
    print("    9001002 - MEJORIA: CV 180000 -> 1200 -> Indetectable")
    print("    9001003 - ESTABLE: Indetectable sostenido")
    print("    9001004 - OUTLIER MES 2: CV='N/A' (texto), CD4=-50")
    print()
    print(f" 9 archivos generados en: {OUTPUT_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
