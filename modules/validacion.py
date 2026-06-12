"""
Motor de Depuracion y Validacion de Calidad de Datos.

Este modulo implementa las reglas de negocio para detectar y bloquear
valores atipicos (outliers) biologicamente imposibles antes de que
los datos sean procesados por los modulos clinicos.

Reglas criticas implementadas:
- Bloquear si Creatinina > 15 mg/dL
- Bloquear si Hemoglobina_Glucosilada == 0
- Alertas para otros valores fuera de rangos fisiologicos

# ============================================================
# PLACEHOLDER: INTEGRACION CON MODELOS PREDICTIVOS
# En versiones futuras, este modulo se conectara con modelos de ML
# para deteccion inteligente de anomalias (Isolation Forest, DBSCAN)
# que complementen las reglas estaticas actuales.
# ============================================================
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REGLAS_VALIDACION


class ResultadoValidacion:
    """Contenedor de resultados de validacion."""

    def __init__(self):
        self.errores: List[Dict[str, Any]] = []
        self.alertas: List[Dict[str, Any]] = []
        self.registros_validos: int = 0
        self.registros_bloqueados: int = 0
        self.registros_con_alerta: int = 0

    @property
    def tiene_errores_criticos(self) -> bool:
        return self.registros_bloqueados > 0

    @property
    def resumen(self) -> Dict[str, Any]:
        return {
            "total_errores": len(self.errores),
            "total_alertas": len(self.alertas),
            "registros_validos": self.registros_validos,
            "registros_bloqueados": self.registros_bloqueados,
            "registros_con_alerta": self.registros_con_alerta,
            "aprobado": not self.tiene_errores_criticos
        }


def validar_rango(valor: float, campo: str, fila: int) -> Optional[Dict[str, Any]]:
    """Valida un valor numerico contra las reglas definidas en config."""
    campo_lower = campo.lower().replace(" ", "_")

    if campo_lower not in REGLAS_VALIDACION:
        return None

    regla = REGLAS_VALIDACION[campo_lower]

    if "valor_invalido" in regla and valor == regla["valor_invalido"]:
        return {
            "fila": fila,
            "campo": campo,
            "valor": valor,
            "regla": f"Valor {valor} es invalido para {campo}",
            "accion": regla["accion"],
            "mensaje": regla["mensaje"]
        }

    if valor < regla["min"] or valor > regla["max"]:
        return {
            "fila": fila,
            "campo": campo,
            "valor": valor,
            "regla": f"Valor {valor} fuera de rango [{regla['min']}-{regla['max']}] {regla['unidad']}",
            "accion": regla["accion"],
            "mensaje": regla["mensaje"]
        }

    return None


def validar_campos_obligatorios(df: pd.DataFrame, campos_requeridos: "List[str]") -> "List[Dict[str, Any]]":
    """Verifica que los campos obligatorios no tengan valores nulos."""
    errores = []
    for campo in campos_requeridos:
        if campo in df.columns:
            nulos = df[df[campo].isna()]
            for idx in nulos.index:
                errores.append({
                    "fila": idx + 1,
                    "campo": campo,
                    "valor": None,
                    "regla": "Campo obligatorio vacio",
                    "accion": "bloquear",
                    "mensaje": f"El campo '{campo}' es obligatorio y esta vacio"
                })
    return errores


def validar_formato_documento(df: pd.DataFrame, col_documento: str = "documento") -> List[Dict[str, Any]]:
    """Valida formato basico de documentos de identidad."""
    alertas = []
    if col_documento not in df.columns:
        return alertas

    for idx, row in df.iterrows():
        doc = str(row[col_documento]).strip()
        if not doc.isdigit() or len(doc) < 5 or len(doc) > 15:
            alertas.append({
                "fila": idx + 1,
                "campo": col_documento,
                "valor": doc,
                "regla": "Formato de documento invalido",
                "accion": "alerta",
                "mensaje": f"Documento '{doc}' no tiene formato numerico valido (5-15 digitos)"
            })
    return alertas


def validar_dataframe(df: pd.DataFrame, campos_requeridos: Optional[List[str]] = None) -> Tuple[pd.DataFrame, ResultadoValidacion]:
    """
    Motor principal de validacion. Procesa un DataFrame completo
    aplicando todas las reglas de calidad de datos.
    """
    resultado = ResultadoValidacion()
    filas_bloqueadas = set()

    if campos_requeridos:
        errores_obligatorios = validar_campos_obligatorios(df, campos_requeridos)
        for error in errores_obligatorios:
            resultado.errores.append(error)
            filas_bloqueadas.add(error["fila"] - 1)

    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    for col in columnas_numericas:
        col_normalizada = col.lower().replace(" ", "_")
        if col_normalizada in REGLAS_VALIDACION:
            for idx, valor in df[col].items():
                if pd.isna(valor):
                    continue
                hallazgo = validar_rango(float(valor), col, idx + 1)
                if hallazgo:
                    if hallazgo["accion"] == "bloquear":
                        resultado.errores.append(hallazgo)
                        filas_bloqueadas.add(idx)
                    else:
                        resultado.alertas.append(hallazgo)

    alertas_doc = validar_formato_documento(df)
    resultado.alertas.extend(alertas_doc)

    resultado.registros_bloqueados = len(filas_bloqueadas)
    resultado.registros_con_alerta = len(set(a["fila"] for a in resultado.alertas))
    resultado.registros_validos = len(df) - resultado.registros_bloqueados

    df_limpio = df.drop(index=list(filas_bloqueadas)).reset_index(drop=True)

    return df_limpio, resultado


def generar_reporte_validacion(resultado: ResultadoValidacion) -> pd.DataFrame:
    """Genera un DataFrame con el reporte detallado de validacion."""
    items = []
    for error in resultado.errores:
        items.append({
            "Tipo": "ERROR",
            "Fila": error["fila"],
            "Campo": error["campo"],
            "Valor": error["valor"],
            "Mensaje": error["mensaje"]
        })
    for alerta in resultado.alertas:
        items.append({
            "Tipo": "ALERTA",
            "Fila": alerta["fila"],
            "Campo": alerta["campo"],
            "Valor": alerta["valor"],
            "Mensaje": alerta["mensaje"]
        })

    if not items:
        return pd.DataFrame(columns=["Tipo", "Fila", "Campo", "Valor", "Mensaje"])

    return pd.DataFrame(items).sort_values(["Tipo", "Fila"]).reset_index(drop=True)
