"""
Modulo de gestion de cohortes (Ingreso/Egreso).

Evalua pacientes mediante score de elegibilidad y sugiere:
- Ingresos nuevos a cohorte
- Egresos por mejoria, fallecimiento o retiro
- Mantenimiento para pacientes estables

Forma parte del ciclo RIAS dinamico.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from datetime import datetime

from modules.riesgo_dinamico import (
    calcular_score_elegibilidad,
    generar_datos_demo_riesgo,
    recalcular_riesgo_cohorte
)


def generar_candidatos_ingreso(n: int = 15) -> pd.DataFrame:
    """Genera datos demo de candidatos a ingreso en cohorte."""
    np.random.seed(101)
    datos = {
        "documento": [f"{90000000 + i}" for i in range(n)],
        "nombres": [f"Candidato_{i}" for i in range(n)],
        "edad": np.random.randint(35, 78, n),
        "diagnostico": np.random.choice(
            ["N18.3", "N18.4", "E11.9", "I10", "N18.5"], n
        ),
        "creatinina": np.round(np.random.uniform(1.0, 7.0, n), 2),
        "tasa_filtracion_glomerular": np.round(np.random.uniform(10, 90, n), 1),
        "hemoglobina_glucosilada": np.round(np.random.uniform(5.0, 11.0, n), 1),
        "presion_arterial_sistolica": np.random.randint(110, 185, n),
        "albuminuria": np.round(np.random.exponential(120, n), 1),
        "adherencia": np.round(np.random.uniform(50, 100, n), 1),
    }
    df = pd.DataFrame(datos)

    # Calcular score de elegibilidad
    scores = []
    recomendaciones = []
    for _, row in df.iterrows():
        score, recom = calcular_score_elegibilidad(row.to_dict(), "ERC_HTA_DM")
        scores.append(score)
        recomendaciones.append(recom)

    df["score_elegibilidad"] = scores
    df["recomendacion"] = recomendaciones
    return df.sort_values("score_elegibilidad", ascending=False)


def renderizar_gestion_cohortes():
    """Renderiza el modulo de gestion de cohortes."""
    st.header("Gestion de cohortes - Ciclo RIAS")
    st.caption("Ingreso, mantenimiento y egreso de pacientes en cohortes de alto costo")

    tab1, tab2, tab3 = st.tabs([
        "Candidatos a ingreso", "Cohorte activa (riesgo dinamico)", "Egresos"
    ])

    with tab1:
        st.subheader("Evaluacion de candidatos a ingreso")
        st.write(
            "El sistema evalua pacientes y genera un score de elegibilidad "
            "sugiriendo quienes deben ingresar a la cohorte."
        )

        candidatos = generar_candidatos_ingreso()

        # KPIs
        col1, col2, col3 = st.columns(3)
        with col1:
            ingresar = len(candidatos[candidatos["recomendacion"] == "INGRESAR"])
            st.metric("Recomendados para ingreso", ingresar)
        with col2:
            mantener = len(candidatos[candidatos["recomendacion"] == "MANTENER"])
            st.metric("En observacion", mantener)
        with col3:
            egresar = len(candidatos[candidatos["recomendacion"] == "EGRESAR"])
            st.metric("No requieren ingreso", egresar)

        # Tabla con recomendaciones
        st.dataframe(candidatos, use_container_width=True, hide_index=True)

        # Boton de aceptacion manual
        st.write("**Aceptacion manual de ingresos:**")
        seleccion = st.multiselect(
            "Seleccione documentos para confirmar ingreso:",
            candidatos[candidatos["recomendacion"] == "INGRESAR"]["documento"].tolist()
        )
        if st.button("Confirmar ingreso seleccionados", type="primary"):
            if seleccion:
                st.success(f"Ingreso confirmado para {len(seleccion)} pacientes: {', '.join(seleccion)}")
            else:
                st.warning("Seleccione al menos un paciente.")

    with tab2:
        st.subheader("Estratificacion de riesgo dinamico")
        st.write(
            "El riesgo se recalcula automaticamente cuando ingresan nuevos datos. "
            "No es un valor estatico."
        )

        # Generar cohorte con riesgo
        df_cohorte = generar_datos_demo_riesgo(50)

        # KPIs de la cohorte
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total en cohorte", len(df_cohorte))
        with col2:
            muy_alto = len(df_cohorte[df_cohorte["nivel_riesgo"] == "Muy Alto"])
            st.metric("Muy alto riesgo", muy_alto)
        with col3:
            alto = len(df_cohorte[df_cohorte["nivel_riesgo"] == "Alto"])
            st.metric("Alto riesgo", alto)
        with col4:
            bajo = len(df_cohorte[df_cohorte["nivel_riesgo"] == "Bajo"])
            st.metric("Bajo riesgo", bajo)

        # Distribucion de riesgo
        fig = px.histogram(df_cohorte, x="score_riesgo", color="nivel_riesgo",
                          nbins=20, title="Distribucion de scores de riesgo",
                          color_discrete_map={
                              "Bajo": "#2ecc71", "Medio": "#f1c40f",
                              "Alto": "#e74c3c", "Muy Alto": "#9b59b6"
                          })
        st.plotly_chart(fig, use_container_width=True)

        # Tabla detallada
        st.dataframe(
            df_cohorte[["documento", "nombres", "score_riesgo", "nivel_riesgo",
                       "factores_riesgo", "fecha_calculo_riesgo"]].sort_values(
                "score_riesgo", ascending=False
            ),
            use_container_width=True, hide_index=True
        )

        # Simulacion de recalculo
        st.divider()
        st.write("**Simulacion de recalculo:**")
        if st.button("Recalcular riesgo con datos actuales"):
            df_recalculado = recalcular_riesgo_cohorte(df_cohorte)
            st.success(f"Riesgo recalculado para {len(df_recalculado)} pacientes.")

    with tab3:
        st.subheader("Pacientes candidatos a egreso")
        st.write(
            "Pacientes con riesgo Bajo sostenido que pueden ser egresados de la cohorte."
        )

        df_cohorte = generar_datos_demo_riesgo(50)
        egresos = df_cohorte[df_cohorte["nivel_riesgo"] == "Bajo"].copy()
        egresos["motivo_egreso"] = np.random.choice(
            ["Mejoria clinica sostenida", "Metas terapeuticas alcanzadas",
             "Bajo riesgo 2 periodos consecutivos"],
            len(egresos)
        )

        if not egresos.empty:
            st.write(f"**{len(egresos)} pacientes candidatos a egreso**")
            st.dataframe(
                egresos[["documento", "nombres", "score_riesgo", "nivel_riesgo", "motivo_egreso"]],
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No hay pacientes candidatos a egreso en este momento.")
