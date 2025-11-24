# Dashboard del Clima - Santiago, Chile

Dashboard interactivo del pronóstico del clima construido con R para procesamiento de datos y Python/Streamlit para visualización.

## Descripción

Este proyecto combina lo mejor de R y Python:
- **R**: Obtiene datos de la API de OpenWeather y los procesa usando `httr2` y `dplyr`
- **Python/Streamlit**: Crea un dashboard interactivo para visualizar los pronósticos

Los datos se comparten entre R y Python usando el formato **Feather** (Apache Arrow), optimizado para velocidad y compatibilidad.

## 🚀 Inicio Rápido

### Requisitos previos
Antes de comenzar, asegúrate de tener instalado:
- **R >= 4.0** ([Descargar R](https://cran.r-project.org/))
- **Python >= 3.11** ([Descargar Python](https://www.python.org/downloads/))
- **Git** ([Descargar Git](https://git-scm.com/downloads))

### Pasos para replicar el proyecto

```bash
# 1. Clonar el repositorio
git clone https://github.com/paulovillarroel/api-weather.git
cd api-weather

# 2. Configurar variables de entorno
cp .env.example .env
# Edita .env y agrega tu RAPIDAPI_KEY (ver sección API más abajo)

# 3. Instalar dependencias de R
# Abre R o RStudio en la carpeta del proyecto y ejecuta:
```

```r
install.packages("renv")
renv::restore()
```

```bash
# 4. Instalar dependencias de Python
# Primero instala uv (si no lo tienes):
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Mac/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync

# 5. Obtener datos del clima
Rscript get-weather.R

# 6. Ejecutar el dashboard
uv run streamlit run app.py
```

El dashboard se abrirá en tu navegador en `http://localhost:8501`

---

## Requisitos

### R
- R >= 4.0
- Paquetes: `httr2`, `dplyr`, `lubridate`, `ggplot2`, `arrow`

### Python
- Python >= 3.11
- uv (gestor de paquetes)

## Instalación

### 1. Instalar dependencias de R con renv

```r
# Instalar renv si no lo tienes
install.packages("renv")

# Restaurar paquetes del proyecto desde el lockfile
renv::restore()
```

La primera vez que ejecutes `renv::restore()`, descargará e instalará las versiones exactas de los paquetes especificados en `renv.lock`:
- httr2 (1.2.1)
- dplyr (1.1.4)
- lubridate (1.9.4)
- ggplot2 (4.0.0)
- arrow (19.0.1.1)
- Y sus dependencias

**Nota:** renv usa un caché global, por lo que si ya tienes estas versiones instaladas en otros proyectos, solo creará enlaces simbólicos en lugar de descargarlas nuevamente.

### 2. Instalar dependencias de Python con uv

```bash
# Instalar uv si no lo tienes
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# Instalar dependencias del proyecto
uv sync
```

### 3. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y completar tus credenciales
# RAPIDAPI_KEY=tu_clave_aqui
```

**Obtener tu API key:**
1. Ve a [RapidAPI - OpenWeather](https://rapidapi.com/worldapi/api/open-weather13/)
2. Regístrate o inicia sesión
3. Suscríbete al plan (hay uno gratuito disponible)
4. Copia tu `X-RapidAPI-Key`
5. Pégala en el archivo `.env`

## Uso

### Paso 1: Obtener y procesar datos con R

Ejecuta el script R para obtener datos de la API:

```bash
Rscript get-weather.R
```

Este script:
1. Llama a la API de OpenWeather
2. Procesa los datos de temperatura
3. Exporta los resultados a `data/temp_data.feather` y `data/temp_diario.feather`
4. Genera un gráfico ggplot2 (mostrado en R)

### Paso 2: Ejecutar el dashboard de Streamlit

```bash
uv run streamlit run app.py
```

El dashboard se abrirá automáticamente en tu navegador (por defecto en http://localhost:8501).

## Estructura del Proyecto

```
api-weather/
├── get-weather.R          # Script R para obtener y procesar datos
├── app.py                 # Aplicación Streamlit (dashboard)
├── .env                   # Variables de entorno (API keys) - NO se sube a Git
├── .env.example           # Plantilla de variables de entorno
├── .gitignore             # Archivos excluidos de Git
├── .Rprofile              # Auto-activa renv para R
├── renv.lock              # Lock file de dependencias R
├── pyproject.toml         # Configuración de dependencias Python
├── uv.lock                # Lock file de dependencias Python
├── renv/                  # Gestión de paquetes R
│   ├── activate.R         # Script de bootstrap renv
│   ├── settings.json      # Configuración de renv
│   └── library/           # Biblioteca privada R (no en Git)
├── data/                  # Carpeta para archivos Feather (generados automáticamente)
│   ├── .gitkeep           # Mantiene la carpeta en Git
│   ├── temp_data.feather  # Generado por get-weather.R (no en Git)
│   └── temp_diario.feather # Generado por get-weather.R (no en Git)
├── .venv/                 # Entorno virtual Python (no en Git)
└── README.md
```

## Características del Dashboard

- **Métricas principales**: Temperatura promedio, máxima, mínima y amplitud térmica del día (con fecha específica)
- **Gráfico de pronóstico 5 días**: Visualización interactiva con Plotly mostrando rango min-max
- **Evolución por hora**: Gráfico detallado de temperaturas hora por hora para todo el período
- **Tablas de datos**:
  - Resumen diario con gradientes de color según temperatura
  - Datos por hora con filtro interactivo por fecha
- **Sidebar informativo**: Última actualización, período de pronóstico y estadísticas
- **Formato en español**: Fechas y textos completamente en español

## Tecnologías

### R
- `renv`: Gestión de dependencias y reproducibilidad
- `httr2`: Cliente HTTP para llamadas a API
- `dplyr`: Manipulación de datos
- `lubridate`: Manejo de fechas
- `ggplot2`: Visualización
- `arrow`: Exportación a formato Feather

### Python
- `streamlit`: Framework para el dashboard
- `pandas`: Manipulación de datos
- `pyarrow`: Lectura de archivos Feather
- `plotly`: Gráficos interactivos

## API

Este proyecto usa la API de OpenWeather a través de RapidAPI.

### Configuración de credenciales

El proyecto utiliza **variables de entorno** para proteger tus credenciales:

1. **Copia el archivo de plantilla:**
   ```bash
   cp .env.example .env
   ```

2. **Obtén tu API key:**
   - Ve a [RapidAPI - OpenWeather](https://rapidapi.com/worldapi/api/open-weather13/)
   - Regístrate y suscríbete al plan (hay uno gratuito)
   - Copia tu `X-RapidAPI-Key`

3. **Edita el archivo `.env`:**
   ```bash
   RAPIDAPI_KEY=tu_clave_aqui
   RAPIDAPI_HOST=open-weather13.p.rapidapi.com
   ```

**Seguridad:** El archivo `.env` está en `.gitignore` y nunca se subirá a GitHub. Comparte solo `.env.example`.

## Notas

- Los archivos `.feather` se sobrescriben en cada ejecución (no se guarda historial)
- Los datos son para Santiago, Chile (coordenadas: -33.447487, -70.673676)
- El pronóstico cubre los próximos 5 días
- Para cambiar la ubicación, modifica los parámetros `latitude` y `longitude` en `get-weather.R`
- **Seguridad**: El archivo `.env` con tus API keys está excluido de Git y nunca se subirá al repositorio

## Comandos Útiles

```bash
# Actualizar datos y ver dashboard
Rscript get-weather.R && uv run streamlit run app.py

# Solo actualizar dependencias Python
uv sync

# Ver paquetes Python instalados
uv pip list
```

```r
# Actualizar lockfile de R después de instalar/actualizar paquetes
renv::snapshot()

# Ver estado de los paquetes R
renv::status()

# Actualizar un paquete R específico
install.packages("nombre_paquete")
renv::snapshot()

# Restaurar paquetes R desde el lockfile
renv::restore()
```

## Troubleshooting

### Error: "Variables de entorno no configuradas"
- Asegúrate de haber creado el archivo `.env` copiando `.env.example`
- Verifica que `RAPIDAPI_KEY` tenga tu clave de API válida
- El archivo `.env` debe estar en la raíz del proyecto

### Error: "No se encontraron archivos de datos"
- Ejecuta primero `Rscript get-weather.R` para generar los archivos Feather

### Error al instalar paquete R `arrow`
```r
# En sistemas Unix/Mac, puede requerir dependencias del sistema
# Ubuntu/Debian
sudo apt-get install -y -V ca-certificates lsb-release wget
# Mac
brew install apache-arrow
```

### El dashboard no se actualiza
- Ejecuta nuevamente `Rscript get-weather.R`
- En Streamlit, usa el botón "Rerun" o presiona `R`

### Error de API (401 Unauthorized)
- Verifica que tu API key en `.env` sea correcta
- Asegúrate de estar suscrito al plan en RapidAPI
- Revisa que no hayas excedido el límite de requests del plan gratuito

## Licencia

Este proyecto es de código abierto para propósitos educativos.
