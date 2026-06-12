"""
Modulo de Consolidacion y Exportacion (Salida CAC).

Genera archivos .txt delimitados por tabulaciones, sin justificaciones
ni caracteres especiales, listos para reporte a la Cuenta de Alto Costo.

Nomenclatura: AAAAMMDD_CODEPS_[PATOLOGIA].txt
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CODIGO_EPS, PATOLOGIAS


def limpiar_para_exportacion(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el DataFrame para cumplir con el formato CAC."""
    df_export = df.copy()
    for col in df_export.columns:
        if df_export[col].dtype == object:
            df_export[col] = (
                df_export[col]
                .fillna('')
                .astype(str)
                .str.replace(r'[\t\n\r]', ' ', regex=True)
                .str.replace(r'[^\w\s.,;:\-/()]', '', regex=True)
                .str.strip()
            )
        else:
            df_export[col] = df_export[col].fillna('')
    return df_export


def generar_nombre_archivo(patologia: str, codigo_eps: str = CODIGO_EPS) -> str:
    """Genera el nombre del archivo segun la nomenclatura CAC."""
    fecha = datetime.now().strftime("%Y%m%d")
    patologia_clean = patologia.upper().replace(" ", "_")
    return f"{fecha}_{codigo_eps}_{patologia_clean}.txt"


def exportar_a_txt_tabulado(df: pd.DataFrame, patologia: str) -> str:
    """Convierte un DataFrame a texto delimitado por tabulaciones."""
    df_limpio = limpiar_para_exportacion(df)
    return df_limpio.to_csv(sep='\t', index=False, encoding='utf-8')


def renderizar_exportacion(df: Optional[pd.DataFrame], patologia: str):
    """Renderiza la interfaz de exportacion CAC en Streamlit."""
    st.subheader("Exportacion CAC")

    if df is None or df.empty:
        st.warning("No hay datos validados para exportar. Primero cargue y valide datos.")
        return

    nombre_archivo = generar_nombre_archivo(patologia)

    st.info(f"""
    **Resumen de exportacion:**
    - Registros a exportar: {len(df)}
    - Columnas: {len(df.columns)}
    - Formato: TXT delimitado por tabulaciones
    - Archivo: `{nombre_archivo}`
    """)

    with st.expander("Vista previa del archivo de salida"):
        contenido_preview = exportar_a_txt_tabulado(df.head(5), patologia)
        st.code(contenido_preview, language="text")

    contenido_completo = exportar_a_txt_tabulado(df, patologia)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Generar archivo CAC",
            data=contenido_completo,
            file_name=nombre_archivo,
            mime="text/plain",
            type="primary",
            use_container_width=True
        )

    with col2:
        st.metric("Registros", len(df))

    st.caption(
        f"El archivo se descargara como `{nombre_archivo}` "
        "en formato texto delimitado por tabulaciones, sin caracteres especiales."
    )
