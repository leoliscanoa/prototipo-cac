"""
Modulo clinico: Hemofilia

Funcionalidades:
- Control estricto de consumo de factores de coagulacion
- Seguimiento de episodios hemorragicos
- Monitoreo de inhibidores

# PLACEHOLDER: MODELO PREDICTIVO DE EPISODIOS
# Se integrara un modelo para predecir frecuencia de episodios
# hemorragicos basado en tipo de hemofilia, severidad, profilaxis
# y adherencia al tratamiento.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np


def _cols(df, columnas):
    """Selecciona columnas disponibles sin KeyError."""
    return df[[c for c in columnas if c in df.columns]]


def calcular_consumo_per_capita(consumo_ui: int, peso_kg: float) -> float:
    """Calcula consumo per capita UI/kg/anio."""
    if peso_kg > 0:
        return round(consumo_ui / peso_kg, 1)
    return 0.0


def generar_datos_demo_hemofilia() -> pd.DataFrame:
    """Genera datos de demostracion para hemofilia."""
    np.random.seed(77)
    n = 30

    tipos = ["A", "B"]
    severidades = ["Leve", "Moderada", "Severa"]
    profilaxis = ["Profilaxis primaria", "Profilaxis secundaria", "A demanda"]

    datos = {
        "documento": [f"{60000000 + i}" for i in range(n)],
        "nombres": [f"Paciente_Hemo_{i}" for i in range(n)],
        "edad": np.random.randint(2, 55, n),
        "tipo_hemofilia": np.random.choice(tipos, n, p=[0.8, 0.2]),
        "severidad": np.random.choice(severidades, n, p=[0.25, 0.30, 0.45]),
        "factor_coagulacion_consumo_ui": np.random.randint(5000, 200000, n),
        "episodios_hemorragicos": np.random.randint(0, 25, n),
        "articulacion_diana": np.random.choice(
            ["Rodilla", "Codo", "Tobillo", "Cadera", "Ninguna"], n
        ),
        "inhibidores": np.random.choice(
            ["Positivo", "Negativo"], n, p=[0.15, 0.85]
        ),
        "tipo_profilaxis": np.random.choice(
            profilaxis, n, p=[0.3, 0.35, 0.35]
        ),
        "peso_kg": np.round(np.random.uniform(15, 90, n), 1),
    }
    return pd.DataFrame(datos)


def renderizar_modulo_hemofilia(df: pd.DataFrame = None):
    """Renderiza la vista del modulo de hemofilia."""
    st.header("Modulo hemofilia")

    if df is None or df.empty:
        st.info("Usando datos de demostracion.")
        df = generar_datos_demo_hemofilia()

    # Calculos
    if ("factor_coagulacion_consumo_ui" in df.columns
            and "peso_kg" in df.columns):
        df["consumo_ui_kg"] = df.apply(
            lambda row: calcular_consumo_per_capita(
                row["factor_coagulacion_consumo_ui"], row["peso_kg"]
            ),
            axis=1
        )

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total pacientes", len(df))
    with col2:
        if "episodios_hemorragicos" in df.columns:
            total_ep = df["episodios_hemorragicos"].sum()
            st.metric("Total episodios (12m)", int(total_ep))
    with col3:
        if "inhibidores" in df.columns:
            inhib = len(df[df["inhibidores"] == "Positivo"])
            st.metric("Con inhibidores", inhib)
    with col4:
        if "factor_coagulacion_consumo_ui" in df.columns:
            total_ui = df["factor_coagulacion_consumo_ui"].sum()
            st.metric("Consumo total (UI)", f"{total_ui:,.0f}")

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "Consumo de factores", "Episodios hemorragicos",
        "Analisis por severidad"
    ])

    with tab1:
        st.subheader("Control de consumo de factores de coagulacion")

        if "consumo_ui_kg" in df.columns:
            fig = px.bar(
                df.sort_values("consumo_ui_kg", ascending=False),
                x="nombres", y="consumo_ui_kg",
                color="tipo_hemofilia",
                title="Consumo de factor (UI/kg) por paciente"
            )
            st.plotly_chart(fig, use_container_width=True)

        if ("tipo_profilaxis" in df.columns
                and "factor_coagulacion_consumo_ui" in df.columns):
            fig2 = px.box(
                df, x="tipo_profilaxis",
                y="factor_coagulacion_consumo_ui",
                color="severidad",
                title="Consumo de factor por tipo de profilaxis y severidad"
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Tabla detallada de consumo
        st.write("**Detalle de consumo por paciente:**")
        cols_consumo = [
            "documento", "nombres", "tipo_hemofilia", "severidad",
            "factor_coagulacion_consumo_ui", "peso_kg", "consumo_ui_kg",
            "tipo_profilaxis"
        ]
        if "factor_coagulacion_consumo_ui" in df.columns:
            st.dataframe(
                _cols(df, cols_consumo).sort_values(
                    "factor_coagulacion_consumo_ui", ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.dataframe(
                _cols(df, cols_consumo),
                use_container_width=True,
                hide_index=True
            )

    with tab2:
        st.subheader("Seguimiento de episodios hemorragicos")

        col_a, col_b = st.columns(2)
        with col_a:
            if "episodios_hemorragicos" in df.columns:
                fig = px.histogram(
                    df, x="episodios_hemorragicos",
                    color="severidad",
                    title="Distribucion de episodios hemorragicos (12 meses)",
                    nbins=15
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_b:
            if "articulacion_diana" in df.columns:
                fig = px.pie(
                    df[df["articulacion_diana"] != "Ninguna"],
                    names="articulacion_diana",
                    title="Articulaciones diana"
                )
                st.plotly_chart(fig, use_container_width=True)

        # Pacientes con alto riesgo hemorragico
        if "episodios_hemorragicos" in df.columns:
            alto_riesgo = df[df["episodios_hemorragicos"] > 10]
            if not alto_riesgo.empty:
                st.warning(
                    f"{len(alto_riesgo)} pacientes con >10 episodios "
                    "en 12 meses"
                )
                st.dataframe(
                    _cols(alto_riesgo, [
                        "documento", "nombres", "tipo_hemofilia",
                        "severidad", "episodios_hemorragicos",
                        "tipo_profilaxis"
                    ]).sort_values(
                        "episodios_hemorragicos", ascending=False
                    ),
                    use_container_width=True,
                    hide_index=True
                )

    with tab3:
        st.subheader("Analisis por severidad")
        if "severidad" in df.columns:
            resumen = df.groupby(
                ["tipo_hemofilia", "severidad"]
            ).agg({
                "episodios_hemorragicos": "mean",
                "factor_coagulacion_consumo_ui": "mean",
                "documento": "count"
            }).rename(columns={
                "episodios_hemorragicos": "Promedio episodios",
                "factor_coagulacion_consumo_ui": "Promedio consumo UI",
                "documento": "N pacientes"
            }).reset_index()
            st.dataframe(resumen, use_container_width=True, hide_index=True)

    st.divider()
    st.caption(
        "Modelo predictivo: proximamente prediccion de frecuencia "
        "de sangrado y optimizacion de profilaxis."
    )
