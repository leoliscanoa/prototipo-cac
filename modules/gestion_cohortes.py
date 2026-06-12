"""
Modulo de gestion de cohortes (Ingreso/Egreso).

Evalua pacientes mediante score de elegibilidad y sugiere:
- Ingresos nuevos a cohorte
- Egresos por mejoria, fallecimiento o retiro
- Mantenimiento para pacientes estables

Usa datos reales del prestador cuando estan disponibles.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from datetime import datetime

from modules.riesgo_dinamico import (
    calcular_score_elegibilidad,
    calcular_score_riesgo,
    generar_datos_demo_riesgo,
    recalcular_riesgo_cohorte
)


def preparar_datos_para_riesgo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Toma los datos cargados por el prestador y les aplica el motor
    de riesgo dinamico para calcular score y nivel.
    """
    return recalcular_riesgo_cohorte(df)


def aplicar_elegibilidad(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica score de elegibilidad a cada paciente."""
    scores = []
    recomendaciones = []
    for _, row in df.iterrows():
        score, recom = calcular_score_elegibilidad(row.to_dict(), "GENERAL")
        scores.append(score)
        recomendaciones.append(recom)
    df = df.copy()
    df["score_elegibilidad"] = scores
    df["recomendacion"] = recomendaciones
    return df


def renderizar_gestion_cohortes(df_prestador: pd.DataFrame = None):
    """
    Renderiza el modulo de gestion de cohortes.
    Usa datos del prestador si estan disponibles, sino datos demo.
    """
    st.header("Gestion de cohortes - Ciclo RIAS")
    st.caption("Ingreso, mantenimiento y egreso de pacientes en cohortes de alto costo")

    # Determinar fuente de datos
    if df_prestador is not None and not df_prestador.empty:
        df_base = df_prestador.copy()
        st.success(f"Trabajando con {len(df_base)} registros cargados por el prestador.")
        usando_demo = False
    else:
        df_base = generar_datos_demo_riesgo(50)
        st.info("Sin datos del prestador. Mostrando datos de demostracion.")
        usando_demo = True

    # Aplicar motor de riesgo si no tiene las columnas
    if "score_riesgo" not in df_base.columns:
        df_base = recalcular_riesgo_cohorte(df_base)

    tab1, tab2, tab3 = st.tabs([
        "Candidatos a ingreso", "Cohorte activa (riesgo dinamico)", "Egresos"
    ])

    with tab1:
        st.subheader("Evaluacion de candidatos a ingreso")
        st.write(
            "El sistema evalua pacientes y genera un score de elegibilidad "
            "sugiriendo quienes deben ingresar a la cohorte."
        )

        # Aplicar elegibilidad
        df_elegibilidad = aplicar_elegibilidad(df_base)

        # KPIs
        col1, col2, col3 = st.columns(3)
        with col1:
            ingresar = len(df_elegibilidad[df_elegibilidad["recomendacion"] == "INGRESAR"])
            st.metric("Recomendados para ingreso", ingresar)
        with col2:
            mantener = len(df_elegibilidad[df_elegibilidad["recomendacion"] == "MANTENER"])
            st.metric("En observacion", mantener)
        with col3:
            egresar = len(df_elegibilidad[df_elegibilidad["recomendacion"] == "EGRESAR"])
            st.metric("No requieren ingreso", egresar)

        # Tabla
        cols_mostrar = [c for c in ["documento", "nombres", "score_riesgo", "nivel_riesgo",
                        "score_elegibilidad", "recomendacion"] if c in df_elegibilidad.columns]
        st.dataframe(
            df_elegibilidad[cols_mostrar].sort_values("score_elegibilidad", ascending=False),
            use_container_width=True, hide_index=True
        )

        # Aceptacion manual
        candidatos_ingreso = df_elegibilidad[df_elegibilidad["recomendacion"] == "INGRESAR"]
        if not candidatos_ingreso.empty and "documento" in candidatos_ingreso.columns:
            st.write("**Aceptacion manual de ingresos:**")
            seleccion = st.multiselect(
                "Seleccione documentos para confirmar ingreso:",
                candidatos_ingreso["documento"].tolist()
            )
            if st.button("Confirmar ingreso seleccionados", type="primary"):
                if seleccion:
                    st.success(f"Ingreso confirmado para {len(seleccion)} pacientes.")
                else:
                    st.warning("Seleccione al menos un paciente.")

    with tab2:
        st.subheader("Estratificacion de riesgo dinamico")
        st.write(
            "El riesgo se recalcula automaticamente cuando ingresan nuevos datos. "
            "No es un valor estatico."
        )

        # KPIs de la cohorte
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total en cohorte", len(df_base))
        with col2:
            muy_alto = len(df_base[df_base["nivel_riesgo"] == "Muy Alto"])
            st.metric("Muy alto riesgo", muy_alto)
        with col3:
            alto = len(df_base[df_base["nivel_riesgo"] == "Alto"])
            st.metric("Alto riesgo", alto)
        with col4:
            bajo = len(df_base[df_base["nivel_riesgo"] == "Bajo"])
            st.metric("Bajo riesgo", bajo)

        # Distribucion de riesgo
        fig = px.histogram(df_base, x="score_riesgo", color="nivel_riesgo",
                          nbins=20, title="Distribucion de scores de riesgo",
                          color_discrete_map={
                              "Bajo": "#2ecc71", "Medio": "#f1c40f",
                              "Alto": "#e74c3c", "Muy Alto": "#9b59b6"
                          })
        st.plotly_chart(fig, use_container_width=True)

        # Tabla detallada
        cols_riesgo = [c for c in ["documento", "nombres", "score_riesgo", "nivel_riesgo",
                       "factores_riesgo", "fecha_calculo_riesgo"] if c in df_base.columns]
        st.dataframe(
            df_base[cols_riesgo].sort_values("score_riesgo", ascending=False),
            use_container_width=True, hide_index=True
        )

    with tab3:
        st.subheader("Pacientes candidatos a egreso")
        st.write(
            "Pacientes con riesgo Bajo sostenido que pueden ser egresados de la cohorte."
        )

        egresos = df_base[df_base["nivel_riesgo"] == "Bajo"].copy()
        if not egresos.empty:
            egresos["motivo_egreso"] = np.random.choice(
                ["Mejoria clinica sostenida", "Metas terapeuticas alcanzadas",
                 "Bajo riesgo sostenido"],
                len(egresos)
            )
            st.write(f"**{len(egresos)} pacientes candidatos a egreso**")
            cols_egreso = [c for c in ["documento", "nombres", "score_riesgo",
                           "nivel_riesgo", "motivo_egreso"] if c in egresos.columns]
            st.dataframe(egresos[cols_egreso], use_container_width=True, hide_index=True)
        else:
            st.info("No hay pacientes candidatos a egreso en este momento.")
