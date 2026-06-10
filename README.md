# q10_project — ETL Académico USM

Pipeline ETL que extrae datos académicos desde la **API Q10** (sistema de gestión académica) de la **Universidad del Magdalena (USM)**: cancelaciones, rendimiento académico (notas), inasistencias, clasificación de estudiantes y catálogo de cursos. Los datos se limpian, transforman y consolidan para alimentar KPIs institucionales con segmentación por sede, programa, nivel, grupo y jornada.

---

## Requisitos

- Python >= 3.10
- Clave de API Q10

## Instalación

### Windows (PowerShell)
```powershell
git clone <repo>
cd q10_project
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
copy .env.example .env
# Editar .env con tu Q10_API_KEY
```

### Linux / macOS (bash)
```bash
git clone <repo>
cd q10_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu Q10_API_KEY
```

## Uso

### CLI

Los comandos son idénticos en ambos sistemas:

```bash
# Ejecutar todos los módulos en orden
python main.py

# O ejecutar módulos individuales
python main.py cursos        # Catálogo de cursos
python main.py cancelados    # Cancelaciones + edades
python main.py notas         # Notas (filtra estudiantes cancelados)
python main.py inasistencias # Inasistencias detalladas
python main.py estudiantes   # Clasificación de estudiantes por sede/programa/nivel/grupo
python main.py consolidar    # Tabla dimensional unificada
python main.py excel         # Genera archivos .xlsx para revisión manual
```

### Análisis exploratorio

Los notebooks son **autocontenidos** (no importan `src/`), se abren desde la raíz del proyecto:

```bash
# Activar entorno primero (ver Instalación)
jupyter notebook notebooks/
```

## Estructura del proyecto

```
q10_project/
├── main.py                     # Orquestador ETL (CLI)
├── requirements.txt
├── .env.example
├── README.md
│
├── src/
│   ├── config.py               # API_KEY, URL, periodos, programas, fechas
│   ├── utils.py                # logging, retry, guardar CSV/parquet
│   │
│   ├── extract_cursos.py       # GET /cursos → catálogo de cursos
│   ├── extract_notas.py        # GET /evaluaciones/cuantitativo/notas
│   ├── transform_notas.py      # Pivot: extrae 3 seguimientos, grupo y nota final
│   ├── extract_inasistencias.py# GET /inasistencias → detalle + agregado
│   ├── extract_cancelados.py   # GET /matriculas-canceladas
│   ├── extract_edades.py       # GET /estudiantes/{codigo} → edad, género
│   ├── extract_estudiantes.py  # GET /estudiantes?Periodo={id} → clasificación
│   ├── analisis_inasistencias.py# Clasificación de inasistencias por grupo y seguimiento
│   ├── consolidar.py           # Consolidación y resumen para KPIs
│   └── generar_excel.py        # Convierte datasets a .xlsx para revisión
│
├── notebooks/
│   ├── analisis_cancelados.ipynb
│   ├── conteo_estudiantes.ipynb
│   ├── inasistencias_por_seguimiento.ipynb
│   ├── bajo_rendimiento.ipynb   # Estudiantes con nota < 3.0 por programa/semestre/sede/asignatura/área
│   └── dashboard_informe.ipynb  # (futuro)
│
├── tests/                      # 44 tests unitarios
│   ├── test_extract_edades.py
│   ├── test_utils.py
│   ├── test_transform_notas.py
│   ├── test_consolidar.py
│   └── test_analisis_inasistencias.py
│
└── data/
    ├── raw/                    # Datos crudos por fuente
    │   ├── cursos.{parquet,csv}
    │   ├── notas_raw.{parquet,csv}
    │   ├── notas_pivot.{parquet,csv,xlsx}   (columnas: Primer/Segundo/Tercer Seguimiento, Grupo, Nota final)
    │   ├── inasistencias_{agregado,detalle}.{parquet,csv,xlsx}
    │   ├── cancelados.{csv,xlsx,parquet}
    │   └── estudiantes.{parquet,csv}
    └── processed/              # Datos consolidados
        ├── consolidado_notas.{parquet,csv}
        └── resumen_informe.xlsx   (5 hojas: promedios por programa/sede/jornada/nivel, inasistencias)
```

## Configuración (`src/config.py`)

| Variable | Descripción |
|---|---|
| `API_KEY` | Clave de autenticación Q10 (desde `.env`) |
| `BASE_URL` | `https://api.q10.com/v1` |
| `PERIODOS` | `[6]` — solo periodo 6 |
| `PROGRAMAS` | 33 códigos de programa tecnológico USM |
| `EXCLUIR_PROGRAMAS` | Programas excluidos de la analítica (TecLab, CIES, Diplo) |
| `PROGRAMAS_GRUPO_B` | Programas con fechas de corte del grupo B |
| `SEDES_GRUPO_B` | Sedes con fechas de corte del grupo B |
| `FECHA_INICIO_INASISTENCIAS` | `"2026-02-01"` — inicio del rango |

## Arquitectura del pipeline

```
main.py  (CLI: python main.py [módulo])
│
├── cursos
│   └── GET /cursos → data/raw/cursos.parquet
│
├── cancelados
│   ├── GET /matriculas-canceladas (periodo × programa)
│   ├── GET /estudiantes/{codigo} (edad, género)
│   └── → data/raw/cancelados.{csv,parquet}
│
├── notas
│   ├── (usa cursos.parquet para obtener consecutivo_curso por periodo)
│   ├── GET /evaluaciones/cuantitativo/notas?Consecutivo_curso={id}
│   ├── transform: extrae primeros 3 parámetros padre, renombra a
│   │   Primer/Segundo/Tercer Seguimiento, calcula Grupo y Nota final (30/30/40)
│   ├── limpia Nombre_asignatura (quita prefijo "{codigo}-")
│   └── filtra estudiantes que aparecen en cancelados (Numero_identificacion)
│       → data/raw/notas_pivot.parquet
│
├── inasistencias
│   └── GET /inasistencias?Fecha_inicio={}&Fecha_fin={}
│       → data/raw/inasistencias_{agregado,detalle}.parquet
│
├── estudiantes
│   └── GET /estudiantes?Periodo={id} (con paginación)
│       → data/raw/estudiantes.parquet   (34 columnas de clasificación)
│
├── consolidar
│   ├── merge: notas_pivot + clasificación estudiantes (por Numero_identificacion)
│   └── → data/processed/consolidado_notas.parquet  (1.043 columnas)
│       → data/processed/resumen_informe.xlsx       (5 hojas de KPIs)
│
└── excel
    └── convierte datasets a .xlsx (notas_pivot partido en 6 hojas)
```

## Clasificación de estudiantes

El módulo `estudiantes` extrae el endpoint `GET /estudiantes?Periodo={id}` que proporciona datos maestros de clasificación por periodo académico:

| Dimensión | Columnas | Descripción |
|---|---|---|
| **Sede** | `Codigo_sede`, `Nombre_sede` | Sede donde estudia (BASTIDAS, INEM, BURITACA, etc.) |
| **Jornada** | `Codigo_jornada`, `Nombre_jornada` | Jornada académica |
| **Programa** | `Codigo_programa`, `Nombre_programa` | Programa tecnológico |
| **Nivel/Semestre** | `Codigo_nivel`, `Nombre_nivel` | Ej: "Semestre 01", "Semestre 02" |
| **Grupo** | `Consecutivo_grupo`, `Nombre_grupo` | Grupo de clase (puede ser null) |
| **Condición** | `Condicion_matricula` | "Nuevo" o "Antiguo" |

Además, `Nombre_programa` se procesa con `separar_sede_programa()` (`extract_estudiantes.py:14`) que extrae `Sede` y `Nombre_programa_limpio`:
- 2 partes: `"BASTIDAS - TECNOLOGÍA EN MARKETING DIGITAL"` → sede=`BASTIDAS`, programa=`TECNOLOGÍA EN MARKETING DIGITAL`
- 3 partes: `"INEM - TARDE - TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS"` → sede=`INEM`, programa=`TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS` (la parte del medio es jornada y se ignora)
- Sin separador: el valor completo se replica en ambas columnas

Estas dimensiones se fusionan con la tabla de notas durante la consolidación, logrando un 99.4% de cobertura de clasificación.

## Mecanismo de reintentos

`request_with_retry()` en `src/utils.py`:
- Hasta 3 intentos con backoff exponencial (1s, 2s, 4s)
- Reintenta en errores de conexión, timeout y códigos 429/502/503/504
- Timeout por request: 30s

## Endpoints Q10 utilizados

| Recurso | Endpoint | Parámetros clave |
|---|---|---|
| Cursos | `GET /cursos` | `Limit`, `Offset` |
| Notas | `GET /evaluaciones/cuantitativo/notas` | `Consecutivo_curso` |
| Inasistencias | `GET /inasistencias` | `Fecha_inicio`, `Fecha_fin`, `Limit`, `Offset` |
| Matrículas canceladas | `GET /matriculas-canceladas` | `Consecutivo_periodo`, `Codigo_programa` |
| Clasificación estudiantes | `GET /estudiantes?Periodo={id}` | `Periodo` (requerido), `Sede_jornada`, `Programa`, `Curso`, `Limit`, `Offset` (opcionales) |
| Datos de estudiante | `GET /estudiantes/{codigo}` | Edad, género |

## Tests

```bash
pytest tests/ -v    # 44 tests
```

---

Proyecto desarrollado para el análisis institucional de la Universidad del Magdalena.
