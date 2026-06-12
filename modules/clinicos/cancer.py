"""
Modulo Clinico: Cancer

Funcionalidades:
- Alertas de seguimiento
- Control de oportunidad diagnostica
- Trazabilidad de tratamientos (Cirugia, Quimio, Radio)

# PLACEHOLDER: MODELO PREDICTIVO DE RECAIDA
# Se integrara un modelo de ML para predecir probabilidad de recaida.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np


def _cols(df, columnas):
    """Selecciona columnas disponibles sin KeyError."""
    return df[[c for c in columnas if c in df.columns]]


def generar_datos_demo_cancer() -> pd.DataFrame:
    """Genera datos de demostracion para la cohorte de cancer."""
    np.random.seed(42)
    n = 50

    tipos_cancer = ["Mama", "Prostata", "Colon", "Pulmon", "Cervix", "Gastrico"]
    estadios = ["I", "II", "IIIA", "IIIB", "IV"]
    tratamientos = ["Cirugia", "Quimioterapia", "Radioterapia", "Cirugia+Quimio", "Quimio+Radio"]

    datos = {
        "documento": [f"{10000000 + i}" for i in range(n)],
        "nombres": [f"Paciente_{i}" for i in range(n)],
        "tipo_cancer": np.random.choice(tipos_cancer, n),
        "estadio": np.random.choice(estadios, n),
        "fecha_diagnostico": [
            (datetime.now() - timedelta(days=np.random.randint(30, 730))).strftime("%Y-%m-%d")
            for _ in range(n)
        ],
        "tratamiento_actual": np.random.choice(tratamientos, n),
        "dias_desde_diagnostico": np.random.randint(30, 730, n),
        "dias_hasta_inicio_tratamiento": np.random.randint(1, 90, n),
        "ultimo_seguimiento_dias": np.random.randint(1, 180, n),
    }
    return pd.DataFrame(datos)


def renderizar_modulo_cancer(df: pd.DataFrame = None):
    """Renderiza la vista del modulo clinico de cancer."""
    st.header("Modulo cancer")

    if df is None or df.empty:
        st.info("Usando datos de demostracion. Cargue datos reales desde el modulo de ingesta.")
        df = generar_datos_demo_cancer()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total pacientes", len(df))
    with col2:
        if "dias_hasta_inicio_tratamiento" in df.columns:
            oportunidad = df["dias_hasta_inicio_tratamiento"].mean()
            st.metric("Oportunidad Dx-Tx (dias)", f"{oportunidad:.0f}")
    with col3:
        if "ultimo_seguimiento_dias" in df.columns:
            perdidos = len(df[df["ultimo_seguimiento_dias"] > 90])
            st.metric("Sin seguimiento >90 dias", perdidos)
    with col4:
        if "estadio" in df.columns:
            avanzados = len(df[df["estadio"].isin(["IIIB", "IV"])])
            st.metric("Estadio avanzado", avanzados)

    # Alertas de seguimiento
    st.subheader("Alertas de seguimiento")
    if "ultimo_seguimiento_dias" in df.columns:
        alertas_seg = df[df["ultimo_seguimiento_dias"] > 60].copy()
        if not alertas_seg.empty:
            alertas_seg["prioridad"] = alertas_seg["ultimo_seguimiento_dias"].apply(
                lambda x: "CRITICA" if x > 120 else "ALTA"
            )
            st.dataframe(
                _cols(alertas_seg, ["documento", "nombres", "tipo_cancer", "estadio",
                                    "ultimo_seguimiento_dias", "prioridad"]).sort_values(
                    "ultimo_seguimiento_dias", ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("Todos los pacientes con seguimiento al dia")

    # Distribucion
    st.subheader("Distribucion de cohorte")
    tab1, tab2, tab3 = st.tabs(["Por tipo", "Por estadio", "Oportunidad diagnostica"])

    with tab1:
        if "tipo_cancer" in df.columns:
            fig = px.pie(df, names="tipo_cancer", title="Distribucion por tipo de cancer")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if "estadio" in df.columns:
            fig = px.histogram(df, x="estadio", color="tipo_cancer",
                             title="Distribucion por estadio TNM")
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if "dias_hasta_inicio_tratamiento" in df.columns:
            fig = px.box(df, x="tipo_cancer", y="dias_hasta_inicio_tratamiento",
                        title="Oportunidad: dias desde diagnostico hasta tratamiento",
                        color="tipo_cancer")
            st.plotly_chart(fig, use_container_width=True)

    # Trazabilidad
    st.subheader("Trazabilidad de tratamientos")
    if "tratamiento_actual" in df.columns:
        trazabilidad = df.groupby(["tipo_cancer", "tratamiento_actual"]).size().reset_index(name="pacientes")
        fig = px.bar(trazabilidad, x="tipo_cancer", y="pacientes", color="tratamiento_actual",
                    title="Tratamientos por tipo de cancer", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.caption("Modelo predictivo de recaida: proximamente se integrara prediccion basada en ML.")
