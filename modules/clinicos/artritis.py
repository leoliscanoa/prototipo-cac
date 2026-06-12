"""
Modulo clinico: Artritis reumatoide

Funcionalidades:
- Seguimiento farmacologico
- Indicadores de adherencia a medicamentos DMARD
- Monitoreo DAS28

# PLACEHOLDER: MODELO PREDICTIVO DE RESPUESTA TERAPEUTICA
# Se integrara un modelo para predecir respuesta a DMARDs
# biologicos vs convencionales, optimizando el switch terapeutico.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np


def _cols(df, columnas):
    """Selecciona columnas disponibles sin KeyError."""
    return df[[c for c in columnas if c in df.columns]]


def clasificar_actividad_das28(das28: float) -> str:
    """Clasifica actividad de la enfermedad por DAS28."""
    if das28 < 2.6:
        return "Remision"
    elif das28 <= 3.2:
        return "Baja actividad"
    elif das28 <= 5.1:
        return "Moderada actividad"
    else:
        return "Alta actividad"


def generar_datos_demo_artritis() -> pd.DataFrame:
    """Genera datos de demostracion para artritis reumatoide."""
    np.random.seed(44)
    n = 40

    dmards = ["Metotrexato", "Leflunomida", "Sulfasalazina",
              "Adalimumab", "Rituximab", "Tocilizumab"]
    respuestas = ["Buena", "Moderada", "Sin respuesta"]

    datos = {
        "documento": [f"{30000000 + i}" for i in range(n)],
        "nombres": [f"Paciente_AR_{i}" for i in range(n)],
        "edad": np.random.randint(25, 75, n),
        "das28": np.round(np.random.uniform(1.5, 7.5, n), 2),
        "medicamento_dmard": np.random.choice(dmards, n),
        "adherencia_porcentaje": np.round(np.random.uniform(40, 100, n), 1),
        "meses_tratamiento": np.random.randint(1, 60, n),
        "respuesta_clinica": np.random.choice(respuestas, n, p=[0.4, 0.35, 0.25]),
        "pcr": np.round(np.random.uniform(0.1, 15.0, n), 2),
        "vsg": np.random.randint(5, 80, n),
    }
    return pd.DataFrame(datos)


def renderizar_modulo_artritis(df: pd.DataFrame = None):
    """Renderiza la vista del modulo de artritis reumatoide."""
    st.header("Modulo artritis reumatoide")

    if df is None or df.empty:
        st.info("Usando datos de demostracion.")
        df = generar_datos_demo_artritis()

    # Clasificar actividad
    if "das28" in df.columns:
        df["actividad_das28"] = df["das28"].apply(clasificar_actividad_das28)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total pacientes", len(df))
    with col2:
        if "adherencia_porcentaje" in df.columns:
            baja_adherencia = len(df[df["adherencia_porcentaje"] < 80])
            st.metric("Baja adherencia (<80%)", baja_adherencia)
    with col3:
        if "actividad_das28" in df.columns:
            alta = len(df[df["actividad_das28"] == "Alta actividad"])
            st.metric("Alta actividad", alta)
    with col4:
        if "actividad_das28" in df.columns:
            remision = len(df[df["actividad_das28"] == "Remision"])
            st.metric("En remision", remision)

    # Seguimiento farmacologico
    st.subheader("Seguimiento farmacologico DMARD")
    tab1, tab2, tab3 = st.tabs(
        ["Adherencia", "Actividad de enfermedad", "Respuesta terapeutica"]
    )

    with tab1:
        if "adherencia_porcentaje" in df.columns and "medicamento_dmard" in df.columns:
            fig = px.box(
                df, x="medicamento_dmard", y="adherencia_porcentaje",
                color="medicamento_dmard",
                title="Adherencia por DMARD (%)"
            )
            fig.add_hline(
                y=80, line_dash="dash", line_color="red",
                annotation_text="Meta 80%"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Tabla de pacientes con baja adherencia
            baja = _cols(
                df[df["adherencia_porcentaje"] < 80],
                ["documento", "nombres", "medicamento_dmard",
                 "adherencia_porcentaje", "meses_tratamiento"]
            ).sort_values("adherencia_porcentaje")

            if not baja.empty:
                st.warning(f"{len(baja)} pacientes con adherencia < 80%")
                st.dataframe(baja, use_container_width=True, hide_index=True)

    with tab2:
        if "actividad_das28" in df.columns:
            fig = px.pie(
                df, names="actividad_das28",
                title="Distribucion por actividad (DAS28)",
                color="actividad_das28",
                color_discrete_map={
                    "Remision": "#2ecc71",
                    "Baja actividad": "#f1c40f",
                    "Moderada actividad": "#e67e22",
                    "Alta actividad": "#e74c3c"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if "respuesta_clinica" in df.columns and "medicamento_dmard" in df.columns:
            resp_pivot = df.groupby(
                ["medicamento_dmard", "respuesta_clinica"]
            ).size().reset_index(name="n")
            fig = px.bar(
                resp_pivot, x="medicamento_dmard", y="n",
                color="respuesta_clinica",
                title="Respuesta clinica por DMARD", barmode="stack"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.caption(
        "Modelo predictivo: proximamente prediccion de respuesta "
        "a biologicos vs convencionales."
    )
