"""
Modulo clinico: Hepatitis C

Funcionalidades:
- Seguimiento farmacoterapeutico (AAD)
- Indicador de respuesta virologica sostenida (RVS)
- Mock de integracion con SIVIGILA

# PLACEHOLDER: INTEGRACION REAL CON SIVIGILA
# En produccion, este modulo se conectara con el sistema SIVIGILA
# del INS mediante API REST para notificacion automatica de casos.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np


def _cols(df, columnas):
    """Selecciona columnas disponibles sin KeyError."""
    return df[[c for c in columnas if c in df.columns]]


def evaluar_rvs(carga_viral: int, fase: str) -> str:
    """Evalua respuesta virologica sostenida."""
    if fase in ["Completo 12 sem", "Completo 24 sem"] and carga_viral == 0:
        return "RVS alcanzada"
    elif fase in ["Completo 12 sem", "Completo 24 sem"] and carga_viral > 0:
        return "Sin RVS - Recaida"
    elif fase == "En tratamiento":
        return "En tratamiento"
    else:
        return "Pendiente"


def generar_datos_demo_hepatitis_c() -> pd.DataFrame:
    """Genera datos de demostracion para hepatitis C."""
    np.random.seed(66)
    n = 35

    genotipos = ["1a", "1b", "2", "3", "4"]
    antivirales = [
        "Sofosbuvir/Velpatasvir", "Sofosbuvir/Ledipasvir",
        "Glecaprevir/Pibrentasvir", "Elbasvir/Grazoprevir"
    ]
    fases_tx = ["En tratamiento", "Completo 12 sem",
                "Completo 24 sem", "Pendiente inicio"]

    datos = {
        "documento": [f"{50000000 + i}" for i in range(n)],
        "nombres": [f"Paciente_HepC_{i}" for i in range(n)],
        "edad": np.random.randint(25, 75, n),
        "genotipo": np.random.choice(
            genotipos, n, p=[0.3, 0.25, 0.15, 0.2, 0.1]
        ),
        "carga_viral_vhc": np.random.choice(
            [0] * 15 + list(np.random.randint(1000, 5000000, 20)), n
        ),
        "medicamento_antiviral": np.random.choice(antivirales, n),
        "semanas_tratamiento": np.random.choice([0, 4, 8, 12, 16, 24], n),
        "fase_tratamiento": np.random.choice(
            fases_tx, n, p=[0.35, 0.3, 0.2, 0.15]
        ),
        "fibrosis_score": np.random.choice(
            ["F0", "F1", "F2", "F3", "F4"], n
        ),
        "notificado_sivigila": np.random.choice(
            ["Si", "No"], n, p=[0.7, 0.3]
        ),
    }
    return pd.DataFrame(datos)


def renderizar_modulo_hepatitis_c(df: pd.DataFrame = None):
    """Renderiza la vista del modulo de hepatitis C."""
    st.header("Modulo hepatitis C")

    if df is None or df.empty:
        st.info("Usando datos de demostracion.")
        df = generar_datos_demo_hepatitis_c()

    # Evaluar RVS
    if "carga_viral_vhc" in df.columns and "fase_tratamiento" in df.columns:
        df["estado_rvs"] = df.apply(
            lambda row: evaluar_rvs(
                row["carga_viral_vhc"], row["fase_tratamiento"]
            ),
            axis=1
        )

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total pacientes", len(df))
    with col2:
        if "estado_rvs" in df.columns:
            rvs = len(df[df["estado_rvs"] == "RVS alcanzada"])
            st.metric("RVS alcanzada", rvs)
    with col3:
        if "fibrosis_score" in df.columns:
            cirrosis = len(df[df["fibrosis_score"] == "F4"])
            st.metric("Cirrosis (F4)", cirrosis)
    with col4:
        if "notificado_sivigila" in df.columns:
            pendientes = len(df[df["notificado_sivigila"] == "No"])
            st.metric("Pendiente SIVIGILA", pendientes)

    # Tabs
    tab1, tab2, tab3 = st.tabs(
        ["Farmacoterapia", "RVS y genotipos", "Integracion SIVIGILA"]
    )

    with tab1:
        st.subheader("Seguimiento farmacoterapeutico")
        if "medicamento_antiviral" in df.columns:
            color_col = "fase_tratamiento" if "fase_tratamiento" in df.columns else None
            fig = px.histogram(
                df, x="medicamento_antiviral", color=color_col,
                title="Antivirales de accion directa en uso",
                barmode="group"
            )
            st.plotly_chart(fig, use_container_width=True)

            if "semanas_tratamiento" in df.columns:
                fig2 = px.box(
                    df, x="medicamento_antiviral", y="semanas_tratamiento",
                    title="Semanas de tratamiento por AAD"
                )
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            if "estado_rvs" in df.columns:
                fig = px.pie(
                    df, names="estado_rvs",
                    title="Respuesta virologica sostenida",
                    color="estado_rvs",
                    color_discrete_map={
                        "RVS alcanzada": "#2ecc71",
                        "Sin RVS - Recaida": "#e74c3c",
                        "En tratamiento": "#3498db",
                        "Pendiente": "#95a5a6"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        with col_b:
            if "genotipo" in df.columns:
                fig = px.pie(
                    df, names="genotipo",
                    title="Distribucion por genotipo"
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Integracion SIVIGILA")
        st.info(
            "Mock de integracion: en produccion, este boton enviara "
            "la notificacion al Sistema de Vigilancia en Salud Publica "
            "(SIVIGILA) del Instituto Nacional de Salud."
        )

        # Mock button de integracion
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            if "notificado_sivigila" in df.columns:
                pendientes_df = df[df["notificado_sivigila"] == "No"]
                st.write(
                    f"**Casos pendientes de notificacion:** {len(pendientes_df)}"
                )
                if not pendientes_df.empty:
                    st.dataframe(
                        _cols(pendientes_df, [
                            "documento", "nombres", "genotipo",
                            "fibrosis_score"
                        ]),
                        use_container_width=True,
                        hide_index=True
                    )
        with col_s2:
            if st.button(
                "Notificar a SIVIGILA", type="primary",
                use_container_width=True
            ):
                st.success(
                    "[MOCK] Notificacion enviada exitosamente a SIVIGILA."
                )

            # Indicador de estado de integracion
            st.info("Estado: Mock (No conectado)")
            st.caption("En produccion se conectara via API REST al INS.")

    st.divider()
    st.caption(
        "Integracion futura: API REST con SIVIGILA para "
        "notificacion automatica de eventos."
    )
