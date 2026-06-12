"""
=================================================================
ECOSISTEMA CAC RISK MANAGEMENT - MVP v2.0
=================================================================
Aplicacion web tipo SaaS para la Gestion de Riesgo en Salud,
Reportes a la Cuenta de Alto Costo (CAC) y operacion de las
Rutas Integrales de Atencion en Salud (RIAS) en Colombia.

Arquitectura de dos portales:
- Portal Prestador (IPS): Nivel operativo
- Portal Asegurador (EPS): Nivel estrategico y gestion del riesgo

Ejecutar con: streamlit run app.py
=================================================================
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Configuracion de la pagina
st.set_page_config(
    page_title="CAC Risk Management",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Paleta de colores institucional (salud) ---
st.markdown("""
<style>
    :root {
        --primary-blue: #1B4F72;
        --secondary-blue: #2980B9;
        --accent-green: #1E8449;
        --light-green: #D5F5E3;
        --light-blue: #D6EAF8;
        --alert-red: #C0392B;
        --alert-yellow: #F39C12;
        --neutral-gray: #F8F9FA;
    }
    [data-testid="stSidebar"] {
        background-color: #1B4F72;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stRadio label span {
        color: #D6EAF8 !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover span {
        color: #FFFFFF !important;
    }
    [data-testid="stMetric"] {
        background-color: #D6EAF8;
        border-left: 4px solid #1B4F72;
        padding: 12px 16px;
        border-radius: 4px;
    }
    [data-testid="stMetric"] label {
        color: #1B4F72 !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #1B4F72;
        border-color: #1B4F72;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2980B9;
        border-color: #2980B9;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        border-bottom-color: #1B4F72;
        color: #1B4F72;
    }
    .stSuccess {
        border-left-color: #1E8449;
    }
    h1, h2, h3 {
        color: #1B4F72 !important;
    }
</style>
""", unsafe_allow_html=True)

# Importar modulos
from modules.ingesta import renderizar_carga_masiva, renderizar_carga_individual
from modules.validacion import validar_dataframe, generar_reporte_validacion
from modules.exportacion import renderizar_exportacion
from modules.mapeo_columnas import normalizar_columnas
from modules.tablero_ips import renderizar_tablero_ips
from modules.gestion_cohortes import renderizar_gestion_cohortes
from modules.crm_clinico import renderizar_crm_clinico
from modules.tablero_modelo import renderizar_tablero_modelo
from modules.clinicos.cancer import renderizar_modulo_cancer
from modules.clinicos.erc import renderizar_modulo_erc
from modules.clinicos.artritis import renderizar_modulo_artritis
from modules.clinicos.vih import renderizar_modulo_vih
from modules.clinicos.hepatitis_c import renderizar_modulo_hepatitis_c
from modules.clinicos.hemofilia import renderizar_modulo_hemofilia
from config import PATOLOGIAS, CODIGO_EPS, NOMBRE_EPS


# ============================================================
# ESTADO DE SESION
# ============================================================
if "datos_cargados" not in st.session_state:
    st.session_state.datos_cargados = None
if "datos_validados" not in st.session_state:
    st.session_state.datos_validados = None
if "resultado_validacion" not in st.session_state:
    st.session_state.resultado_validacion = None
if "portal_activo" not in st.session_state:
    st.session_state.portal_activo = "IPS"


# ============================================================
# BARRA LATERAL
# ============================================================
with st.sidebar:
    st.title("CAC Risk Management")

    # Selector de portal
    portal = st.radio(
        "Portal",
        options=["Portal IPS (Prestador)", "Portal EPS (Asegurador)"],
        index=0,
        key="selector_portal"
    )

    # Nombre dinamico segun portal
    if portal == "Portal IPS (Prestador)":
        st.caption(NOMBRE_EPS)
    else:
        st.caption("EPS")
    st.divider()

    # Menu segun portal
    if portal == "Portal IPS (Prestador)":
        menu = st.radio(
            "Navegacion IPS",
            options=[
                "Tablero operativo",
                "Ingesta de datos",
                "Validacion y calidad",
                "Cancer",
                "ERC / HTA / DM",
                "Artritis reumatoide",
                "VIH / SIDA",
                "Hepatitis C",
                "Hemofilia",
            ],
            index=0
        )
    else:
        menu = st.radio(
            "Navegacion EPS",
            options=[
                "Dashboard estrategico",
                "Gestion de cohortes",
                "Intervencion clinica (CRM)",
                "Desempeno del modelo (IA)",
                "Exportacion CAC",
            ],
            index=0
        )

    st.divider()

    # Estado del sistema
    st.write("**Estado del sistema**")
    if st.session_state.datos_cargados is not None:
        st.success(f"Datos: {len(st.session_state.datos_cargados)} reg.")
    else:
        st.info("Sin datos cargados")

    if st.session_state.datos_validados is not None:
        st.success(f"Validados: {len(st.session_state.datos_validados)} reg.")

    st.divider()
    st.caption(f"v2.0.0 | {datetime.now().strftime('%Y-%m-%d')}")


# ============================================================
# CONTENIDO - PORTAL IPS
# ============================================================
if portal == "Portal IPS (Prestador)":

    if menu == "Tablero operativo":
        renderizar_tablero_ips()

    elif menu == "Ingesta de datos":
        st.title("Ingesta de datos")
        st.markdown("Cargue datos de pacientes en formato CSV o TXT delimitado por tabulaciones.")

        tab_masiva, tab_individual = st.tabs(["Carga masiva", "Registro individual"])

        with tab_masiva:
            df_cargado = renderizar_carga_masiva()
            if df_cargado is not None:
                df_cargado = normalizar_columnas(df_cargado)
                st.session_state.datos_cargados = df_cargado
                st.success("Datos almacenados en memoria. Proceda a validacion.")

        with tab_individual:
            patologia_sel = st.selectbox("Patologia", PATOLOGIAS, key="pat_ingesta")
            df_individual = renderizar_carga_individual(patologia_sel)
            if df_individual is not None:
                if st.session_state.datos_cargados is not None:
                    st.session_state.datos_cargados = pd.concat(
                        [st.session_state.datos_cargados, df_individual],
                        ignore_index=True
                    )
                else:
                    st.session_state.datos_cargados = df_individual
                st.success("Registro individual guardado.")

    elif menu == "Validacion y calidad":
        st.title("Motor de depuracion y validacion")
        st.markdown(
            "Evalua los datos antes de procesarlos. **Bloquea valores biologicamente imposibles** "
            "y genera alertas para valores atipicos."
        )

        if st.session_state.datos_cargados is None:
            st.warning("No hay datos cargados. Primero vaya al modulo de ingesta.")
        else:
            st.write(f"**Registros a validar:** {len(st.session_state.datos_cargados)}")

            campos_obligatorios = st.multiselect(
                "Campos obligatorios para validar:",
                options=st.session_state.datos_cargados.columns.tolist(),
                default=["documento"] if "documento" in st.session_state.datos_cargados.columns else []
            )

            if st.button("Ejecutar validacion", type="primary"):
                with st.spinner("Validando datos..."):
                    df_valido, resultado = validar_dataframe(
                        st.session_state.datos_cargados,
                        campos_requeridos=campos_obligatorios
                    )
                    st.session_state.datos_validados = df_valido
                    st.session_state.resultado_validacion = resultado

                st.divider()
                resumen = resultado.resumen

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total evaluados", len(st.session_state.datos_cargados))
                with col2:
                    st.metric("Validos", resumen["registros_validos"])
                with col3:
                    st.metric("Bloqueados", resumen["registros_bloqueados"])
                with col4:
                    st.metric("Con alertas", resumen["registros_con_alerta"])

                if resumen["aprobado"]:
                    st.success("Validacion aprobada. Todos los registros son validos.")
                else:
                    st.error(f"Se bloquearon {resumen['registros_bloqueados']} registros con errores criticos.")

                reporte_df = generar_reporte_validacion(resultado)
                if not reporte_df.empty:
                    st.subheader("Detalle de hallazgos")
                    st.dataframe(reporte_df, use_container_width=True, hide_index=True)

                st.subheader("Datos validados")
                st.dataframe(df_valido.head(20), use_container_width=True, hide_index=True)

    # --- Modulos clinicos ---
    elif menu == "Cancer":
        datos = st.session_state.datos_validados
        if datos is not None and not datos.empty and {"tipo_cancer", "estadio", "fecha_diagnostico"}.intersection(set(datos.columns)):
            renderizar_modulo_cancer(datos)
        else:
            renderizar_modulo_cancer(None)

    elif menu == "ERC / HTA / DM":
        datos = st.session_state.datos_validados
        if datos is not None and not datos.empty and {"creatinina", "tasa_filtracion_glomerular", "albuminuria"}.intersection(set(datos.columns)):
            renderizar_modulo_erc(datos)
        else:
            renderizar_modulo_erc(None)

    elif menu == "Artritis reumatoide":
        datos = st.session_state.datos_validados
        if datos is not None and not datos.empty and {"medicamento_dmard", "actividad_enfermedad", "terapia_biologica"}.intersection(set(datos.columns)):
            renderizar_modulo_artritis(datos)
        else:
            renderizar_modulo_artritis(None)

    elif menu == "VIH / SIDA":
        datos = st.session_state.datos_validados
        if datos is not None and not datos.empty and {"cd4", "carga_viral", "esquema_tar"}.intersection(set(datos.columns)):
            renderizar_modulo_vih(datos)
        else:
            renderizar_modulo_vih(None)

    elif menu == "Hepatitis C":
        datos = st.session_state.datos_validados
        if datos is not None and not datos.empty and {"genotipo", "medicamento_antiviral", "respuesta_virologica"}.intersection(set(datos.columns)):
            renderizar_modulo_hepatitis_c(datos)
        else:
            renderizar_modulo_hepatitis_c(None)

    elif menu == "Hemofilia":
        datos = st.session_state.datos_validados
        if datos is not None and not datos.empty and {"tipo_hemofilia", "factor_coagulacion_consumo_ui", "episodios_hemorragicos"}.intersection(set(datos.columns)):
            renderizar_modulo_hemofilia(datos)
        else:
            renderizar_modulo_hemofilia(None)


# ============================================================
# CONTENIDO - PORTAL EPS
# ============================================================
else:

    if menu == "Dashboard estrategico":
        st.title("Dashboard estrategico - Gestion del riesgo poblacional")
        st.markdown(
            "Vista consolidada para la toma de decisiones de la EPS. "
            "Ciclo RIAS: identificar, estratificar, intervenir, monitorear."
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pacientes en cohorte", "1,245")
        with col2:
            st.metric("Riesgo muy alto", "89")
        with col3:
            st.metric("Intervenciones mes", "342")
        with col4:
            st.metric("AUC modelo activo", "0.847")

        st.divider()

        st.subheader("Ciclo de gestion RIAS")
        st.markdown("""
        ```
        IDENTIFICAR  ->  ESTRATIFICAR  ->  INTERVENIR  ->  MONITOREAR  -> (ciclo)
        (Cohortes)      (Riesgo IA)      (CRM clinico)   (Indicadores)
        ```
        """)

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.info("**Gestion de cohortes:** Ingreso/egreso basado en score de elegibilidad")
        with col_b:
            st.info("**Riesgo dinamico:** Recalculo automatico con cada nuevo dato clinico")
        with col_c:
            st.info("**CRM clinico:** Prescripcion de acciones y trazabilidad de gestiones")
        with col_d:
            st.info("**Desempeno IA:** Metricas TRIPOD+AI, explicabilidad SHAP")

        st.subheader("Cohortes disponibles")
        patologias_info = {
            "Cancer": "Seguimiento, oportunidad diagnostica, trazabilidad de tratamientos",
            "ERC / HTA / DM": "Estratificacion KDIGO, alertas de progresion renal",
            "Artritis reumatoide": "Seguimiento farmacologico DMARD, adherencia",
            "VIH / SIDA": "Auditoria TAR, transmision materno-infantil, coinfecciones",
            "Hepatitis C": "Farmacoterapia AAD, integracion SIVIGILA",
            "Hemofilia": "Consumo de factores, episodios hemorragicos",
        }
        for nombre, desc in patologias_info.items():
            st.write(f"- **{nombre}:** {desc}")

    elif menu == "Gestion de cohortes":
        renderizar_gestion_cohortes()

    elif menu == "Intervencion clinica (CRM)":
        renderizar_crm_clinico()

    elif menu == "Desempeno del modelo (IA)":
        renderizar_tablero_modelo()

    elif menu == "Exportacion CAC":
        st.title("Consolidacion y exportacion CAC")
        st.markdown(
            "Genera archivos `.txt` delimitados por tabulaciones para reporte a la "
            "Cuenta de Alto Costo. Formato: `AAAAMMDD_CODEPS_[PATOLOGIA].txt`"
        )
        patologia_export = st.selectbox(
            "Seleccione la patologia para exportar:",
            PATOLOGIAS,
            key="pat_export"
        )
        renderizar_exportacion(st.session_state.datos_validados, patologia_export)
