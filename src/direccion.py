"""
SIPOR Dashboard - Vista Dirección
Análisis operativo y toma de decisiones
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

from src.styles import COLORS, show_header, create_metric_card, get_plotly_template
from src.loader import load_inventario, load_eventos, validate_data_exists, get_date_range, filter_by_date_range, get_unique_values

def render_direccion_view():
    """Render the management/direction view dashboard"""
    
    # Header
    show_header(
        "Vista Dirección",
        "Análisis operativo: productividad, reparaciones y variaciones"
    )
    
    # Load data
    df_eventos = load_eventos()
    df_inventario = load_inventario()
    
    if not validate_data_exists(df_eventos, "Eventos"):
        return
    
    # --- Date Range Logic (Fixed 30 Days) ---
    # User requested REMOVAL of date inputs. We will auto-select the last 30 days of available data.
    min_date_evt, max_date_evt = get_date_range(df_eventos)
    
    if not max_date_evt:
        st.error("No hay fechas válidas en el registro de eventos")
        return

    # Default to last 30 days from the latest event
    end_date = max_date_evt
    start_date = max_date_evt - timedelta(days=30)
    
    # Ensure start date is not before the earliest available data
    if min_date_evt and start_date < min_date_evt:
        start_date = min_date_evt

    st.info(f"📅 Analizando período: **{start_date.strftime('%d-%m-%Y')}** al **{end_date.strftime('%d-%m-%Y')}** (Últimos 30 días operables)")

    # --- Sidebar Filters ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filtros Operativos")
    
    # Filter Events by the fixed date range
    df_filtered_evt = filter_by_date_range(df_eventos, start_date, end_date)
    
    # Additional filters for Events
    turnos = get_unique_values(df_filtered_evt, 'turno')
    selected_turnos = st.sidebar.multiselect("Turnos", options=turnos, default=turnos)
    
    zonas = get_unique_values(df_filtered_evt, 'zona')
    selected_zonas = st.sidebar.multiselect("Zonas", options=zonas, default=zonas, key="dir_zonas")
    
    # Apply context filters
    if selected_turnos:
        df_filtered_evt = df_filtered_evt[df_filtered_evt['turno'].isin(selected_turnos)]
    if selected_zonas:
        df_filtered_evt = df_filtered_evt[df_filtered_evt['zona'].isin(selected_zonas)]

    if df_filtered_evt.empty:
        st.warning("⚠️ No hay eventos para los filtros seleccionados en este período")
    
    # --- SECTION 1: EVENT ANALYSIS (Repairs / Write-offs) ---
    st.markdown("## 🛠️ Productividad y Eventos")
    
    # KPIs
    total_reparadas = df_filtered_evt[df_filtered_evt['tipo_evento'] == 'Reparada']['cantidad'].sum()
    total_bajas = df_filtered_evt[df_filtered_evt['tipo_evento'] == 'Baja']['cantidad'].sum()
    
    # Trend Logic
    period_days = (end_date - start_date).days
    prev_start = start_date - timedelta(days=period_days)
    prev_end = start_date - timedelta(days=1)
    df_prev = filter_by_date_range(df_eventos, prev_start, prev_end)
    
    total_reparadas_prev = df_prev[df_prev['tipo_evento'] == 'Reparada']['cantidad'].sum()
    
    delta_rep = None
    if total_reparadas_prev > 0:
        pct = ((total_reparadas - total_reparadas_prev) / total_reparadas_prev) * 100
        delta_rep = f"{pct:+.1f}%"
        
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        create_metric_card("Reparaciones", f"{int(total_reparadas):,}", delta=delta_rep)
    with col2:
        create_metric_card("Bajas", f"{int(total_bajas):,}")
    with col3:
        # Efficiency by shift
        shift_sum = df_filtered_evt.groupby('turno', as_index=False)['cantidad'].sum()
        if shift_sum.empty:
            best_shift = "N/A"
        else:
            best_shift = shift_sum.loc[shift_sum['cantidad'].idxmax(), 'turno']
            
        create_metric_card("Turno +Activo", str(best_shift))
        
    with col4:
         # Efficiency by zone
        zona_sum = df_filtered_evt.groupby('zona', as_index=False)['cantidad'].sum()
        if zona_sum.empty:
            best_zone = "N/A"
        else:
            best_zone = zona_sum.loc[zona_sum['cantidad'].idxmax(), 'zona']
            
        create_metric_card("Zona +Activa", str(best_zone))

    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Tendencia de Eventos")
        df_time = df_filtered_evt.groupby(['fecha', 'tipo_evento'])['cantidad'].sum().reset_index()
        fig = px.line(
            df_time, x='fecha', y='cantidad', color='tipo_evento',
            markers=True,
            color_discrete_map={'Reparada': COLORS['success'], 'Baja': COLORS['danger']}
        )
        fig.update_layout(**get_plotly_template()['layout'])
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("### Productividad por Turno")
        df_shift = df_filtered_evt.groupby(['turno', 'tipo_evento'])['cantidad'].sum().reset_index()
        fig = px.bar(
            df_shift, x='turno', y='cantidad', color='tipo_evento',
            barmode='group',
            color_discrete_map={'Reparada': COLORS['success'], 'Baja': COLORS['danger']}
        )
        fig.update_layout(**get_plotly_template()['layout'])
        st.plotly_chart(fig, use_container_width=True)

    # --- SECTION 2: INVENTORY VARIATIONS (Deltas) ---
    if not df_inventario.empty:
        st.markdown("## 📈 Variación de Stocks (Deltas)")
        
        # Calculate Delta: Value at End Date - Value at Start Date
        # Filter dates strictly
        df_inv_period = filter_by_date_range(df_inventario, start_date, end_date)
        
        if not df_inv_period.empty:
            actual_min_date = df_inv_period['fecha'].min()
            actual_max_date = df_inv_period['fecha'].max()
            
            if actual_min_date != actual_max_date:
                # Group by Insumo (and Zone/Subzone if needed) for Start and End dates
                # Using 'insumo' for broad overview
                
                df_start = df_inv_period[df_inv_period['fecha'] == actual_min_date].groupby('insumo')['cantidad'].sum()
                df_end = df_inv_period[df_inv_period['fecha'] == actual_max_date].groupby('insumo')['cantidad'].sum()
                
                # Combine
                df_deltas = pd.DataFrame({'Inicio': df_start, 'Fin': df_end}).fillna(0)
                df_deltas['Delta'] = df_deltas['Fin'] - df_deltas['Inicio']
                df_deltas['Delta %'] = (df_deltas['Delta'] / df_deltas['Inicio'] * 100).fillna(0)
                df_deltas = df_deltas.reset_index()
                
                # Visualizing Deltas
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"### Mayores Aumentos (vs {actual_min_date.strftime('%d-%m')})")
                    df_incr = df_deltas[df_deltas['Delta'] > 0].sort_values('Delta', ascending=False).head(5)
                    if not df_incr.empty:
                        fig = px.bar(
                            df_incr, y='insumo', x='Delta', orientation='h',
                            text='Delta',
                            color_discrete_sequence=[COLORS['success']]
                        )
                        fig.update_traces(texttemplate='+%{text:,.0f}')
                        fig.update_layout(**get_plotly_template()['layout'])
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No hubo aumentos significativos en este período.")

                with col2:
                    st.markdown(f"### Mayores Disminuciones (vs {actual_min_date.strftime('%d-%m')})")
                    df_decr = df_deltas[df_deltas['Delta'] < 0].sort_values('Delta', ascending=True).head(5)
                    if not df_decr.empty:
                        fig = px.bar(
                            df_decr, y='insumo', x='Delta', orientation='h',
                            text='Delta',
                            color_discrete_sequence=[COLORS['danger']]
                        )
                        fig.update_traces(texttemplate='%{text:,.0f}')
                        fig.update_layout(**get_plotly_template()['layout'])
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No hubo disminuciones significativas en este período.")
            else:
                st.info("⚠️ El rango de fechas seleccionado no tiene suficiente amplitud para calcular variaciones (Deltas).")
        else:
            st.warning("No hay datos de inventario en el rango seleccionado.")
