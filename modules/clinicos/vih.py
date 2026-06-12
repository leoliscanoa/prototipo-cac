"""
Modulo clinico: VIH / SIDA

Funcionalidades:
- Auditoria de fallas terapeuticas (TAR)
- Control de transmision materno-infantil
- Seguimiento de coinfecciones (TB, Hepatitis B/C)
- Monitoreo CD4 y carga viral

# PLACEHOLDER: MODELO PREDICTIVO DE FALLA TERAPEUTICA
# Se integrara un modelo basado en datos longitudinales de CD4
# y carga viral para prediccion temprana de falla virologica.
# Variables: adherencia, esquema TAR, CD4 nadir, resistencia.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np


def _cols(df, columnas):
    """Selecciona columnas disponibles sin KeyError."""
    return df[[c for c in columnas if c in df.columns]]


def clasificar_falla_virologica(carga_viral: int, meses_tar: int) -> str:
    """
    Clasifica falla virologica segun criterios OMS.
    Falla: CV >1000 copias/mL despues de 6 meses en TAR.
    """
    if meses_tar < 6:
        return "En observacion (<6 meses)"
    elif carga_viral == 0 or carga_viral < 50:
        return "Supresion viral"
    elif carga_viral < 1000:
        return "Viremia baja"
    else:
        return "Falla virologica"


def generar_datos_demo_vih() -> pd.DataFrame:
    """Genera datos de demostracion para VIH/SIDA."""
    np.random.seed(55)
    n = 60

    esquemas_tar = [
        "TDF/FTC/EFV", "TDF/FTC/DTG", "ABC/3TC/DTG",
        "TAF/FTC/BIC", "AZT/3TC/LPV/r"
    ]
    coinfecciones = ["Ninguna", "TB", "Hepatitis B", "Hepatitis C", "TB + Hep B"]

    datos = {
        "documento": [f"{40000000 + i}" for i in range(n)],
        "nombres": [f"Paciente_VIH_{i}" for i in range(n)],
        "edad": np.random.randint(18, 65, n),
        "sexo": np.random.choice(["M", "F"], n),
        "cd4": np.random.randint(50, 1200, n),
        "carga_viral": np.random.choice(
            [0] * 40 + list(np.random.randint(50, 500000, 20)), n
        ),
        "esquema_tar": np.random.choice(esquemas_tar, n),
        "meses_en_tar": np.random.randint(1, 120, n),
        "adherencia_tar": np.round(np.random.uniform(50, 100, n), 1),
        "coinfeccion": np.random.choice(
            coinfecciones, n, p=[0.55, 0.2, 0.1, 0.1, 0.05]
        ),
        "gestante": np.random.choice(["No", "Si"], n, p=[0.9, 0.1]),
    }
    return pd.DataFrame(datos)


def renderizar_modulo_vih(df: pd.DataFrame = None):
    """Renderiza la vista del modulo VIH/SIDA."""
    st.header("Modulo VIH / SIDA")

    if df is None or df.empty:
        st.info("Usando datos de demostracion.")
        df = generar_datos_demo_vih()
    else:
        st.success(f"Mostrando {len(df)} registros cargados.")

    # Clasificar falla
    if "carga_viral" in df.columns and "meses_en_tar" in df.columns:
        df["estado_virologico"] = df.apply(
            lambda row: clasificar_falla_virologica(
                row["carga_viral"], row["meses_en_tar"]
            ),
            axis=1
        )

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total pacientes", len(df))
    with col2:
        if "estado_virologico" in df.columns:
            suprimidos = len(df[df["estado_virologico"] == "Supresion viral"])
            st.metric(
                "Supresion viral",
                f"{suprimidos} ({suprimidos * 100 // len(df)}%)"
            )
    with col3:
        if "estado_virologico" in df.columns:
            falla = len(df[df["estado_virologico"] == "Falla virologica"])
            st.metric("Falla virologica", falla)
    with col4:
        if "coinfeccion" in df.columns:
            coinf = len(df[df["coinfeccion"] != "Ninguna"])
            st.metric("Con coinfeccion", coinf)

    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "Auditoria TAR", "Transmision materno-infantil",
        "Coinfecciones", "CD4 y carga viral"
    ])

    with tab1:
        st.subheader("Auditoria de fallas terapeuticas")
        if "estado_virologico" in df.columns:
            fig = px.pie(
                df, names="estado_virologico",
                title="Estado virologico de la cohorte",
                color="estado_virologico",
                color_discrete_map={
                    "Supresion viral": "#2ecc71",
                    "Viremia baja": "#f1c40f",
                    "Falla virologica": "#e74c3c",
                    "En observacion (<6 meses)": "#95a5a6"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

            # Tabla de fallas
            fallas = df[df["estado_virologico"] == "Falla virologica"]
            if not fallas.empty:
                st.error(f"{len(fallas)} pacientes con falla virologica")
                st.dataframe(
                    _cols(fallas, [
                        "documento", "nombres", "esquema_tar", "cd4",
                        "carga_viral", "meses_en_tar", "adherencia_tar"
                    ]).sort_values("carga_viral", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )

    with tab2:
        st.subheader("Control transmision materno-infantil")
        if "gestante" in df.columns:
            gestantes = df[df["gestante"] == "Si"]
            if not gestantes.empty:
                st.write(f"**Gestantes en seguimiento:** {len(gestantes)}")
                st.dataframe(
                    _cols(gestantes, [
                        "documento", "nombres", "cd4", "carga_viral",
                        "esquema_tar", "estado_virologico"
                    ]),
                    use_container_width=True,
                    hide_index=True
                )
                # Alerta gestantes con CV detectable
                gest_cv_alta = gestantes[gestantes["carga_viral"] > 50]
                if not gest_cv_alta.empty:
                    st.error(
                        f"{len(gest_cv_alta)} gestante(s) con carga viral "
                        "detectable. Riesgo de transmision vertical."
                    )
            else:
                st.info("No hay gestantes en la cohorte actual.")

    with tab3:
        st.subheader("Coinfecciones")
        if "coinfeccion" in df.columns:
            fig = px.histogram(
                df, x="coinfeccion", color="coinfeccion",
                title="Distribucion de coinfecciones"
            )
            st.plotly_chart(fig, use_container_width=True)

            coinf_df = df[df["coinfeccion"] != "Ninguna"]
            if not coinf_df.empty:
                st.dataframe(
                    _cols(coinf_df, [
                        "documento", "nombres", "coinfeccion",
                        "cd4", "esquema_tar"
                    ]),
                    use_container_width=True,
                    hide_index=True
                )

    with tab4:
        st.subheader("Monitoreo CD4 y carga viral")
        col_a, col_b = st.columns(2)
        with col_a:
            if "cd4" in df.columns:
                fig = px.histogram(
                    df, x="cd4", title="Distribucion CD4", nbins=25
                )
                fig.add_vline(
                    x=200, line_dash="dash", line_color="red",
                    annotation_text="CD4<200 (SIDA)"
                )
                fig.add_vline(
                    x=500, line_dash="dash", line_color="green",
                    annotation_text="CD4>500 (meta)"
                )
                st.plotly_chart(fig, use_container_width=True)
        with col_b:
            if "adherencia_tar" in df.columns:
                fig = px.box(
                    df, x="esquema_tar", y="adherencia_tar",
                    title="Adherencia por esquema TAR"
                )
                fig.add_hline(
                    y=95, line_dash="dash", line_color="red",
                    annotation_text="Meta 95%"
                )
                st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.caption(
        "Modelo predictivo: proximamente prediccion temprana "
        "de falla virologica con ML."
    )
