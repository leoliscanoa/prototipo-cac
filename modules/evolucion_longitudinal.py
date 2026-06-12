"""
Modulo de Evolucion Longitudinal del Riesgo.

Permite a la EPS visualizar la curva de riesgo de un paciente
a traves del tiempo, usando el historico de datos cargados
previamente por las IPS.

Este modulo NO carga datos. Lee del historico consolidado
en session_state.
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional

from modules.riesgo_dinamico import (
    calcular_score_riesgo,
    calcular_riesgo_historico,
    calcular_tendencia_paciente
)


def renderizar_evolucion_longitudinal(historico_periodos: dict):
    """
    Renderiza la vista de evolucion longitudinal del riesgo.

    Args:
        historico_periodos: Dict con {nombre_periodo: DataFrame} cargado por IPS
                           Ej: {"Enero 2026": df1, "Febrero 2026": df2, "Marzo 2026": df3}
    """
    st.header("Evolucion longitudinal del riesgo")
    st.caption("Analisis de la curva de riesgo del paciente a traves del tiempo")

    if not historico_periodos:
        st.info(
            "Sin datos historicos disponibles. El prestador (IPS) debe cargar "
            "archivos de multiples periodos para habilitar este analisis. "
            "Use el boton 'Agregar periodo' para cargar meses adicionales."
        )
        return

    periodos_disponibles = list(historico_periodos.keys())
    st.write(f"**Periodos disponibles:** {', '.join(periodos_disponibles)}")
    st.write(f"**Total periodos cargados:** {len(periodos_disponibles)}")

    # Consolidar todos los periodos con score de riesgo
    dfs_consolidado = []
    for periodo, df in historico_periodos.items():
        df_temp = df.copy()
        df_temp["periodo"] = periodo
        # Calcular riesgo para este periodo
        df_temp = calcular_riesgo_historico(df_temp, col_periodo="periodo")
        dfs_consolidado.append(df_temp)

    df_historico = pd.concat(dfs_consolidado, ignore_index=True)

    # Determinar columna de documento
    col_doc = "documento" if "documento" in df_historico.columns else "num_id"
    if col_doc not in df_historico.columns:
        st.error("No se encontro columna de identificacion del paciente.")
        return

    # Lista de pacientes unicos
    pacientes_unicos = sorted(df_historico[col_doc].unique().tolist())

    st.divider()

    # --- Vista 1: Seleccionar paciente individual ---
    st.subheader("Curva de riesgo por paciente")

    paciente_seleccionado = st.selectbox(
        "Seleccione un paciente (documento):",
        options=pacientes_unicos,
        key="pac_longitudinal"
    )

    if paciente_seleccionado:
        df_paciente = df_historico[df_historico[col_doc] == paciente_seleccionado].copy()

        if len(df_paciente) < 1:
            st.warning("No hay datos para este paciente.")
            return

        # Ordenar por periodo
        df_paciente = df_paciente.sort_values("periodo")

        # Calcular tendencia
        scores = df_paciente["score_riesgo"].tolist()
        tendencia = calcular_tendencia_paciente(scores)

        # Indicador visual de tendencia
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.metric("Score actual", f"{scores[-1]:.1f}",
                     delta=f"{scores[-1] - scores[0]:.1f}" if len(scores) > 1 else None)
        with col_t2:
            nivel_actual = df_paciente["nivel_riesgo"].iloc[-1]
            st.metric("Nivel actual", nivel_actual)
        with col_t3:
            if tendencia == "AUMENTO":
                st.metric("Tendencia", "Aumento", delta="riesgo sube", delta_color="inverse")
            elif tendencia == "DISMINUYO":
                st.metric("Tendencia", "Disminucion", delta="riesgo baja", delta_color="normal")
            else:
                st.metric("Tendencia", "Estable", delta="sin cambio significativo", delta_color="off")

        # Grafico de linea - curva de riesgo
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_paciente["periodo"],
            y=df_paciente["score_riesgo"],
            mode='lines+markers',
            name='Score de riesgo',
            line=dict(color='#1B4F72', width=3),
            marker=dict(size=10)
        ))

        # Zonas de riesgo como fondo
        fig.add_hrect(y0=0, y1=25, fillcolor="#2ecc71", opacity=0.1,
                     annotation_text="Bajo", annotation_position="left")
        fig.add_hrect(y0=26, y1=50, fillcolor="#f1c40f", opacity=0.1,
                     annotation_text="Medio", annotation_position="left")
        fig.add_hrect(y0=51, y1=75, fillcolor="#e74c3c", opacity=0.1,
                     annotation_text="Alto", annotation_position="left")
        fig.add_hrect(y0=76, y1=100, fillcolor="#9b59b6", opacity=0.1,
                     annotation_text="Muy Alto", annotation_position="left")

        fig.update_layout(
            title=f"Evolucion del riesgo - Paciente {paciente_seleccionado}",
            xaxis_title="Periodo",
            yaxis_title="Score de riesgo (0-100)",
            yaxis=dict(range=[0, 105]),
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

        # Detalle por periodo
        st.write("**Detalle por periodo:**")
        cols_detalle = [c for c in ["periodo", "score_riesgo", "nivel_riesgo",
                        "factores_riesgo", "creatinina", "tasa_filtracion_glomerular",
                        "hemoglobina_glucosilada", "presion_arterial_sistolica",
                        "cd4", "carga_viral"] if c in df_paciente.columns]
        st.dataframe(df_paciente[cols_detalle], use_container_width=True, hide_index=True)

    # --- Vista 2: Resumen poblacional por periodo ---
    st.divider()
    st.subheader("Comparativo poblacional entre periodos")

    resumen_periodos = []
    for periodo in periodos_disponibles:
        df_p = df_historico[df_historico["periodo"] == periodo]
        resumen_periodos.append({
            "Periodo": periodo,
            "Total pacientes": len(df_p),
            "Muy Alto": len(df_p[df_p["nivel_riesgo"] == "Muy Alto"]),
            "Alto": len(df_p[df_p["nivel_riesgo"] == "Alto"]),
            "Medio": len(df_p[df_p["nivel_riesgo"] == "Medio"]),
            "Bajo": len(df_p[df_p["nivel_riesgo"] == "Bajo"]),
            "Score promedio": round(df_p["score_riesgo"].mean(), 1),
        })

    df_resumen = pd.DataFrame(resumen_periodos)
    st.dataframe(df_resumen, use_container_width=True, hide_index=True)

    # Grafico comparativo
    fig_comp = go.Figure()
    for nivel, color in [("Muy Alto", "#9b59b6"), ("Alto", "#e74c3c"),
                         ("Medio", "#f1c40f"), ("Bajo", "#2ecc71")]:
        fig_comp.add_trace(go.Bar(
            x=df_resumen["Periodo"],
            y=df_resumen[nivel],
            name=nivel,
            marker_color=color
        ))
    fig_comp.update_layout(
        title="Distribucion de riesgo por periodo",
        barmode='stack', height=400,
        xaxis_title="Periodo", yaxis_title="Pacientes"
    )
    st.plotly_chart(fig_comp, use_container_width=True)
