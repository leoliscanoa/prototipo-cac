# CAC Risk Management - MVP v2.0

Ecosistema SaaS para la Gestion de Riesgo en Salud, Reportes a la Cuenta de Alto Costo (CAC) y operacion de Rutas Integrales de Atencion en Salud (RIAS) en Colombia.

## Arquitectura

```
prototipo-cac/
├── app.py                          # Punto de entrada (multiportal IPS/EPS)
├── config.py                       # Configuracion, umbrales, reglas
├── requirements.txt
├── modules/
│   ├── ingesta.py                  # Carga de datos (masiva/individual)
│   ├── validacion.py               # Motor de depuracion y validacion
│   ├── exportacion.py              # Consolidacion y exportacion CAC
│   ├── mapeo_columnas.py           # Normalizacion de cabeceras
│   ├── riesgo_dinamico.py          # Motor de riesgo (recalculo, SHAP)
│   ├── crm_clinico.py             # CRM de salud (intervenciones, logs)
│   ├── gestion_cohortes.py         # Ciclo RIAS (ingreso/egreso)
│   ├── tablero_ips.py              # Tablero operativo diario IPS
│   ├── tablero_modelo.py           # Desempeno tecnico IA (TRIPOD+AI)
│   ├── utils.py                    # Utilidades compartidas
│   └── clinicos/
│       ├── cancer.py               # Cohorte Cancer
│       ├── erc.py                  # ERC / HTA / DM (KDIGO)
│       ├── artritis.py             # Artritis Reumatoide
│       ├── vih.py                  # VIH / SIDA
│       ├── hepatitis_c.py          # Hepatitis C (+ mock SIVIGILA)
│       └── hemofilia.py            # Hemofilia
├── data/
│   ├── sample_erc.txt
│   └── test/                       # Archivos de prueba (6 cohortes)
└── scripts/
    └── generar_datos_prueba.py     # Generador de mock data
```

## Portales

### Portal IPS (Prestador) - Nivel operativo
- Tablero operativo diario (tareas pendientes/vencidas)
- Ingesta de datos (masiva .csv/.txt + formulario individual)
- Motor de validacion (bloqueo de outliers biologicos)
- Modulos clinicos por patologia con indicadores

### Portal EPS (Asegurador) - Nivel estrategico
- Dashboard estrategico (ciclo RIAS)
- Gestion de cohortes (ingreso/egreso con score de elegibilidad)
- Estratificacion de riesgo dinamico (recalculo automatico)
- CRM clinico (intervenciones, trazabilidad, prescripcion por riesgo)
- Desempeno del modelo IA (AUC, calibracion, DCA, explicabilidad SHAP)
- Exportacion CAC (archivos .txt tabulados)

## Ejecucion

```bash
pip install -r requirements.txt
streamlit run app.py
```

La aplicacion se abrira en `http://localhost:8501`

## Motor de riesgo dinamico

El riesgo de cada paciente se recalcula automaticamente cuando ingresan
nuevos datos clinicos. No es un valor estatico.

Logica implementada:
- Score numerico 0-100 basado en variables clinicas ponderadas
- Clasificacion en 4 niveles: Bajo, Medio, Alto, Muy Alto
- Explicabilidad: factores que mas contribuyen al riesgo (tipo SHAP)
- Score de elegibilidad para ingreso/egreso de cohortes

## Tablero de desempeno tecnico (TRIPOD+AI)

Metricas simuladas del modelo predictivo:
- Discriminacion: AUC-ROC 0.847, C-index 0.832
- Clasificacion: Sensibilidad 0.81, Especificidad 0.79, F1 0.80
- Calibracion: Brier score 0.142, curva de calibracion
- Utilidad clinica: Decision Curve Analysis (DCA)
- Explicabilidad: SHAP values con traduccion a lenguaje clinico
