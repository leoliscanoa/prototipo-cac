"""
Modulo de Intervencion Clinica (CRM de Salud).

Permite a los gestores de la EPS:
- Ver alertas por nivel de riesgo y adherencia
- Registrar intervenciones (llamadas, SMS, correos, educacion)
- Programar acciones segun riesgo (rutinarias vs urgentes)
- Consultar trazabilidad cronologica de acciones por paciente

Usa datos reales del prestador cuando estan disponibles.
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import numpy as np

from modules.riesgo_dinamico import recalcular_riesgo_cohorte


def generar_log_intervenciones_demo() -> pd.DataFrame:
    """Genera datos demo del log de intervenciones."""
    np.random.seed(88)
    n = 30
    tipos_accion = ["Llamada telefonica", "Envio SMS", "Correo electronico",
                    "Educacion en salud", "Cita prioritaria", "Visita domiciliaria"]
    gestores = ["Ana Ruiz", "Carlos Pena", "Maria Lopez", "Pedro Diaz"]
    resultados = ["Contacto exitoso", "No contesta", "Mensaje dejado",
                  "Cita agendada", "Paciente informado"]
    datos = {
        "documento": [f"{10000000 + np.random.randint(0, 50)}" for _ in range(n)],
        "fecha_accion": [
            (datetime.now() - timedelta(days=np.random.randint(0, 60))).strftime("%Y-%m-%d %H:%M")
            for _ in range(n)
        ],
        "tipo_accion": np.random.choice(tipos_accion, n),
        "gestor": np.random.choice(gestores, n),
        "resultado": np.random.choice(resultados, n),
        "observaciones": [f"Seguimiento #{i+1}" for i in range(n)],
    }
    return pd.DataFrame(datos).sort_values("fecha_accion", ascending=False)


def generar_alertas_desde_datos(df: pd.DataFrame, historico: dict = None) -> pd.DataFrame:
    """
    Genera alertas reales basadas en los datos del prestador.
    Incluye indicador de tendencia si hay datos historicos.
    """
    alertas = []

    if "nivel_riesgo" not in df.columns:
        df = recalcular_riesgo_cohorte(df)

    # Calcular tendencia si hay historico
    tendencias = {}
    if historico and len(historico) >= 2:
        from modules.riesgo_dinamico import calcular_riesgo_historico, calcular_tendencia_paciente
        periodos = sorted(historico.keys())
        col_doc = "documento" if "documento" in df.columns else "num_id"

        # Calcular scores para periodos anteriores
        for doc in df[col_doc].unique():
            scores_pac = []
            for periodo in periodos:
                df_p = historico[periodo]
                col_doc_p = "documento" if "documento" in df_p.columns else "num_id"
                if col_doc_p in df_p.columns:
                    pac_p = df_p[df_p[col_doc_p] == doc]
                    if not pac_p.empty:
                        from modules.riesgo_dinamico import calcular_score_riesgo
                        score, _, _ = calcular_score_riesgo(pac_p.iloc[0].to_dict())
                        scores_pac.append(score)
            if scores_pac:
                tendencias[doc] = calcular_tendencia_paciente(scores_pac)

    # Pacientes de riesgo Alto/Muy Alto
    alto_riesgo = df[df["nivel_riesgo"].isin(["Alto", "Muy Alto"])]
    col_doc = "documento" if "documento" in df.columns else "num_id"

    for _, row in alto_riesgo.iterrows():
        doc = str(row.get(col_doc, "N/A"))
        nombre = row.get("nombres", f"Pac. {doc}")
        nivel = row["nivel_riesgo"]
        factores = row.get("factores_riesgo", "")
        score = row.get("score_riesgo", 0)

        # Tendencia
        tendencia = tendencias.get(doc, "SIN HISTORICO")
        if tendencia == "AUMENTO":
            indicador = "^ AUMENTO"
        elif tendencia == "DISMINUYO":
            indicador = "v DISMINUYO"
        elif tendencia == "ESTABLE":
            indicador = "= ESTABLE"
        else:
            indicador = "- Sin historico"

        if nivel == "Muy Alto":
            accion = "Cita prioritaria + intervencion multidisciplinaria"
        else:
            accion = "Cita prioritaria con especialista"

        alertas.append({
            "documento": doc,
            "nombres": nombre,
            "nivel_riesgo": nivel,
            "score": score,
            "tendencia": indicador,
            "alerta": f"Riesgo {nivel}: {factores}" if factores else f"Riesgo {nivel}",
            "accion_prescrita": accion,
        })

    if not alertas:
        return pd.DataFrame(columns=["documento", "nombres", "nivel_riesgo", "score",
                                     "tendencia", "alerta", "accion_prescrita"])

    return pd.DataFrame(alertas).sort_values("score", ascending=False).head(20)


def renderizar_crm_clinico(df_prestador: pd.DataFrame = None, historico: dict = None):
    """
    Renderiza el modulo CRM clinico para gestores EPS.
    Usa datos del prestador si estan disponibles.
    El historico permite mostrar tendencias de riesgo.
    """
    st.header("Intervencion clinica - CRM de salud")

    # Inicializar log en session state
    if "log_intervenciones" not in st.session_state:
        st.session_state.log_intervenciones = generar_log_intervenciones_demo()

    # Preparar datos con riesgo
    if df_prestador is not None and not df_prestador.empty:
        df_riesgo = df_prestador.copy()
        if "score_riesgo" not in df_riesgo.columns:
            df_riesgo = recalcular_riesgo_cohorte(df_riesgo)
        usando_demo = False
    else:
        df_riesgo = None
        usando_demo = True

    tab1, tab2, tab3 = st.tabs([
        "Alertas y prescripcion", "Registrar intervencion", "Trazabilidad (log)"
    ])

    with tab1:
        st.subheader("Alertas activas por nivel de riesgo")

        st.markdown("""
        **Reglas de prescripcion automatica:**
        - Riesgo Alto/Muy Alto: Cita prioritaria, intervencion multidisciplinaria
        - Riesgo Medio: Seguimiento programado
        - Riesgo Bajo: Control rutinario
        """)

        if df_riesgo is not None:
            alertas = generar_alertas_desde_datos(df_riesgo, historico=historico)
            if not alertas.empty:
                st.write(f"**{len(alertas)} pacientes con alertas activas:**")
                st.dataframe(alertas, use_container_width=True, hide_index=True)
            else:
                st.success("Sin alertas activas. Todos los pacientes en rango aceptable.")
        else:
            st.info("Sin datos del prestador. Cargue datos desde el portal IPS para ver alertas reales.")

    with tab2:
        st.subheader("Registrar nueva intervencion")

        with st.form("form_intervencion"):
            col1, col2 = st.columns(2)
            with col1:
                doc_paciente = st.text_input("Documento del paciente")
                tipo_accion = st.selectbox("Tipo de accion", [
                    "Llamada telefonica", "Envio SMS", "Correo electronico",
                    "Educacion en salud", "Cita prioritaria",
                    "Visita domiciliaria", "Intervencion multidisciplinaria"
                ])
                gestor = st.text_input("Nombre del gestor")

            with col2:
                resultado = st.selectbox("Resultado", [
                    "Contacto exitoso", "No contesta", "Mensaje dejado",
                    "Cita agendada", "Paciente informado", "Rechaza atencion"
                ])
                observaciones = st.text_area("Observaciones", height=100)

            submitted = st.form_submit_button("Guardar intervencion", type="primary")

            if submitted and doc_paciente:
                nueva_entrada = pd.DataFrame([{
                    "documento": doc_paciente,
                    "fecha_accion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tipo_accion": tipo_accion,
                    "gestor": gestor,
                    "resultado": resultado,
                    "observaciones": observaciones,
                }])
                st.session_state.log_intervenciones = pd.concat(
                    [nueva_entrada, st.session_state.log_intervenciones],
                    ignore_index=True
                )
                st.success(f"Intervencion registrada para documento {doc_paciente}")

    with tab3:
        st.subheader("Trazabilidad cronologica")

        filtro_doc = st.text_input("Filtrar por documento (dejar vacio para ver todos):", key="filtro_log")

        log = st.session_state.log_intervenciones
        if filtro_doc:
            log = log[log["documento"].str.contains(filtro_doc)]

        st.write(f"**{len(log)} registros encontrados**")
        st.dataframe(log, use_container_width=True, hide_index=True)
