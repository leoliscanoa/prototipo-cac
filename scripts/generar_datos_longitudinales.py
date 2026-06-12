"""
=================================================================
GENERADOR DE DATOS LONGITUDINALES v3 - VOLUMEN MASIVO
=================================================================
Genera archivos .txt (tab-separated) con 50-200 pacientes por cohorte,
simulando evolucion clinica real a lo largo de 3 meses.

Dinamismo entre meses:
- Pacientes que DETERIORAN (valores empeoran)
- Pacientes que MEJORAN (respuesta a tratamiento)
- Pacientes ESTABLES (cronicos controlados)
- Pacientes con OUTLIERS (errores de dato)
- Pacientes que INGRESAN en mes 2 o 3 (nuevos en cohorte)
- Pacientes que EGRESAN (no aparecen en meses siguientes)

Volumen:
- ERC: Mes1=80, Mes2=95, Mes3=100 (ingresos y egresos)
- Cancer: Mes1=60, Mes2=70, Mes3=65 (ingresos y fallecimientos)
- VIH: Mes1=55, Mes2=60, Mes3=65 (ingresos progresivos)

Ejecucion:
    python scripts/generar_datos_longitudinales.py
=================================================================
"""

import csv
import os
import random
import numpy as np

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
    ruta = os.path.join(OUTPUT_DIR, nombre)
    with open(ruta, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        writer.writerow(cabeceras)
        for registro in registros:
            writer.writerow(registro)
    print(f"  {nombre} - {len(registros)} registros")


# =============================================================
# ERC / HTA / DM - ~80-100 pacientes
# =============================================================
def generar_erc():
    """
    Genera cohorte ERC con evolucion longitudinal.
    Mes1=80, Mes2=95 (+15 ingresos), Mes3=100 (+5 ingresos, 0 egresos por dialisis)
    Distribucion: 25% deterioro, 20% mejoria, 40% estables, 10% outliers, 5% ingresos tardios
    """
    cabeceras = [
        "TIPO_ID", "NUM_ID", "DX_ERC", "ESTADIO_ERC", "CREATININA",
        "TFG", "ALBUMINURIA", "PRESION_ARTERIAL", "DIABETES_ASOCIADA",
        "DIALISIS", "TRASPLANTE", "MEDICAMENTOS"
    ]

    np.random.seed(2026)
    random.seed(2026)

    medicamentos_erc = [
        "LOSARTAN METFORMINA", "ENALAPRIL INSULINA", "VALSARTAN AMLODIPINO",
        "LOSARTAN DAPAGLIFLOZINA", "IRBESARTAN METFORMINA", "HIDROCLOROTIAZIDA",
        "ENALAPRIL FUROSEMIDA", "LOSARTAN SITAGLIPTINA", "VALSARTAN EMPAGLIFLOZINA",
        "AMLODIPINO METFORMINA", "LOSARTAN INSULINA GLARGINA", "ENALAPRIL AMLODIPINO"
    ]

    meds_avanzado = [
        "ERITROPOYETINA BICARBONATO LOSARTAN", "DIALISIS ERITROPOYETINA CALCIO",
        "FUROSEMIDA ERITROPOYETINA BICARBONATO", "DIALISIS PERITONEAL EPO"
    ]

    # Base de pacientes: 100 pacientes totales, aparecen segun mes
    pacientes_base = []
    for i in range(100):
        doc = f"{7000000 + i}"
        tipo_id = random.choice(["CC", "CC", "CC", "CC", "TI", "CE"])

        # Perfil de evolucion
        if i < 20:
            perfil = "deterioro"
        elif i < 35:
            perfil = "mejoria"
        elif i < 70:
            perfil = "estable"
        elif i < 80:
            perfil = "outlier"
        elif i < 95:
            perfil = "ingreso_mes2"  # Aparecen desde mes 2
        else:
            perfil = "ingreso_mes3"  # Aparecen desde mes 3

        # Valores base
        edad = random.randint(35, 80)
        diabetes = "SI" if random.random() < 0.6 else "NO"

        if perfil == "deterioro":
            creat_base = round(random.uniform(1.5, 3.5), 2)
            tfg_base = round(random.uniform(20, 55), 1)
            alb_base = round(random.uniform(100, 400), 1)
            pas_base = random.randint(140, 175)
            pad_base = random.randint(88, 105)
        elif perfil == "mejoria":
            creat_base = round(random.uniform(1.3, 2.5), 2)
            tfg_base = round(random.uniform(35, 60), 1)
            alb_base = round(random.uniform(80, 250), 1)
            pas_base = random.randint(145, 165)
            pad_base = random.randint(90, 100)
        else:
            creat_base = round(random.uniform(0.8, 2.0), 2)
            tfg_base = round(random.uniform(45, 100), 1)
            alb_base = round(random.uniform(10, 150), 1)
            pas_base = random.randint(118, 145)
            pad_base = random.randint(72, 92)

        pacientes_base.append({
            "idx": i, "doc": doc, "tipo_id": tipo_id, "perfil": perfil,
            "creat_base": creat_base, "tfg_base": tfg_base, "alb_base": alb_base,
            "pas_base": pas_base, "pad_base": pad_base, "diabetes": diabetes,
        })

    # Generar registros por mes
    for mes in MESES:
        registros = []
        for p in pacientes_base:
            # Control de aparicion segun perfil
            if p["perfil"] == "ingreso_mes2" and mes["indice"] < 2:
                continue
            if p["perfil"] == "ingreso_mes3" and mes["indice"] < 3:
                continue

            m = mes["indice"]

            if p["perfil"] == "deterioro":
                # Creatinina sube, TFG baja cada mes
                creat = round(p["creat_base"] + (m - 1) * random.uniform(0.8, 1.8), 2)
                tfg = round(max(5, p["tfg_base"] - (m - 1) * random.uniform(8, 15)), 1)
                alb = round(p["alb_base"] + (m - 1) * random.uniform(50, 120), 1)
                pas = p["pas_base"] + (m - 1) * random.randint(3, 10)
                pad = p["pad_base"] + (m - 1) * random.randint(2, 6)
                dialisis = "SI" if (creat > 5.0 or tfg < 12) else "NO"
                meds = random.choice(meds_avanzado) if dialisis == "SI" else random.choice(medicamentos_erc)

            elif p["perfil"] == "mejoria":
                # Creatinina baja, TFG sube
                creat = round(max(0.7, p["creat_base"] - (m - 1) * random.uniform(0.2, 0.5)), 2)
                tfg = round(min(120, p["tfg_base"] + (m - 1) * random.uniform(5, 12)), 1)
                alb = round(max(10, p["alb_base"] - (m - 1) * random.uniform(30, 80)), 1)
                pas = max(110, p["pas_base"] - (m - 1) * random.randint(5, 12))
                pad = max(65, p["pad_base"] - (m - 1) * random.randint(3, 8))
                dialisis = "NO"
                meds = random.choice(medicamentos_erc)

            elif p["perfil"] == "outlier":
                if m == 2:
                    # MES 2: INYECTAR OUTLIER
                    outlier_type = random.choice(["creat_alta", "tfg_neg", "pa_imposible"])
                    if outlier_type == "creat_alta":
                        creat = random.choice([200, 150, 180, 250])
                    elif outlier_type == "tfg_neg":
                        creat = round(p["creat_base"], 2)
                        tfg = random.choice([-20, -15, -30])
                    else:
                        creat = round(p["creat_base"], 2)

                    if outlier_type != "tfg_neg":
                        tfg = round(p["tfg_base"], 1)
                    if outlier_type == "pa_imposible":
                        pas = random.choice([900, 500, 800])
                        pad = random.choice([400, 300, 500])
                    else:
                        pas = p["pas_base"]
                        pad = p["pad_base"]
                    alb = round(p["alb_base"], 1)
                    dialisis = "NO"
                    meds = random.choice(medicamentos_erc)
                else:
                    # Meses 1 y 3: datos normales
                    creat = round(p["creat_base"] + random.uniform(-0.1, 0.1), 2)
                    tfg = round(p["tfg_base"] + random.uniform(-2, 2), 1)
                    alb = round(p["alb_base"] + random.uniform(-10, 10), 1)
                    pas = p["pas_base"] + random.randint(-3, 3)
                    pad = p["pad_base"] + random.randint(-2, 2)
                    dialisis = "NO"
                    meds = random.choice(medicamentos_erc)
            else:
                # Estable o ingreso tardio: variacion minima
                creat = round(p["creat_base"] + random.uniform(-0.15, 0.15), 2)
                tfg = round(p["tfg_base"] + random.uniform(-3, 3), 1)
                alb = round(max(5, p["alb_base"] + random.uniform(-15, 15)), 1)
                pas = p["pas_base"] + random.randint(-4, 4)
                pad = p["pad_base"] + random.randint(-3, 3)
                dialisis = "NO"
                meds = random.choice(medicamentos_erc)

            # Determinar estadio por TFG
            if tfg >= 90:
                estadio, dx = "G1", "N18.1"
            elif tfg >= 60:
                estadio, dx = "G2", "N18.2"
            elif tfg >= 45:
                estadio, dx = "G3a", "N18.3"
            elif tfg >= 30:
                estadio, dx = "G3b", "N18.3"
            elif tfg >= 15:
                estadio, dx = "G4", "N18.4"
            else:
                estadio, dx = "G5", "N18.5"

            registros.append([
                p["tipo_id"], p["doc"], dx, estadio, str(creat), str(tfg),
                str(alb), f"{pas}/{pad}", p["diabetes"], dialisis, "NO", meds
            ])

        nombre = f"{mes['fecha']}_{CODIGO_EPS}_ERC_HTA_DM.txt"
        escribir_archivo(nombre, cabeceras, registros)


# =============================================================
# CANCER - ~60-70 pacientes
# =============================================================
def generar_cancer():
    """
    Genera cohorte Cancer con evolucion longitudinal.
    Mes1=60, Mes2=70 (+10 ingresos), Mes3=65 (5 fallecen, 0 nuevos)
    """
    cabeceras = [
        "TIPO_ID", "NUM_ID", "TIPO_CANCER", "FECHA_DX", "ESTADIO_CLINICO",
        "HISTOLOGIA", "RIESGO", "IPS_TRATANTE", "ESTADO_VITAL",
        "CIRUGIA", "QUIMIOTERAPIA", "RADIOTERAPIA", "MED_ONCOLOGICOS"
    ]

    np.random.seed(2027)
    random.seed(2027)

    tipos_cancer = ["MAMA", "PROSTATA", "COLON", "PULMON", "CERVIX", "GASTRICO"]
    histologias = {
        "MAMA": "CARCINOMA DUCTAL INFILTRANTE",
        "PROSTATA": "ADENOCARCINOMA ACINAR",
        "COLON": "ADENOCARCINOMA",
        "PULMON": "CARCINOMA CELULAS NO PEQUENAS",
        "CERVIX": "CARCINOMA ESCAMOSO",
        "GASTRICO": "ADENOCARCINOMA DIFUSO",
    }
    estadios_seq = ["I", "IIA", "IIB", "IIIA", "IIIB", "IV"]
    riesgo_map = {"I": "BAJO", "IIA": "INTERMEDIO", "IIB": "INTERMEDIO",
                  "IIIA": "ALTO", "IIIB": "MUY ALTO", "IV": "MUY ALTO"}
    ips_list = ["HOSPITAL KENNEDY", "CLINICA MARLY", "HOSPITAL SAN IGNACIO",
                "FUNDACION SANTA FE", "IPS COLSANITAS", "IPS NUEVA VIDA",
                "HOSPITAL EL TUNAL", "CLINICA COUNTRY"]
    meds_cancer = {
        "MAMA": ["TAMOXIFENO", "DOXORRUBICINA CICLOFOSFAMIDA", "PACLITAXEL", "TRASTUZUMAB", "LETROZOL"],
        "PROSTATA": ["VIGILANCIA ACTIVA", "BICALUTAMIDA", "ENZALUTAMIDA", "ABIRATERONA"],
        "COLON": ["CAPECITABINA", "FOLFOX", "FOLFIRI BEVACIZUMAB", "CETUXIMAB"],
        "PULMON": ["CISPLATINO PEMETREXED", "PEMBROLIZUMAB", "CARBOPLATINO", "OSIMERTINIB"],
        "CERVIX": ["CISPLATINO", "PACLITAXEL CARBOPLATINO", "BEVACIZUMAB"],
        "GASTRICO": ["CAPECITABINA", "TRASTUZUMAB", "FOLFOX", "RAMUCIRUMAB"],
    }

    # 75 pacientes base
    pacientes = []
    for i in range(75):
        doc = f"{8000000 + i}"
        tipo_id = random.choice(["CC", "CC", "CC", "TI", "CE"])
        tipo_cancer = random.choice(tipos_cancer)
        fecha_dx = f"202{random.randint(3,5)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

        if i < 15:
            perfil = "deterioro"
            estadio_idx = random.randint(3, 4)  # Empieza IIIA/IIIB
        elif i < 30:
            perfil = "mejoria"
            estadio_idx = random.randint(2, 3)  # Empieza IIB/IIIA
        elif i < 55:
            perfil = "estable"
            estadio_idx = random.randint(0, 2)  # I/IIA/IIB
        elif i < 60:
            perfil = "outlier"
            estadio_idx = random.randint(1, 3)
        elif i < 70:
            perfil = "ingreso_mes2"
            estadio_idx = random.randint(1, 3)
        else:
            perfil = "egreso_mes3"  # Fallecen en mes 3
            estadio_idx = random.randint(4, 5)

        pacientes.append({
            "doc": doc, "tipo_id": tipo_id, "tipo_cancer": tipo_cancer,
            "fecha_dx": fecha_dx, "perfil": perfil, "estadio_idx": estadio_idx,
        })

    for mes in MESES:
        registros = []
        for p in pacientes:
            if p["perfil"] == "ingreso_mes2" and mes["indice"] < 2:
                continue

            m = mes["indice"]
            tipo_cancer = p["tipo_cancer"]

            if p["perfil"] == "deterioro":
                # Progresa un estadio por mes
                idx = min(5, p["estadio_idx"] + (m - 1))
                estadio = estadios_seq[idx]
                estado_vital = "FALLECIDO" if (idx >= 5 and m == 3 and random.random() < 0.4) else "VIVO"
            elif p["perfil"] == "mejoria":
                # Baja un estadio
                idx = max(0, p["estadio_idx"] - (m - 1))
                estadio = estadios_seq[idx]
                estado_vital = "VIVO"
            elif p["perfil"] == "egreso_mes3":
                if m == 3:
                    estadio = "IV"
                    estado_vital = "FALLECIDO"
                else:
                    estadio = estadios_seq[p["estadio_idx"]]
                    estado_vital = "VIVO"
            elif p["perfil"] == "outlier" and m == 2:
                # Outlier: estadio imposible
                estadio = random.choice(["XV", "VII", "99"])
                estado_vital = "VIVO"
            else:
                estadio = estadios_seq[min(5, p["estadio_idx"])]
                estado_vital = "VIVO"

            riesgo = riesgo_map.get(estadio, "ALTO") if estadio in riesgo_map else ""
            cirugia = "SI" if random.random() < 0.5 else "NO"
            quimio = "SI" if random.random() < 0.6 else "NO"
            radio = "SI" if random.random() < 0.3 else "NO"
            med = random.choice(meds_cancer.get(tipo_cancer, ["QUIMIOTERAPIA"]))

            if estado_vital == "FALLECIDO":
                med = "PALIATIVO"

            registros.append([
                p["tipo_id"], p["doc"], tipo_cancer, p["fecha_dx"], estadio,
                histologias.get(tipo_cancer, "CARCINOMA"), riesgo,
                random.choice(ips_list), estado_vital,
                cirugia, quimio, radio, med
            ])

        nombre = f"{mes['fecha']}_{CODIGO_EPS}_CANCER.txt"
        escribir_archivo(nombre, cabeceras, registros)


# =============================================================
# VIH / SIDA - ~55-65 pacientes
# =============================================================
def generar_vih():
    """
    Genera cohorte VIH con evolucion longitudinal.
    Mes1=55, Mes2=60 (+5 ingresos), Mes3=65 (+5 ingresos)
    """
    cabeceras = [
        "TIPO_ID", "NUM_ID", "POBLACION_CLAVE", "FECHA_INICIO_TAR",
        "ESQUEMA_MED", "CARGA_VIRAL", "CD4", "PROFILAXIS",
        "COINFECCION_TB", "COINFECCION_HEPB", "COINFECCION_HEPC",
        "GESTANTE", "RESULTADO_PARTO", "SEGUIMIENTO_MENOR_12M"
    ]

    np.random.seed(2028)
    random.seed(2028)

    poblaciones = ["HETEROSEXUAL", "HSH", "TRANS", "UDI", "PERINATAL"]
    esquemas = ["TDF/FTC/DTG", "TAF/FTC/BIC", "ABC/3TC/DTG", "TDF/FTC/EFV", "AZT/3TC/LPV-r"]
    esquemas_rescate = ["DRV/r/DTG/TDF/FTC", "DRV/r/RAL/TDF/FTC", "DRV/r/ETV/TDF/FTC"]

    # 65 pacientes base
    pacientes = []
    for i in range(65):
        doc = f"{9000000 + i}"
        tipo_id = random.choice(["CC", "CC", "CC", "TI", "CE"])
        poblacion = random.choice(poblaciones)
        fecha_tar = f"202{random.randint(0,5)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

        if i < 12:
            perfil = "deterioro"
            cv_base = random.randint(500, 5000)
            cd4_base = random.randint(150, 350)
        elif i < 25:
            perfil = "mejoria"
            cv_base = random.randint(50000, 300000)
            cd4_base = random.randint(100, 250)
        elif i < 48:
            perfil = "estable"
            cv_base = 0  # indetectable
            cd4_base = random.randint(450, 900)
        elif i < 55:
            perfil = "outlier"
            cv_base = 0
            cd4_base = random.randint(400, 700)
        elif i < 60:
            perfil = "ingreso_mes2"
            cv_base = random.randint(100000, 500000)
            cd4_base = random.randint(80, 250)
        else:
            perfil = "ingreso_mes3"
            cv_base = random.randint(150000, 400000)
            cd4_base = random.randint(100, 200)

        gestante = "SI" if (random.random() < 0.08 and poblacion == "HETEROSEXUAL") else "NO"
        coinf_tb = "SI" if random.random() < 0.12 else "NO"
        coinf_hepb = "SI" if random.random() < 0.08 else "NO"
        coinf_hepc = "SI" if random.random() < 0.06 else "NO"

        pacientes.append({
            "doc": doc, "tipo_id": tipo_id, "poblacion": poblacion,
            "fecha_tar": fecha_tar, "perfil": perfil,
            "cv_base": cv_base, "cd4_base": cd4_base,
            "gestante": gestante, "coinf_tb": coinf_tb,
            "coinf_hepb": coinf_hepb, "coinf_hepc": coinf_hepc,
        })

    for mes in MESES:
        registros = []
        for p in pacientes:
            if p["perfil"] == "ingreso_mes2" and mes["indice"] < 2:
                continue
            if p["perfil"] == "ingreso_mes3" and mes["indice"] < 3:
                continue

            m = mes["indice"]

            if p["perfil"] == "deterioro":
                # CV sube, CD4 baja
                cv = int(p["cv_base"] * (3 ** (m - 1)))  # exponencial
                cd4 = max(20, p["cd4_base"] - (m - 1) * random.randint(40, 80))
                esquema = esquemas_rescate[0] if m == 3 else random.choice(esquemas)
                profilaxis = "TMP/SMX" if cd4 < 200 else "NO"
            elif p["perfil"] == "mejoria":
                # CV baja, CD4 sube
                if m == 1:
                    cv = p["cv_base"]
                elif m == 2:
                    cv = max(50, int(p["cv_base"] * 0.02))
                else:
                    cv = 0  # indetectable
                cd4 = p["cd4_base"] + (m - 1) * random.randint(60, 120)
                esquema = random.choice(esquemas[:3])
                profilaxis = "TMP/SMX" if (cd4 < 200 and m == 1) else "NO"
            elif p["perfil"] == "outlier" and m == 2:
                # Outlier en mes 2
                outlier_type = random.choice(["cv_texto", "cd4_neg", "cv_extremo"])
                if outlier_type == "cv_texto":
                    cv = "N/A"
                    cd4 = p["cd4_base"]
                elif outlier_type == "cd4_neg":
                    cv = 0
                    cd4 = random.choice([-50, -100, -30])
                else:
                    cv = 99999999
                    cd4 = p["cd4_base"]
                esquema = random.choice(esquemas)
                profilaxis = "NO"
                # Escribir y continuar
                cv_str = str(cv) if isinstance(cv, int) else cv
                registros.append([
                    p["tipo_id"], p["doc"], p["poblacion"], p["fecha_tar"],
                    esquema, cv_str, str(cd4), profilaxis,
                    p["coinf_tb"], p["coinf_hepb"], p["coinf_hepc"],
                    p["gestante"], "NO APLICA", "NO APLICA"
                ])
                continue
            else:
                # Estable o ingreso
                cv = 0
                cd4 = p["cd4_base"] + random.randint(-20, 20)
                esquema = random.choice(esquemas[:3])
                profilaxis = "NO"

            cv_str = "INDETECTABLE" if cv == 0 else str(cv)

            resultado_parto = "NO APLICA"
            seg_menor = "NO APLICA"
            if p["gestante"] == "SI" and m == 3:
                resultado_parto = "VIVO SIN VIH" if cv == 0 else "EN SEGUIMIENTO"
                seg_menor = "SI COMPLETO" if cv == 0 else "EN CURSO"

            registros.append([
                p["tipo_id"], p["doc"], p["poblacion"], p["fecha_tar"],
                esquema, cv_str, str(cd4), profilaxis,
                p["coinf_tb"], p["coinf_hepb"], p["coinf_hepc"],
                p["gestante"], resultado_parto, seg_menor
            ])

        nombre = f"{mes['fecha']}_{CODIGO_EPS}_VIH_SIDA.txt"
        escribir_archivo(nombre, cabeceras, registros)


# =============================================================
# ARTRITIS REUMATOIDE - ~50-60 pacientes
# =============================================================
def generar_artritis():
    """
    Genera cohorte Artritis Reumatoide con evolucion longitudinal.
    Mes1=50, Mes2=55 (+5 ingresos), Mes3=60 (+5 ingresos)
    """
    cabeceras = [
        "TIPO_ID", "NUM_ID", "DX_AR", "FECHA_DX", "ESTADO_FUNCIONAL",
        "ACTIVIDAD_ENFERMEDAD", "DMARD", "TERAPIA_BIOLOGICA",
        "EVENTOS_ADVERSOS", "CONTINUIDAD_TRATAMIENTO"
    ]

    np.random.seed(2029)
    random.seed(2029)

    dmards = ["METOTREXATO 15MG", "METOTREXATO 25MG", "LEFLUNOMIDA 20MG",
              "SULFASALAZINA 1G", "HIDROXICLOROQUINA 400MG"]
    biologicos = ["NO", "NO", "NO", "ADALIMUMAB", "RITUXIMAB",
                  "TOCILIZUMAB", "ETANERCEPT", "ABATACEPT"]
    eventos = ["NINGUNO", "NINGUNO", "NINGUNO", "NAUSEAS", "HEPATOTOXICIDAD",
               "INFECCION URINARIA", "NEUTROPENIA", "RETINOPATIA"]
    clases_func = ["CLASE I", "CLASE II", "CLASE III", "CLASE IV"]

    pacientes = []
    for i in range(60):
        doc = f"{3000000 + i}"
        tipo_id = random.choice(["CC", "CC", "CC", "TI", "CE"])
        fecha_dx = f"202{random.randint(0,4)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

        if i < 12:
            perfil = "deterioro"
            das28_base = round(random.uniform(3.5, 5.5), 1)
        elif i < 24:
            perfil = "mejoria"
            das28_base = round(random.uniform(4.0, 6.5), 1)
        elif i < 44:
            perfil = "estable"
            das28_base = round(random.uniform(2.0, 3.5), 1)
        elif i < 50:
            perfil = "outlier"
            das28_base = round(random.uniform(3.0, 4.5), 1)
        elif i < 55:
            perfil = "ingreso_mes2"
            das28_base = round(random.uniform(4.0, 6.0), 1)
        else:
            perfil = "ingreso_mes3"
            das28_base = round(random.uniform(5.0, 7.0), 1)

        pacientes.append({
            "doc": doc, "tipo_id": tipo_id, "fecha_dx": fecha_dx,
            "perfil": perfil, "das28_base": das28_base,
        })

    for mes in MESES:
        registros = []
        for p in pacientes:
            if p["perfil"] == "ingreso_mes2" and mes["indice"] < 2:
                continue
            if p["perfil"] == "ingreso_mes3" and mes["indice"] < 3:
                continue

            m = mes["indice"]

            if p["perfil"] == "deterioro":
                das28 = round(min(9.0, p["das28_base"] + (m - 1) * random.uniform(0.5, 1.5)), 1)
                clase = clases_func[min(3, 1 + (m - 1))]
                bio = random.choice(biologicos[3:]) if m >= 2 else "NO"
                evento = random.choice(eventos[3:]) if m == 3 else "NINGUNO"
                continuidad = f"CONTINUO {12 + (m-1)*3} MESES"
            elif p["perfil"] == "mejoria":
                das28 = round(max(1.5, p["das28_base"] - (m - 1) * random.uniform(0.8, 1.8)), 1)
                clase = clases_func[max(0, 2 - (m - 1))]
                bio = random.choice(biologicos[3:]) if p["das28_base"] > 5.0 else "NO"
                evento = "NINGUNO"
                continuidad = f"CONTINUO {6 + m*3} MESES"
            elif p["perfil"] == "outlier" and m == 2:
                # DAS28 imposible
                das28 = random.choice([15.0, -3.0, 25.0, 99.9])
                clase = "CLASE II"
                bio = "NO"
                evento = "NINGUNO"
                continuidad = "CONTINUO 12 MESES"
            else:
                das28 = round(p["das28_base"] + random.uniform(-0.3, 0.3), 1)
                clase = clases_func[0] if das28 < 2.6 else clases_func[1]
                bio = "NO"
                evento = "NINGUNO"
                continuidad = f"CONTINUO {random.randint(6, 48)} MESES"

            # Clasificar actividad
            if das28 < 2.6:
                actividad = f"DAS28 {das28} REMISION"
            elif das28 <= 3.2:
                actividad = f"DAS28 {das28} BAJA"
            elif das28 <= 5.1:
                actividad = f"DAS28 {das28} MODERADA"
            else:
                actividad = f"DAS28 {das28} ALTA"

            dmard = random.choice(dmards)
            dx = random.choice(["M05.9", "M06.0", "M05.8", "M06.9"])

            registros.append([
                p["tipo_id"], p["doc"], dx, p["fecha_dx"], clase,
                actividad, dmard, bio, evento, continuidad
            ])

        nombre = f"{mes['fecha']}_{CODIGO_EPS}_ARTRITIS_REUMATOIDE.txt"
        escribir_archivo(nombre, cabeceras, registros)


# =============================================================
# HEPATITIS C - ~50-60 pacientes
# =============================================================
def generar_hepatitis_c():
    """
    Genera cohorte Hepatitis C con evolucion longitudinal.
    Mes1=50, Mes2=55, Mes3=60
    """
    cabeceras = [
        "TIPO_ID", "NUM_ID", "DX_CONFIRMADO", "GENOTIPO_VIRAL",
        "MEDICAMENTO", "FECHA_INICIO_TRAT", "ADHERENCIA",
        "RESPUESTA_VIROLOGICA", "EVOLUCION_CLINICA", "REGISTRO_DISPENSACION"
    ]

    np.random.seed(2030)
    random.seed(2030)

    genotipos = ["1A", "1B", "2", "3", "4"]
    antivirales = ["SOFOSBUVIR/VELPATASVIR", "SOFOSBUVIR/LEDIPASVIR",
                   "GLECAPREVIR/PIBRENTASVIR", "ELBASVIR/GRAZOPREVIR"]
    fibrosis = ["F0 SIN FIBROSIS", "F1 FIBROSIS LEVE", "F2 FIBROSIS MODERADA",
                "F3 FIBROSIS AVANZADA", "F4 CIRROSIS COMPENSADA"]

    pacientes = []
    for i in range(60):
        doc = f"{5000000 + i}"
        tipo_id = random.choice(["CC", "CC", "CC", "TI", "CE"])
        genotipo = random.choice(genotipos)
        med = random.choice(antivirales)
        fecha_trat = f"202{random.randint(4,5)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

        if i < 12:
            perfil = "mejoria"  # Logran RVS
            semanas_base = random.randint(4, 8)
            adherencia_base = random.randint(90, 100)
        elif i < 20:
            perfil = "deterioro"  # No logran RVS
            semanas_base = random.randint(4, 8)
            adherencia_base = random.randint(55, 75)
        elif i < 42:
            perfil = "estable"  # En tratamiento o seguimiento
            semanas_base = random.randint(0, 12)
            adherencia_base = random.randint(80, 100)
        elif i < 50:
            perfil = "outlier"
            semanas_base = random.randint(4, 8)
            adherencia_base = 90
        elif i < 55:
            perfil = "ingreso_mes2"
            semanas_base = 0
            adherencia_base = 0
        else:
            perfil = "ingreso_mes3"
            semanas_base = 0
            adherencia_base = 0

        fib_idx = random.randint(0, 4)

        pacientes.append({
            "doc": doc, "tipo_id": tipo_id, "genotipo": genotipo,
            "med": med, "fecha_trat": fecha_trat, "perfil": perfil,
            "semanas_base": semanas_base, "adherencia_base": adherencia_base,
            "fib_idx": fib_idx,
        })

    for mes in MESES:
        registros = []
        for p in pacientes:
            if p["perfil"] == "ingreso_mes2" and mes["indice"] < 2:
                continue
            if p["perfil"] == "ingreso_mes3" and mes["indice"] < 3:
                continue

            m = mes["indice"]

            if p["perfil"] == "mejoria":
                semanas = p["semanas_base"] + (m - 1) * 4
                adherencia = p["adherencia_base"]
                if semanas >= 12:
                    respuesta = "RVS12 ALCANZADA"
                    evolucion = fibrosis[max(0, p["fib_idx"] - 1)]
                    dispensacion = f"COMPLETO {semanas} SEMANAS"
                else:
                    respuesta = f"EN TRATAMIENTO SEMANA {semanas}"
                    evolucion = fibrosis[p["fib_idx"]]
                    dispensacion = "EN CURSO"

            elif p["perfil"] == "deterioro":
                semanas = p["semanas_base"] + (m - 1) * 4
                adherencia = max(40, p["adherencia_base"] - (m - 1) * random.randint(5, 15))
                if m == 3:
                    respuesta = "SIN RVS RECAIDA"
                    evolucion = fibrosis[min(4, p["fib_idx"] + 1)]
                else:
                    respuesta = f"EN TRATAMIENTO SEMANA {semanas}"
                    evolucion = fibrosis[p["fib_idx"]]
                dispensacion = f"COMPLETO {semanas} SEMANAS" if semanas >= 12 else "EN CURSO"

            elif p["perfil"] == "outlier" and m == 2:
                # Outlier: adherencia imposible
                semanas = p["semanas_base"] + 4
                adherencia = random.choice([250, -10, 999])
                respuesta = "EN TRATAMIENTO SEMANA " + str(semanas)
                evolucion = fibrosis[p["fib_idx"]]
                dispensacion = "EN CURSO"

            else:
                semanas = p["semanas_base"] + (m - 1) * 4 if p["semanas_base"] > 0 else (m - 1) * 4
                adherencia = p["adherencia_base"] if p["adherencia_base"] > 0 else random.randint(85, 100)
                if semanas == 0:
                    respuesta = "PENDIENTE INICIO"
                    dispensacion = "PENDIENTE"
                elif semanas >= 12:
                    respuesta = "RVS12 ALCANZADA" if random.random() < 0.7 else "EN EVALUACION"
                    dispensacion = f"COMPLETO {semanas} SEMANAS"
                else:
                    respuesta = f"EN TRATAMIENTO SEMANA {semanas}"
                    dispensacion = "EN CURSO"
                evolucion = fibrosis[p["fib_idx"]]

            registros.append([
                p["tipo_id"], p["doc"], "B18.2", p["genotipo"],
                p["med"], p["fecha_trat"], str(adherencia),
                respuesta, evolucion, dispensacion
            ])

        nombre = f"{mes['fecha']}_{CODIGO_EPS}_HEPATITIS_C.txt"
        escribir_archivo(nombre, cabeceras, registros)


# =============================================================
# HEMOFILIA - ~50-55 pacientes
# =============================================================
def generar_hemofilia():
    """
    Genera cohorte Hemofilia con evolucion longitudinal.
    Mes1=50, Mes2=52, Mes3=55
    """
    cabeceras = [
        "TIPO_ID", "NUM_ID", "TIPO_HEMOFILIA", "FACTOR_DEFICIENTE",
        "SEVERIDAD", "INHIBIDORES", "EPISODIOS_HEMORRAGICOS",
        "PROFILAXIS", "TRATAMIENTO", "CONSUMO_FACTORES", "COMPLICACIONES"
    ]

    np.random.seed(2031)
    random.seed(2031)

    tipos = ["A", "A", "A", "A", "B"]  # 80% tipo A
    severidades = ["LEVE", "MODERADA", "SEVERA"]
    profilaxis_tipos = ["PROFILAXIS PRIMARIA", "PROFILAXIS SECUNDARIA", "A DEMANDA"]
    tratamientos_a = ["FACTOR VIII RECOMBINANTE", "FACTOR VIII PLASMATICO",
                      "FACTOR VIII VIDA MEDIA EXTENDIDA", "EMICIZUMAB"]
    tratamientos_b = ["FACTOR IX RECOMBINANTE", "FACTOR IX PLASMATICO",
                      "FACTOR IX VIDA MEDIA EXTENDIDA"]
    complicaciones = ["NINGUNA", "NINGUNA", "ARTROPATIA RODILLA", "ARTROPATIA CODO",
                      "ARTROPATIA TOBILLO", "HEMATOMA MUSCULAR", "ARTROPATIA MULTIPLE"]

    pacientes = []
    for i in range(55):
        doc = f"{6000000 + i}"
        tipo_id = random.choice(["CC", "CC", "CC", "TI"])
        tipo_hemo = random.choice(tipos)
        factor = "FACTOR VIII" if tipo_hemo == "A" else "FACTOR IX"
        severidad = random.choices(severidades, weights=[20, 30, 50])[0]

        if i < 10:
            perfil = "deterioro"
            episodios_base = random.randint(5, 12)
            consumo_base = random.randint(40000, 100000)
        elif i < 20:
            perfil = "mejoria"
            episodios_base = random.randint(8, 15)
            consumo_base = random.randint(50000, 120000)
        elif i < 42:
            perfil = "estable"
            episodios_base = random.randint(1, 6)
            consumo_base = random.randint(20000, 80000)
        elif i < 50:
            perfil = "outlier"
            episodios_base = random.randint(3, 8)
            consumo_base = random.randint(30000, 70000)
        elif i < 52:
            perfil = "ingreso_mes2"
            episodios_base = random.randint(5, 12)
            consumo_base = random.randint(40000, 90000)
        else:
            perfil = "ingreso_mes3"
            episodios_base = random.randint(8, 15)
            consumo_base = random.randint(60000, 100000)

        inhibidores = "POSITIVO" if random.random() < 0.12 else "NEGATIVO"
        profilaxis = random.choice(profilaxis_tipos)

        pacientes.append({
            "doc": doc, "tipo_id": tipo_id, "tipo_hemo": tipo_hemo,
            "factor": factor, "severidad": severidad, "perfil": perfil,
            "episodios_base": episodios_base, "consumo_base": consumo_base,
            "inhibidores": inhibidores, "profilaxis": profilaxis,
        })

    for mes in MESES:
        registros = []
        for p in pacientes:
            if p["perfil"] == "ingreso_mes2" and mes["indice"] < 2:
                continue
            if p["perfil"] == "ingreso_mes3" and mes["indice"] < 3:
                continue

            m = mes["indice"]

            if p["perfil"] == "deterioro":
                # Mas episodios, mas consumo
                episodios = p["episodios_base"] + (m - 1) * random.randint(2, 5)
                consumo = p["consumo_base"] + (m - 1) * random.randint(15000, 40000)
                compl = random.choice(complicaciones[2:])
            elif p["perfil"] == "mejoria":
                # Menos episodios con profilaxis adecuada
                episodios = max(0, p["episodios_base"] - (m - 1) * random.randint(2, 5))
                consumo = p["consumo_base"] + (m - 1) * random.randint(-5000, 10000)
                compl = "NINGUNA" if m == 3 else random.choice(complicaciones[:3])
            elif p["perfil"] == "outlier" and m == 2:
                # Outlier: consumo imposible o episodios negativos
                outlier_type = random.choice(["consumo_extremo", "episodios_neg"])
                if outlier_type == "consumo_extremo":
                    episodios = p["episodios_base"]
                    consumo = random.choice([999999, 800000, 1500000])
                else:
                    episodios = random.choice([-5, -10, -3])
                    consumo = p["consumo_base"]
                compl = "NINGUNA"
            else:
                # Estable
                episodios = p["episodios_base"] + random.randint(-1, 1)
                consumo = p["consumo_base"] + random.randint(-5000, 5000)
                compl = random.choice(complicaciones[:4])

            tratamiento = random.choice(tratamientos_a) if p["tipo_hemo"] == "A" else random.choice(tratamientos_b)
            # Emicizumab si tiene inhibidores
            if p["inhibidores"] == "POSITIVO" and p["tipo_hemo"] == "A":
                tratamiento = "EMICIZUMAB"

            registros.append([
                p["tipo_id"], p["doc"], p["tipo_hemo"], p["factor"],
                p["severidad"], p["inhibidores"], str(episodios),
                p["profilaxis"], tratamiento, str(consumo), compl
            ])

        nombre = f"{mes['fecha']}_{CODIGO_EPS}_HEMOFILIA.txt"
        escribir_archivo(nombre, cabeceras, registros)


# =============================================================
# EJECUCION
# =============================================================
def main():
    print("=" * 65)
    print(" GENERADOR DE DATOS LONGITUDINALES v3 - VOLUMEN MASIVO")
    print(" Periodo: Enero - Marzo 2026 | EPS: EPS001")
    print(" 6 cohortes x 3 meses = 18 archivos")
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

    print("--- ARTRITIS REUMATOIDE ---")
    generar_artritis()
    print()

    print("--- HEPATITIS C ---")
    generar_hepatitis_c()
    print()

    print("--- HEMOFILIA ---")
    generar_hemofilia()
    print()

    print("=" * 65)
    print(" RESUMEN:")
    print("  ERC:       80 -> 95 -> 100 pacientes")
    print("  Cancer:    65 -> 75 -> 75 pacientes")
    print("  VIH:       55 -> 60 -> 65 pacientes")
    print("  Artritis:  50 -> 55 -> 60 pacientes")
    print("  Hep C:     50 -> 55 -> 60 pacientes")
    print("  Hemofilia: 50 -> 52 -> 55 pacientes")
    print()
    print(f" 18 archivos en: {OUTPUT_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
