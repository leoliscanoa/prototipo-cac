"""
Modulo de Intervencion Clinica (CRM de Salud).

Permite a los gestores de la EPS:
- Ver alertas por nivel de riesgo y adherencia
- Registrar intervenciones (llamadas, SMS, correos, educacion)
- Programar acciones segun riesgo (rutinarias vs urgentes)
- Consultar trazabilidad cronologica de acciones por paciente
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import numpy as np


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


def renderizar_crm_clinico():
    """Renderiza el modulo CRM clinico para gestores EPS."""
    st.header("Intervencion clinica - CRM de salud")

    # Inicializar log en session state
    if "log_intervenciones" not in st.session_state:
        st.session_state.log_intervenciones = generar_log_intervenciones_demo()

    tab1, tab2, tab3 = st.tabs([
        "Alertas y prescripcion", "Registrar intervencion", "Trazabilidad (log)"
    ])

    with tab1:
        st.subheader("Alertas activas por nivel de riesgo")

        # Simulacion de alertas
        alertas = pd.DataFrame({
            "documento": ["10000003", "10000012", "10000027", "10000041", "10000008"],
            "nombres": ["Paciente_3", "Paciente_12", "Paciente_27", "Paciente_41", "Paciente_8"],
            "nivel_riesgo": ["Muy Alto", "Muy Alto", "Alto", "Alto", "Medio"],
            "adherencia": [45, 55, 62, 70, 78],
            "alerta": [
                "No asiste a control hace 90 dias",
                "HbA1c en deterioro progresivo",
                "Carga viral detectable 2 periodos",
                "Creatinina en aumento sostenido",
                "Pendiente laboratorio de control"
            ],
            "accion_prescrita": [
                "Cita prioritaria + visita domiciliaria",
                "Intervencion multidisciplinaria",
                "Cita prioritaria con infectologia",
                "Cita prioritaria nefrologia",
                "Recordatorio telefonico de laboratorio"
            ]
        })

        # Codigo de colores por riesgo
        st.markdown("""
        **Reglas de prescripcion automatica:**
        - Riesgo Alto/Muy Alto + No adherente: Cita prioritaria, intervencion multidisciplinaria
        - Riesgo Bajo/Adherente: Control rutinario programado
        """)

        st.dataframe(alertas, use_container_width=True, hide_index=True)

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

        # Filtro por documento
        filtro_doc = st.text_input("Filtrar por documento (dejar vacio para ver todos):", key="filtro_log")

        log = st.session_state.log_intervenciones
        if filtro_doc:
            log = log[log["documento"].str.contains(filtro_doc)]

        st.write(f"**{len(log)} registros encontrados**")
        st.dataframe(log, use_container_width=True, hide_index=True)
