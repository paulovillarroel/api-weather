library(httr2)
library(dplyr)
library(lubridate)
library(ggplot2)
library(arrow)

# Cargar variables de entorno desde .env
if (file.exists(".env")) {
  readRenviron(".env")
}

# Obtener API key desde variables de entorno
api_key <- Sys.getenv("RAPIDAPI_KEY")
api_host <- Sys.getenv("RAPIDAPI_HOST")

# Validar que las variables de entorno estén configuradas
if (api_key == "" || api_host == "") {
  stop(
    "Error: Variables de entorno no configuradas. Copia .env.example a .env y completa tus credenciales."
  )
}

url <- "https://open-weather13.p.rapidapi.com/fivedaysforcast"

response <- request(url) |>
  req_url_query(
    latitude = "-33.447487",
    longitude = "-70.673676",
    lang = "EN"
  ) |>
  req_headers(
    `x-rapidapi-key` = api_key,
    `x-rapidapi-host` = api_host
  ) |>
  req_perform()

json_data <- resp_body_json(response, simplifyVector = TRUE)


# ===== VISUALIZACIÓN SIMPLIFICADA DE TEMPERATURAS =====

temp_data <- data.frame(
  fecha_hora = as.POSIXct(json_data$list$dt, origin = "1970-01-01", tz = "UTC"),
  temp = json_data$list$main$temp - 273.15,
  temp_min = json_data$list$main$temp_min - 273.15,
  temp_max = json_data$list$main$temp_max - 273.15
)

temp_data$fecha <- as.Date(temp_data$fecha_hora)

print("=== DATOS POR HORA ===")
print(temp_data)

# Resumen diario de temperaturas
temp_diario <- temp_data |>
  group_by(fecha) |>
  summarise(
    temp_min_dia = min(temp_min),
    temp_max_dia = max(temp_max),
    temp_promedio = mean(temp)
  ) |>
  ungroup() |>
  head(5)

print("\n=== PRONÓSTICO 5 DÍAS (Min/Max por día) ===")
print(temp_diario)

# Gráfico de evolución de temperaturas
grafico_temp <- ggplot(temp_diario, aes(x = fecha)) +
  geom_ribbon(
    aes(ymin = temp_min_dia, ymax = temp_max_dia),
    fill = "lightblue",
    alpha = 0.5
  ) +
  geom_line(aes(y = temp_max_dia, color = "Máxima"), linewidth = 1.2) +
  geom_line(aes(y = temp_min_dia, color = "Mínima"), linewidth = 1.2) +
  geom_line(
    aes(y = temp_promedio, color = "Promedio"),
    linewidth = 1,
    linetype = "dashed"
  ) +
  geom_point(aes(y = temp_max_dia, color = "Máxima"), size = 3) +
  geom_point(aes(y = temp_min_dia, color = "Mínima"), size = 3) +
  scale_color_manual(
    values = c("Máxima" = "red", "Mínima" = "blue", "Promedio" = "darkgreen")
  ) +
  labs(
    title = "Pronóstico de Temperatura - Próximos 5 Días",
    subtitle = "Santiago, Chile",
    x = "Fecha",
    y = "Temperatura (°C)",
    color = "Tipo"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16),
    plot.subtitle = element_text(hjust = 0.5, size = 12),
    legend.position = "bottom"
  )

print(grafico_temp)

# ===== EXPORTAR DATOS PARA STREAMLIT =====

write_feather(temp_data, "data/temp_data.feather")
write_feather(temp_diario, "data/temp_diario.feather")

cat("\n\n=== DATOS EXPORTADOS A FEATHER ===\n")
cat("✓ data/temp_data.feather\n")
cat("✓ data/temp_diario.feather\n")
cat("\nAhora puedes ejecutar el dashboard con: uv run streamlit run app.py\n")
