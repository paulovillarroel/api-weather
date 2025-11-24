# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Weather Dashboard for Santiago, Chile - A bilingual (R + Python) data pipeline and visualization project.

**Data Flow:**
1. R script (`get-weather.R`) fetches weather data from OpenWeather API via RapidAPI
2. Data is processed and exported to Apache Feather format (`.feather` files)
3. Python/Streamlit app (`app.py`) reads Feather files and displays interactive dashboard

**Key Architecture Decision:** Using Apache Feather (via `arrow` package) as the bridge format between R and Python ensures fast, zero-copy data sharing without serialization overhead.

## Development Commands

### Initial Setup (First Time)

```bash
# 1. Configure API credentials
cp .env.example .env
# Edit .env and add your RAPIDAPI_KEY

# 2. Install R dependencies
```

```r
# In R console:
install.packages("renv")
renv::restore()
```

```bash
# 3. Install Python dependencies
uv sync
```

### Regular Development Workflow

```bash
# Fetch fresh weather data (regenerates .feather files in data/)
Rscript get-weather.R

# Run Streamlit dashboard
uv run streamlit run app.py

# One-liner to update data and launch dashboard
Rscript get-weather.R && uv run streamlit run app.py
```

### Dependency Management

**Python (uv):**
```bash
# Add new package
uv add package-name

# Update dependencies
uv sync

# List installed packages
uv pip list
```

**R (renv):**
```r
# Install new package
install.packages("package-name")
renv::snapshot()  # Update renv.lock

# Check for package issues
renv::status()

# Restore packages from lockfile
renv::restore()
```

## Code Architecture

### R Side (`get-weather.R`)

**Environment Variables:**
- Reads `.env` file using `readRenviron()` for API credentials
- Validates `RAPIDAPI_KEY` and `RAPIDAPI_HOST` before API call
- Stops execution with clear error if credentials are missing

**API Integration:**
- Uses `httr2` for HTTP requests (modern alternative to `httr`)
- Fetches 5-day forecast from OpenWeather API
- Coordinates hardcoded for Santiago, Chile: `-33.447487, -70.673676`

**Data Processing Pipeline:**
1. Parse JSON response to extract hourly forecast (`json_data$list`)
2. Convert Kelvin temperatures to Celsius (`temp - 273.15`)
3. Create two datasets:
   - `temp_data`: Hourly data with `fecha_hora`, `temp`, `temp_min`, `temp_max`
   - `temp_diario`: Daily aggregates (min, max, mean per day, limited to 5 days)
4. Export both to `data/temp_data.feather` and `data/temp_diario.feather`

**Visualization:**
- Generates a ggplot2 preview with ribbon plot (min-max range) and line plots
- Not used by Streamlit (display-only for R users)

### Python Side (`app.py`)

**Data Loading:**
- Uses `@st.cache_data` decorator on `load_data()` function
- Reads both Feather files using `pyarrow.feather`
- Converts date columns to pandas datetime
- Shows clear error if Feather files don't exist (directs user to run R script)

**Spanish Locale Configuration:**
- Attempts to set locale to Spanish for date formatting
- Falls back gracefully if Spanish locale not available on system
- Uses `locale.setlocale()` with multiple fallback attempts (Linux vs Windows locale names)

**Dashboard Structure:**

1. **Sidebar:**
   - Last update timestamp
   - Total records count
   - Forecast period range

2. **Main Metrics (Top Row):**
   - Gets first row from `temp_diario` (earliest date)
   - Displays 4 metrics: avg temp, max temp, min temp, thermal amplitude
   - Shows specific date in header and subtitle

3. **5-Day Forecast Chart (Plotly):**
   - Uses `go.Scatter` with `fill='tonexty'` for min-max range shading
   - Three lines: max (red), min (blue), average (green dashed)
   - Unified hover mode for comparing values

4. **Hourly Evolution Chart:**
   - All hourly data points with temperature, temp_max, temp_min
   - Dotted lines for max/min bounds

5. **Data Tables:**
   - Tab 1: Daily summary with gradient coloring
   - Tab 2: Hourly data with date filter dropdown

**Styling:**
- Uses custom CSS for footer
- Applies color gradients to dataframes with `.style.background_gradient()`
- Color scheme: red (hot) to blue (cold)

## Important Technical Details

### Cross-Language Dependencies

Both languages have locked dependencies for reproducibility:
- **R:** `renv.lock` with 40 packages (R 4.5.1)
- **Python:** `uv.lock` with packages for Python >=3.11

Key package versions:
- R: `httr2` 1.2.1, `dplyr` 1.1.4, `arrow` 19.0.1.1
- Python: `streamlit` >=1.28.0, `pandas` >=2.0.0, `pyarrow` >=13.0.0

### Data Contract Between R and Python

The Feather files must maintain this schema:

**`temp_data.feather`:**
- `fecha_hora`: datetime (UTC timezone)
- `temp`: float (Celsius)
- `temp_min`: float (Celsius)
- `temp_max`: float (Celsius)
- `fecha`: date

**`temp_diario.feather`:**
- `fecha`: date
- `temp_min_dia`: float (daily minimum)
- `temp_max_dia`: float (daily maximum)
- `temp_promedio`: float (daily average)

Breaking this schema will cause the Streamlit app to fail.

### API Rate Limits

RapidAPI OpenWeather endpoint has rate limits on free tier. If you get 429 errors:
- Check request count in RapidAPI dashboard
- Consider caching Feather files instead of re-fetching constantly
- Implement rate limiting in R script if running frequently

### Changing Location

To forecast a different city, modify `get-weather.R` lines 26-27:
```r
latitude = "NEW_LAT",
longitude = "NEW_LON",
```

You'll also want to update the hardcoded "Santiago, Chile" strings in:
- `app.py` line 16 (title)
- `get-weather.R` line 72 (ggplot subtitle)
- `README.md` title and descriptions

## Testing the Data Pipeline

Since there are no automated tests, manually verify:

1. **R script output:**
   ```bash
   Rscript get-weather.R
   # Should print hourly data table, daily summary, and show ggplot
   # Should create data/temp_data.feather (40 rows) and data/temp_diario.feather (5 rows)
   ```

2. **Feather file integrity:**
   ```r
   # In R:
   arrow::read_feather("data/temp_data.feather")
   arrow::read_feather("data/temp_diario.feather")
   ```

3. **Streamlit dashboard:**
   ```bash
   uv run streamlit run app.py
   # Should load without errors and show metrics for the earliest date
   ```

## Environment Files

**`.env` (not in Git):**
```
RAPIDAPI_KEY=your_actual_key_here
RAPIDAPI_HOST=open-weather13.p.rapidapi.com
```

**`.env.example` (in Git):**
Template file with placeholder values. New contributors copy this to `.env` and fill in their credentials.

## Known Limitations

- No historical data storage (Feather files overwritten each run)
- No error handling for API failures beyond basic validation
- Hardcoded to Santiago, Chile coordinates
- No automated testing
- Date formatting may show English names if Spanish locale unavailable
- Streamlit caches data - users must click "Rerun" or press R after updating data
