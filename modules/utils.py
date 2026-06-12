"""
Utilidades compartidas entre módulos clínicos.
"""

import pandas as pd
from typing import List


def seleccionar_columnas(df: pd.DataFrame, columnas_deseadas: List[str]) -> pd.DataFrame:
    """
    Selecciona columnas de un DataFrame de forma segura,
    ignorando las que no existan en vez de lanzar KeyError.

    Args:
        df: DataFrame fuente
        columnas_deseadas: Lista de columnas que se desean extraer

    Returns:
        DataFrame con solo las columnas disponibles (en orden)
    """
    disponibles = [c for c in columnas_deseadas if c in df.columns]
    if not disponibles:
        return df
    return df[disponibles]
