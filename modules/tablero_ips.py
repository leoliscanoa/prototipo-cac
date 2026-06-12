"""
Tablero operativo diario para IPS.

Muestra al personal de la IPS:
- Pacientes con actividades pendientes o vencidas
- Tamizajes faltantes
- Laboratorios por tomar
- Consultas de control pendientes
"""

import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime, timedelta


def generar_tareas_pendientes_demo() -> pd.DataFrame:
    """Genera datos demo de tareas pendientes para la IPS."""
    np.random.seed(77)
    n = 35

    tipos_tarea = [
        "Laboratorio de control", "Consulta medica", "Tamizaje",
        "Control enfermeria", "Valoracion nutricion", "Consulta especialista"
    ]
    estados = ["Pendiente", "Vencida", "Proxima"]
    prioridades = ["Alta", "Media", "Baja"]

    fechas_vencimiento = []
    for _ in range(n):
        offset = np.random.randint(-15, 30)
        fechas_vencimiento.append(
            (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d")
        )

    datos = {
        "documento": [f"{10000000 + np.random.randint(0, 80)}" for _ in range(n)],
        "nombres": [f"Paciente_{np.random.randint(0, 80)}" for _ in range(n)],
        "tipo_tarea": np.random.choice(tipos_tarea, n),
        "fecha_vencimiento": fechas_vencimiento,
        "prioridad": np.random.choice(prioridades, n, p=[0.3, 0.45, 0.25]),
        "patologia": np.random.choice(
            ["ERC", "Cancer", "VIH", "Artritis", "Hemofilia"], n
        ),
        "responsable": np.random.choice(
            ["Dr. Garcia", "Enf. Martinez", "Dr. Lopez", "Nut. Perez"], n
        ),
    }
    df = pd.DataFrame(datos)

    # Calcular estado segun fecha
    hoy = datetime.now().strftime("%Y-%m-%d")
    df["estado"] = df["fecha_vencimiento"].apply(
        lambda x: "Vencida" if x < hoy else ("Proxima" if x <= (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d") else "Pendiente")
    )

    return df.sort_values(["estado", "fecha_vencimiento"])


def renderizar_tablero_ips():
    """Renderiza el tablero operativo diario de la IPS."""
    st.header("Tablero operativo diario")
    st.caption("Actividades pendientes y vencidas segun ruta de atencion")

    df_tareas = generar_tareas_pendientes_demo()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total actividades", len(df_tareas))
    with col2:
        vencidas = len(df_tareas[df_tareas["estado"] == "Vencida"])
        st.metric("Vencidas", vencidas)
    with col3:
        proximas = len(df_tareas[df_tareas["estado"] == "Proxima"])
        st.metric("Proximas (7 dias)", proximas)
    with col4:
        alta_prioridad = len(df_tareas[df_tareas["prioridad"] == "Alta"])
        st.metric("Prioridad alta", alta_prioridad)

    st.divider()

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filtro_estado = st.multiselect(
            "Estado", ["Vencida", "Proxima", "Pendiente"],
            default=["Vencida", "Proxima"]
        )
    with col_f2:
        filtro_tipo = st.multiselect(
            "Tipo de tarea", df_tareas["tipo_tarea"].unique().tolist()
        )
    with col_f3:
        filtro_patologia = st.multiselect(
            "Patologia", df_tareas["patologia"].unique().tolist()
        )

    # Aplicar filtros
    df_filtrado = df_tareas.copy()
    if filtro_estado:
        df_filtrado = df_filtrado[df_filtrado["estado"].isin(filtro_estado)]
    if filtro_tipo:
        df_filtrado = df_filtrado[df_filtrado["tipo_tarea"].isin(filtro_tipo)]
    if filtro_patologia:
        df_filtrado = df_filtrado[df_filtrado["patologia"].isin(filtro_patologia)]

    # Tabla de tareas
    st.subheader(f"Actividades ({len(df_filtrado)} resultados)")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # Resumen por tipo
    st.subheader("Resumen por tipo de actividad")
    resumen = df_tareas.groupby(["tipo_tarea", "estado"]).size().reset_index(name="cantidad")
    import plotly.express as px
    fig = px.bar(resumen, x="tipo_tarea", y="cantidad", color="estado",
                barmode="group", title="Actividades por tipo y estado",
                color_discrete_map={"Vencida": "#e74c3c", "Proxima": "#f39c12", "Pendiente": "#3498db"})
    st.plotly_chart(fig, use_container_width=True)
