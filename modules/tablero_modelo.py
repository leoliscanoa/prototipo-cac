"""
Tablero de desempeno tecnico del modelo predictivo.

Muestra metricas de discriminacion, calibracion y explicabilidad
para cumplimiento TRIPOD+AI. Usa datos simulados para el MVP.

Metricas incluidas:
- Discriminacion: AUC-ROC, C-index, Sensibilidad, Especificidad, F1
- Calibracion: Brier score, curva de calibracion
- Utilidad clinica: Decision Curve Analysis (DCA)
- Explicabilidad: SHAP values (simulados)
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def generar_metricas_modelo() -> dict:
    """Genera metricas simuladas del modelo predictivo."""
    return {
        "auc_roc": 0.847,
        "c_index": 0.832,
        "sensibilidad": 0.81,
        "especificidad": 0.79,
        "f1_score": 0.80,
        "brier_score": 0.142,
        "precision": 0.78,
        "recall": 0.81,
        "n_entrenamiento": 12500,
        "n_validacion": 3200,
        "fecha_entrenamiento": "2026-05-15",
        "version_modelo": "v1.2.0-ERC",
    }


def generar_curva_roc() -> go.Figure:
    """Genera curva ROC simulada."""
    np.random.seed(42)
    # Simular scores
    n = 500
    y_true = np.random.binomial(1, 0.3, n)
    y_score = y_true * np.random.uniform(0.5, 1.0, n) + (1 - y_true) * np.random.uniform(0.0, 0.6, n)

    # Calcular ROC manualmente
    thresholds = np.linspace(0, 1, 100)
    tpr_list = []
    fpr_list = []
    for t in thresholds:
        pred = (y_score >= t).astype(int)
        tp = ((pred == 1) & (y_true == 1)).sum()
        fp = ((pred == 1) & (y_true == 0)).sum()
        fn = ((pred == 0) & (y_true == 1)).sum()
        tn = ((pred == 0) & (y_true == 0)).sum()
        tpr_list.append(tp / (tp + fn) if (tp + fn) > 0 else 0)
        fpr_list.append(fp / (fp + tn) if (fp + tn) > 0 else 0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr_list, y=tpr_list, mode='lines',
                            name='Modelo (AUC=0.847)', line=dict(color='#1B4F72', width=2)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines',
                            name='Referencia (AUC=0.5)', line=dict(color='gray', dash='dash')))
    fig.update_layout(title="Curva ROC", xaxis_title="1 - Especificidad (FPR)",
                     yaxis_title="Sensibilidad (TPR)", height=400)
    return fig


def generar_curva_calibracion() -> go.Figure:
    """Genera curva de calibracion simulada."""
    np.random.seed(43)
    deciles = np.linspace(0.05, 0.95, 10)
    observado = deciles + np.random.uniform(-0.05, 0.05, 10)
    observado = np.clip(observado, 0, 1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=deciles, y=observado, mode='lines+markers',
                            name='Modelo', line=dict(color='#1B4F72', width=2),
                            marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines',
                            name='Calibracion perfecta', line=dict(color='gray', dash='dash')))
    fig.update_layout(title="Curva de calibracion", xaxis_title="Probabilidad predicha",
                     yaxis_title="Probabilidad observada", height=400)
    return fig


def generar_dca() -> go.Figure:
    """Genera Decision Curve Analysis simulada."""
    np.random.seed(44)
    thresholds = np.linspace(0.01, 0.99, 50)
    # Beneficio neto simulado
    net_benefit_model = 0.25 - 0.3 * thresholds + np.random.uniform(-0.02, 0.02, 50)
    net_benefit_all = 0.3 * (1 - thresholds) - thresholds * 0.7

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=thresholds, y=net_benefit_model, mode='lines',
                            name='Modelo', line=dict(color='#1B4F72', width=2)))
    fig.add_trace(go.Scatter(x=thresholds, y=net_benefit_all, mode='lines',
                            name='Tratar todos', line=dict(color='#e74c3c', dash='dot')))
    fig.add_trace(go.Scatter(x=thresholds, y=[0]*50, mode='lines',
                            name='No tratar', line=dict(color='gray', dash='dash')))
    fig.update_layout(title="Decision Curve Analysis (DCA)",
                     xaxis_title="Umbral de probabilidad",
                     yaxis_title="Beneficio neto", height=400)
    return fig


def generar_shap_ejemplo() -> pd.DataFrame:
    """Genera explicabilidad tipo SHAP para un paciente ejemplo."""
    return pd.DataFrame({
        "Variable": ["HbA1c", "Edad", "TFG", "Creatinina", "PAS", "Albuminuria", "Adherencia"],
        "Valor": ["8.5%", "65 anos", "42 mL/min", "2.8 mg/dL", "155 mmHg", "180 mg/g", "60%"],
        "Contribucion al riesgo": [+12.0, +8.5, +9.0, +14.4, +4.5, +7.5, +8.0],
        "Direccion": ["Aumenta", "Aumenta", "Aumenta", "Aumenta", "Aumenta", "Aumenta", "Aumenta"],
    }).sort_values("Contribucion al riesgo", ascending=False)


def renderizar_tablero_modelo():
    """Renderiza el tablero de desempeno tecnico del modelo."""
    st.header("Desempeno tecnico del modelo predictivo")
    st.caption("Cumplimiento TRIPOD+AI - Metricas con datos simulados")

    metricas = generar_metricas_modelo()

    # Info del modelo
    st.info(
        f"**Modelo:** {metricas['version_modelo']} | "
        f"**Entrenamiento:** {metricas['n_entrenamiento']} pacientes | "
        f"**Validacion:** {metricas['n_validacion']} pacientes | "
        f"**Fecha:** {metricas['fecha_entrenamiento']}"
    )

    # KPIs principales
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("AUC-ROC", f"{metricas['auc_roc']:.3f}")
    with col2:
        st.metric("C-index", f"{metricas['c_index']:.3f}")
    with col3:
        st.metric("Sensibilidad", f"{metricas['sensibilidad']:.2f}")
    with col4:
        st.metric("Especificidad", f"{metricas['especificidad']:.2f}")
    with col5:
        st.metric("F1-score", f"{metricas['f1_score']:.2f}")
    with col6:
        st.metric("Brier score", f"{metricas['brier_score']:.3f}")

    st.divider()

    # Graficos
    tab1, tab2, tab3, tab4 = st.tabs([
        "Discriminacion (ROC)", "Calibracion", "Utilidad clinica (DCA)", "Explicabilidad (SHAP)"
    ])

    with tab1:
        st.subheader("Capacidad de discriminacion")
        fig_roc = generar_curva_roc()
        st.plotly_chart(fig_roc, use_container_width=True)
        st.caption("Curva ROC: mide la capacidad del modelo para distinguir pacientes de alto vs bajo riesgo.")

    with tab2:
        st.subheader("Calibracion del modelo")
        col_a, col_b = st.columns([2, 1])
        with col_a:
            fig_cal = generar_curva_calibracion()
            st.plotly_chart(fig_cal, use_container_width=True)
        with col_b:
            st.write("**Interpretacion:**")
            st.write("Si la curva se acerca a la diagonal, el modelo esta bien calibrado.")
            st.write(f"Brier score: **{metricas['brier_score']:.3f}** (menor es mejor, ideal < 0.25)")

    with tab3:
        st.subheader("Utilidad clinica - Decision Curve Analysis")
        fig_dca = generar_dca()
        st.plotly_chart(fig_dca, use_container_width=True)
        st.caption("DCA: muestra el beneficio neto de usar el modelo vs tratar a todos o no tratar a nadie.")

    with tab4:
        st.subheader("Explicabilidad del riesgo (SHAP)")
        st.write("**Ejemplo: Paciente con riesgo Alto (score 72.4)**")
        st.write("Factores que mas contribuyen al nivel de riesgo:")

        shap_df = generar_shap_ejemplo()

        # Grafico de barras horizontal tipo SHAP
        fig = px.bar(shap_df, x="Contribucion al riesgo", y="Variable",
                    orientation='h', color="Contribucion al riesgo",
                    color_continuous_scale=["#2ecc71", "#f1c40f", "#e74c3c"],
                    title="Contribucion de cada variable al riesgo del paciente")
        fig.update_layout(height=350, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

        st.write("**Traduccion clinica:**")
        st.info(
            "Riesgo Alto debido a: Creatinina = 2.8 mg/dL (elevada), "
            "HbA1c = 8.5% (mal control metabolico), TFG = 42 mL/min (ERC estadio G3b), "
            "Edad = 65 anos"
        )
        st.dataframe(shap_df, use_container_width=True, hide_index=True)
