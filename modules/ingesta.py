"""
Modulo de Carga de Datos (Ingesta).

Permite la carga masiva de archivos .csv o .txt delimitados por tabulaciones,
asi como la entrada individual mediante formularios.
"""

import pandas as pd
import streamlit as st
from typing import Optional
import io


def detectar_separador(contenido: str) -> str:
    """Detecta automaticamente el separador del archivo."""
    primera_linea = contenido.split('\n')[0]
    if '\t' in primera_linea:
        return '\t'
    elif ';' in primera_linea:
        return ';'
    else:
        return ','


def cargar_archivo(uploaded_file) -> Optional[pd.DataFrame]:
    """Procesa un archivo subido y lo convierte en DataFrame."""
    try:
        contenido = uploaded_file.getvalue().decode('utf-8')
        separador = detectar_separador(contenido)

        df = pd.read_csv(
            io.StringIO(contenido),
            sep=separador,
            encoding='utf-8',
            dtype=str,
            na_values=['', 'NA', 'N/A', 'NULL', 'null', 'None']
        )

        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass

        return df

    except Exception as e:
        st.error(f"Error al procesar archivo: {str(e)}")
        return None


def renderizar_carga_masiva() -> Optional[pd.DataFrame]:
    """Renderiza la interfaz de carga masiva de archivos."""
    st.subheader("Carga masiva de archivos")

    st.info(
        "Suba archivos `.csv` (separados por coma o punto y coma) "
        "o `.txt` (separados por tabulacion). "
        "El sistema detecta automaticamente el delimitador."
    )

    uploaded_file = st.file_uploader(
        "Seleccione archivo",
        type=["csv", "txt"],
        help="Formatos aceptados: CSV, TXT delimitado por tabulaciones"
    )

    if uploaded_file is not None:
        df = cargar_archivo(uploaded_file)
        if df is not None:
            st.success(f"Archivo cargado: {uploaded_file.name} - {len(df)} registros, {len(df.columns)} columnas")

            with st.expander("Vista previa de datos (primeras 10 filas)"):
                st.dataframe(df.head(10), use_container_width=True)

            with st.expander("Resumen estadistico"):
                st.write(f"**Columnas detectadas:** {', '.join(df.columns.tolist())}")
                st.write(f"**Tipos de dato:**")
                tipos = df.dtypes.reset_index()
                tipos.columns = ["Columna", "Tipo"]
                st.dataframe(tipos, use_container_width=True)

            return df

    return None


def renderizar_carga_individual(patologia: str) -> Optional[pd.DataFrame]:
    """Renderiza formulario para carga individual de un paciente."""
    st.subheader("Registro individual")

    campos_clinicos = {
        "CANCER": {
            "tipo_cancer": "Tipo de cancer",
            "estadio": "Estadio TNM",
            "fecha_diagnostico": "Fecha diagnostico",
            "tratamiento_actual": "Tratamiento actual"
        },
        "ERC_HTA_DM": {
            "creatinina": "Creatinina (mg/dL)",
            "tasa_filtracion_glomerular": "TFG (mL/min/1.73m2)",
            "hemoglobina_glucosilada": "HbA1c (%)",
            "presion_arterial_sistolica": "PAS (mmHg)",
            "presion_arterial_diastolica": "PAD (mmHg)",
            "albuminuria": "Albuminuria (mg/g)"
        },
        "ARTRITIS_REUMATOIDE": {
            "das28": "DAS28",
            "medicamento_dmard": "Medicamento DMARD",
            "adherencia_porcentaje": "Adherencia (%)",
            "fecha_inicio_tratamiento": "Fecha inicio tratamiento"
        },
        "VIH_SIDA": {
            "cd4": "Conteo CD4 (celulas/uL)",
            "carga_viral": "Carga viral (copias/mL)",
            "esquema_tar": "Esquema TAR",
            "fecha_inicio_tar": "Fecha inicio TAR"
        },
        "HEPATITIS_C": {
            "genotipo": "Genotipo VHC",
            "carga_viral_vhc": "Carga viral VHC",
            "medicamento_antiviral": "Medicamento antiviral",
            "semanas_tratamiento": "Semanas de tratamiento"
        },
        "HEMOFILIA": {
            "tipo_hemofilia": "Tipo hemofilia (A/B)",
            "severidad": "Severidad",
            "factor_coagulacion_consumo_ui": "Consumo factor (UI)",
            "episodios_hemorragicos": "Episodios hemorragicos (ultimos 12 meses)"
        }
    }

    with st.form("form_individual"):
        st.write("**Datos demograficos**")
        col1, col2 = st.columns(2)

        datos = {}
        with col1:
            datos["documento"] = st.text_input("Numero de documento")
            datos["tipo_documento"] = st.selectbox("Tipo documento", ["CC", "TI", "CE", "PA", "RC"])
            datos["nombres"] = st.text_input("Nombres")
            datos["fecha_nacimiento"] = st.date_input("Fecha de nacimiento")

        with col2:
            datos["apellidos"] = st.text_input("Apellidos")
            datos["sexo"] = st.selectbox("Sexo", ["M", "F", "I"])
            datos["codigo_municipio"] = st.text_input("Codigo municipio DANE")

        if patologia in campos_clinicos:
            st.write(f"**Datos clinicos - {patologia}**")
            col3, col4 = st.columns(2)
            campos = list(campos_clinicos[patologia].items())
            mitad = len(campos) // 2

            with col3:
                for key, label in campos[:mitad + 1]:
                    datos[key] = st.text_input(label, key=f"cli_{key}")

            with col4:
                for key, label in campos[mitad + 1:]:
                    datos[key] = st.text_input(label, key=f"cli_{key}")

        submitted = st.form_submit_button("Guardar registro", type="primary")

        if submitted:
            if datos.get("documento"):
                df = pd.DataFrame([datos])
                for col in df.columns:
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except (ValueError, TypeError):
                        pass
                return df
            else:
                st.warning("El campo documento es obligatorio.")

    return None
