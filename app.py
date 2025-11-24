import streamlit as st
import pandas as pd
import pyarrow.feather as feather
import plotly.graph_objects as go
from datetime import datetime
import locale

# Configurar locale para español (con fallback a inglés si no está disponible)
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
    except:
        pass  # Si no se puede configurar español, se usa el locale por defecto

# Configuración de la página
st.set_page_config(
    page_title="Dashboard del Clima",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🌤️ Pronóstico del Clima - Santiago, Chile")

# Función para cargar datos
@st.cache_data
def load_data():
    try:
        temp_data = feather.read_table("data/temp_data.feather").to_pandas()
        temp_diario = feather.read_table("data/temp_diario.feather").to_pandas()

        # Convertir columnas de fecha
        temp_data['fecha_hora'] = pd.to_datetime(temp_data['fecha_hora'])
        temp_data['fecha'] = pd.to_datetime(temp_data['fecha'])
        temp_diario['fecha'] = pd.to_datetime(temp_diario['fecha'])

        return temp_data, temp_diario
    except FileNotFoundError:
        st.error("⚠️ No se encontraron archivos de datos. Por favor, ejecuta primero el script R: `Rscript get-weather.R`")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {e}")
        st.stop()

# Cargar datos
temp_data, temp_diario = load_data()

# Sidebar con información
with st.sidebar:
    st.header("ℹ️ Información")
    st.write(f"**Última actualización:** {temp_data['fecha_hora'].max().strftime('%Y-%m-%d %H:%M')}")
    st.write(f"**Total de registros:** {len(temp_data)}")
    st.write(f"**Período de pronóstico:** {temp_diario['fecha'].min().strftime('%Y-%m-%d')} a {temp_diario['fecha'].max().strftime('%Y-%m-%d')}")

    st.markdown("---")
    st.markdown("### 📊 Acerca de este dashboard")
    st.markdown("""
    Este dashboard muestra el pronóstico del clima para Santiago, Chile.

    **Datos:**
    - Fuente: OpenWeather API
    - Procesamiento: R (httr2, dplyr)
    - Visualización: Python (Streamlit, Plotly)
    """)

# Métricas principales
# Obtener datos del día actual (primera fecha disponible)
datos_hoy = temp_diario.iloc[0]
fecha_hoy_completa = datos_hoy['fecha'].strftime('%A %d de %B, %Y').capitalize()
fecha_hoy_corta = datos_hoy['fecha'].strftime('%d/%m/%Y')

st.header(f"📈 Métricas Principales - {fecha_hoy_corta}")
st.markdown(f"**Pronóstico para:** {fecha_hoy_completa}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🌡️ Temperatura Promedio",
        value=f"{datos_hoy['temp_promedio']:.1f}°C"
    )

with col2:
    st.metric(
        label="🔥 Temperatura Máxima",
        value=f"{datos_hoy['temp_max_dia']:.1f}°C"
    )

with col3:
    st.metric(
        label="❄️ Temperatura Mínima",
        value=f"{datos_hoy['temp_min_dia']:.1f}°C"
    )

with col4:
    amplitud = datos_hoy['temp_max_dia'] - datos_hoy['temp_min_dia']
    st.metric(
        label="📊 Amplitud Térmica",
        value=f"{amplitud:.1f}°C"
    )

st.markdown("---")

# Gráfico principal: Pronóstico 3 días
st.header("📊 Pronóstico de Temperatura - Próximos 5 Días")

fig = go.Figure()

# Banda de rango (min-max)
fig.add_trace(go.Scatter(
    x=temp_diario['fecha'],
    y=temp_diario['temp_max_dia'],
    fill=None,
    mode='lines',
    line=dict(width=0),
    showlegend=False,
    hoverinfo='skip'
))

fig.add_trace(go.Scatter(
    x=temp_diario['fecha'],
    y=temp_diario['temp_min_dia'],
    fill='tonexty',
    mode='lines',
    line=dict(width=0),
    fillcolor='rgba(173, 216, 230, 0.3)',
    name='Rango Min-Max',
    hoverinfo='skip'
))

# Línea de temperatura máxima
fig.add_trace(go.Scatter(
    x=temp_diario['fecha'],
    y=temp_diario['temp_max_dia'],
    mode='lines+markers',
    name='Temperatura Máxima',
    line=dict(color='#FF4B4B', width=3),
    marker=dict(size=10, symbol='circle'),
    hovertemplate='<b>Máxima</b><br>Fecha: %{x|%Y-%m-%d}<br>Temp: %{y:.1f}°C<extra></extra>'
))

# Línea de temperatura mínima
fig.add_trace(go.Scatter(
    x=temp_diario['fecha'],
    y=temp_diario['temp_min_dia'],
    mode='lines+markers',
    name='Temperatura Mínima',
    line=dict(color='#4B4BFF', width=3),
    marker=dict(size=10, symbol='circle'),
    hovertemplate='<b>Mínima</b><br>Fecha: %{x|%Y-%m-%d}<br>Temp: %{y:.1f}°C<extra></extra>'
))

# Línea de temperatura promedio
fig.add_trace(go.Scatter(
    x=temp_diario['fecha'],
    y=temp_diario['temp_promedio'],
    mode='lines+markers',
    name='Temperatura Promedio',
    line=dict(color='#2ECC71', width=2, dash='dash'),
    marker=dict(size=8, symbol='diamond'),
    hovertemplate='<b>Promedio</b><br>Fecha: %{x|%Y-%m-%d}<br>Temp: %{y:.1f}°C<extra></extra>'
))

fig.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Temperatura (°C)",
    hovermode='x unified',
    template='plotly_white',
    height=500,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Gráfico detallado por hora
st.header("🕐 Evolución de Temperatura por Hora")

fig_hora = go.Figure()

fig_hora.add_trace(go.Scatter(
    x=temp_data['fecha_hora'],
    y=temp_data['temp'],
    mode='lines',
    name='Temperatura',
    line=dict(color='#FF6B6B', width=2),
    hovertemplate='<b>Temperatura</b><br>%{x|%Y-%m-%d %H:%M}<br>%{y:.1f}°C<extra></extra>'
))

fig_hora.add_trace(go.Scatter(
    x=temp_data['fecha_hora'],
    y=temp_data['temp_max'],
    mode='lines',
    name='Máxima',
    line=dict(color='#FF4B4B', width=1, dash='dot'),
    hovertemplate='<b>Máxima</b><br>%{x|%Y-%m-%d %H:%M}<br>%{y:.1f}°C<extra></extra>'
))

fig_hora.add_trace(go.Scatter(
    x=temp_data['fecha_hora'],
    y=temp_data['temp_min'],
    mode='lines',
    name='Mínima',
    line=dict(color='#4B4BFF', width=1, dash='dot'),
    hovertemplate='<b>Mínima</b><br>%{x|%Y-%m-%d %H:%M}<br>%{y:.1f}°C<extra></extra>'
))

fig_hora.update_layout(
    xaxis_title="Fecha y Hora",
    yaxis_title="Temperatura (°C)",
    hovermode='x unified',
    template='plotly_white',
    height=400,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig_hora, use_container_width=True)

st.markdown("---")

# Tablas de datos
st.header("📋 Datos Detallados")

tab1, tab2 = st.tabs(["📅 Resumen Diario", "🕐 Datos por Hora"])

with tab1:
    st.subheader("Resumen Diario de Temperaturas")

    # Formatear el DataFrame para mostrar
    temp_diario_display = temp_diario.copy()
    temp_diario_display['fecha'] = temp_diario_display['fecha'].dt.strftime('%Y-%m-%d')
    temp_diario_display.columns = ['Fecha', 'Temp. Mínima (°C)', 'Temp. Máxima (°C)', 'Temp. Promedio (°C)']

    st.dataframe(
        temp_diario_display.style.format({
            'Temp. Mínima (°C)': '{:.1f}',
            'Temp. Máxima (°C)': '{:.1f}',
            'Temp. Promedio (°C)': '{:.1f}'
        }).background_gradient(subset=['Temp. Mínima (°C)', 'Temp. Máxima (°C)', 'Temp. Promedio (°C)'], cmap='RdYlBu_r'),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.subheader("Datos por Hora")

    # Filtro por fecha
    fechas_disponibles = temp_data['fecha'].unique()
    fecha_seleccionada = st.selectbox(
        "Selecciona una fecha:",
        options=fechas_disponibles,
        format_func=lambda x: pd.to_datetime(x).strftime('%Y-%m-%d')
    )

    # Filtrar datos por fecha seleccionada
    temp_data_filtrado = temp_data[temp_data['fecha'] == fecha_seleccionada].copy()
    temp_data_filtrado['fecha_hora'] = temp_data_filtrado['fecha_hora'].dt.strftime('%Y-%m-%d %H:%M')
    temp_data_filtrado = temp_data_filtrado[['fecha_hora', 'temp', 'temp_min', 'temp_max']]
    temp_data_filtrado.columns = ['Fecha y Hora', 'Temperatura (°C)', 'Temp. Mínima (°C)', 'Temp. Máxima (°C)']

    st.dataframe(
        temp_data_filtrado.style.format({
            'Temperatura (°C)': '{:.1f}',
            'Temp. Mínima (°C)': '{:.1f}',
            'Temp. Máxima (°C)': '{:.1f}'
        }).background_gradient(subset=['Temperatura (°C)', 'Temp. Mínima (°C)', 'Temp. Máxima (°C)'], cmap='RdYlBu_r'),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🌤️ Dashboard del Clima • Datos de OpenWeather API • Generado con Streamlit</p>
</div>
""", unsafe_allow_html=True)
