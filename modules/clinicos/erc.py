"""
Modulo Clinico: Enfermedad Renal Cronica (ERC) / HTA / DM

Funcionalidades:
- Estratificacion de riesgo segun guia KDIGO
- Alertas de progresion de dano renal
- Monitoreo de TFG, Creatinina, HbA1c, PA

# PLACEHOLDER: MODELO PREDICTIVO DE PROGRESION RENAL
# Se integrara un modelo de ML para predecir progresion a estadios
# avanzados (G4/G5) y necesidad de terapia de reemplazo renal.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import ESTADIOS_ERC_KDIGO, ALBUMINURIA_KDIGO


def clasificar_estadio_kdigo(tfg: float) -> str:
    """Clasifica el estadio ERC segun TFG (guia KDIGO 2012)."""
    for estadio, params in ESTADIOS_ERC_KDIGO.items():
        if params["tfg_min"] <= tfg <= params["tfg_max"]:
            return estadio
    return "G5" if tfg < 15 else "G1"


def clasificar_albuminuria(valor_mg_g: float) -> str:
    """Clasifica albuminuria segun KDIGO."""
    if valor_mg_g < 30:
        return "A1"
    elif valor_mg_g <= 300:
        return "A2"
    else:
        return "A3"


def calcular_riesgo_progresion(estadio: str, albuminuria_cat: str) -> str:
    """Calcula riesgo de progresion segun matriz KDIGO."""
    matriz = {
        ("G1", "A1"): "Bajo", ("G1", "A2"): "Moderado", ("G1", "A3"): "Alto",
        ("G2", "A1"): "Bajo", ("G2", "A2"): "Moderado", ("G2", "A3"): "Alto",
        ("G3a", "A1"): "Moderado", ("G3a", "A2"): "Alto", ("G3a", "A3"): "Muy Alto",
        ("G3b", "A1"): "Alto", ("G3b", "A2"): "Alto", ("G3b", "A3"): "Muy Alto",
        ("G4", "A1"): "Muy Alto", ("G4", "A2"): "Muy Alto", ("G4", "A3"): "Muy Alto",
        ("G5", "A1"): "Muy Alto", ("G5", "A2"): "Muy Alto", ("G5", "A3"): "Muy Alto",
    }
    return matriz.get((estadio, albuminuria_cat), "No clasificado")


def generar_datos_demo_erc() -> pd.DataFrame:
    """Genera datos de demostracion para ERC/HTA/DM."""
    np.random.seed(123)
    n = 80
    datos = {
        "documento": [f"{20000000 + i}" for i in range(n)],
        "nombres": [f"Paciente_ERC_{i}" for i in range(n)],
        "edad": np.random.randint(35, 85, n),
        "creatinina": np.round(np.random.uniform(0.6, 8.0, n), 2),
        "tasa_filtracion_glomerular": np.round(np.random.uniform(8, 120, n), 1),
        "hemoglobina_glucosilada": np.round(np.random.uniform(4.5, 12.0, n), 1),
        "presion_arterial_sistolica": np.random.randint(100, 200, n),
        "presion_arterial_diastolica": np.random.randint(60, 120, n),
        "albuminuria": np.round(np.random.exponential(100, n), 1),
        "diabetes": np.random.choice(["Si", "No"], n, p=[0.6, 0.4]),
        "hipertension": np.random.choice(["Si", "No"], n, p=[0.75, 0.25]),
    }
    return pd.DataFrame(datos)


def renderizar_modulo_erc(df: pd.DataFrame = None):
    """Renderiza la vista del modulo clinico de ERC/HTA/DM."""
    st.header("Modulo ERC / HTA / DM")

    if df is None or df.empty:
        st.info("Usando datos de demostracion. Cargue datos reales desde el modulo de ingesta.")
        df = generar_datos_demo_erc()
    else:
        st.success(f"Mostrando {len(df)} registros cargados.")

    if "tasa_filtracion_glomerular" in df.columns:
        df["estadio_kdigo"] = df["tasa_filtracion_glomerular"].apply(clasificar_estadio_kdigo)

    if "albuminuria" in df.columns:
        df["cat_albuminuria"] = df["albuminuria"].apply(clasificar_albuminuria)

    if "estadio_kdigo" in df.columns and "cat_albuminuria" in df.columns:
        df["riesgo_progresion"] = df.apply(
            lambda row: calcular_riesgo_progresion(row["estadio_kdigo"], row["cat_albuminuria"]),
            axis=1
        )

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total pacientes", len(df))
    with col2:
        if "estadio_kdigo" in df.columns:
            avanzados = len(df[df["estadio_kdigo"].isin(["G4", "G5"])])
            st.metric("ERC avanzada (G4-G5)", avanzados)
    with col3:
        if "riesgo_progresion" in df.columns:
            muy_alto = len(df[df["riesgo_progresion"] == "Muy Alto"])
            st.metric("Riesgo muy alto", muy_alto)
    with col4:
        if "hemoglobina_glucosilada" in df.columns:
            mal_control = len(df[df["hemoglobina_glucosilada"] > 7.0])
            st.metric("HbA1c > 7%", mal_control)

    # Estratificacion KDIGO
    st.subheader("Estratificacion de riesgo KDIGO")

    if "estadio_kdigo" in df.columns:
        tab1, tab2, tab3 = st.tabs(["Tabla de riesgo", "Distribucion", "Alertas de progresion"])

        with tab1:
            if "riesgo_progresion" in df.columns:
                cols_tabla = [c for c in ["documento", "nombres", "tasa_filtracion_glomerular",
                              "estadio_kdigo", "cat_albuminuria", "riesgo_progresion"] if c in df.columns]
                df_display = df[cols_tabla].copy()
                color_map = {"Bajo": "BAJO", "Moderado": "MODERADO", "Alto": "ALTO", "Muy Alto": "MUY ALTO"}
                df_display["indicador"] = df_display["riesgo_progresion"].map(color_map)
                st.dataframe(
                    df_display.sort_values("tasa_filtracion_glomerular"),
                    use_container_width=True,
                    hide_index=True
                )

        with tab2:
            fig = px.histogram(df, x="estadio_kdigo",
                             color="estadio_kdigo",
                             title="Distribucion por estadio KDIGO",
                             category_orders={"estadio_kdigo": ["G1", "G2", "G3a", "G3b", "G4", "G5"]},
                             color_discrete_map={k: v["color"] for k, v in ESTADIOS_ERC_KDIGO.items()})
            st.plotly_chart(fig, use_container_width=True)

            if "riesgo_progresion" in df.columns:
                fig2 = px.pie(df, names="riesgo_progresion",
                            title="Distribucion por riesgo de progresion",
                            color="riesgo_progresion",
                            color_discrete_map={"Bajo": "#2ecc71", "Moderado": "#f1c40f",
                                               "Alto": "#e74c3c", "Muy Alto": "#9b59b6"})
                st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            st.write("**Pacientes con riesgo alto de progresion renal:**")
            if "riesgo_progresion" in df.columns:
                alerta_df = df[df["riesgo_progresion"].isin(["Alto", "Muy Alto"])].copy()
                if not alerta_df.empty:
                    cols_alerta = [c for c in ["documento", "nombres", "tasa_filtracion_glomerular",
                                  "estadio_kdigo", "creatinina", "riesgo_progresion"] if c in alerta_df.columns]
                    st.dataframe(
                        alerta_df[cols_alerta].sort_values("tasa_filtracion_glomerular"),
                        use_container_width=True,
                        hide_index=True
                    )
                    st.warning(f"{len(alerta_df)} pacientes requieren intervencion prioritaria.")
                else:
                    st.success("Sin alertas de progresion activas.")

    # Control metabolico
    st.subheader("Control metabolico y hemodinamico")
    col_a, col_b = st.columns(2)

    with col_a:
        if "hemoglobina_glucosilada" in df.columns:
            fig = px.histogram(df, x="hemoglobina_glucosilada",
                             title="Distribucion HbA1c", nbins=20)
            fig.add_vline(x=7.0, line_dash="dash", line_color="red",
                         annotation_text="Meta <7%")
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        if "presion_arterial_sistolica" in df.columns:
            fig = px.scatter(df, x="presion_arterial_sistolica",
                           y="presion_arterial_diastolica",
                           color="estadio_kdigo" if "estadio_kdigo" in df.columns else None,
                           title="Presion arterial (PAS vs PAD)")
            fig.add_hline(y=90, line_dash="dash", line_color="red")
            fig.add_vline(x=140, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.caption("Modelo predictivo de progresion renal: "
               "proximamente se integrara prediccion de tiempo hasta TRR basado en survival analysis.")
