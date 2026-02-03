"""
SIPOR Dashboard - Data Loader
Handles loading and validation of data from Excel
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Cached function to load the raw Excel file
@st.cache_data(ttl=300)
def load_raw_data(file_path='Balance_Insumos.xlsx'):

    """
    Load raw data from Excel file
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        pd.DataFrame: Raw data from Base_Operacion sheet
    """
    try:
        if not os.path.exists(file_path):
            st.error(f"❌ Archivo no encontrado: {file_path}")
            return pd.DataFrame()
        
        # Read the specific sheet
        df = pd.read_excel(file_path, sheet_name='Base_Operacion', engine='openpyxl')
        
        # Standardize column names (strip whitespace, lowercase)
        df.columns = df.columns.astype(str).str.strip().str.lower()
        
        # Map expected columns to standardized names if needed, or just use as is
        # Expected from prompt: Fecha, Zona, SubZona, insumo, subtipo_insumo, 
        # tipo_registro, estado, tipo_evento, turno, cantidad
        
        # Ensure date column is datetime
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            
        # Ensure numeric quantity
        if 'cantidad' in df.columns:
            df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
            
        return df
        
    except Exception as e:
        st.error(f"❌ Error al cargar archivo Excel: {str(e)}")
        return pd.DataFrame()

def load_inventario():
    """
    Get inventory data (tipo_registro = 'estado')
    
    Returns:
        pd.DataFrame: Inventory data
    """
    df = load_raw_data()
    
    if df.empty:
        return df
        
    # Filter for inventory state
    if 'tipo_registro' in df.columns:
        # Case insensitive check
        mask = df['tipo_registro'].astype(str).str.strip().str.lower() == 'estado'
        df_inv = df[mask].copy()
        
        # Validate critical columns for inventory
        required = ['fecha', 'zona', 'subzona', 'insumo', 'cantidad', 'estado']
        missing = [col for col in required if col not in df_inv.columns]
        
        if missing:
            st.warning(f"⚠️ Columnas faltantes para inventario: {', '.join(missing)}")
            return pd.DataFrame()
            
        return df_inv
    
    return pd.DataFrame()

def load_eventos():
    """
    Get events data (tipo_registro = 'evento')
    
    Returns:
        pd.DataFrame: Events data
    """
    df = load_raw_data()
    
    if df.empty:
        return df
        
    # Filter for events
    if 'tipo_registro' in df.columns:
        # Case insensitive check
        mask = df['tipo_registro'].astype(str).str.strip().str.lower() == 'evento'
        df_evt = df[mask].copy()
        
        # Validate critical columns for events
        required = ['fecha', 'zona', 'insumo', 'cantidad', 'tipo_evento', 'turno']
        missing = [col for col in required if col not in df_evt.columns]
        
        if missing:
            st.warning(f"⚠️ Columnas faltantes para eventos: {', '.join(missing)}")
            return pd.DataFrame()
            
        # Standardize event type
        if 'tipo_evento' in df_evt.columns:
            df_evt['tipo_evento'] = df_evt['tipo_evento'].astype(str).str.strip().str.title()
            
        return df_evt
    
    return pd.DataFrame()

def get_unique_values(df, column):
    """
    Get sorted unique values from a column
    """
    if df.empty or column not in df.columns:
        return []
    
    return sorted(df[column].astype(str).replace('nan', 'N/A').unique().tolist())

def validate_data_exists(df, source_name="datos"):
    """
    Check if dataframe has data
    """
    if df.empty:
        st.warning(f"⚠️ No se encontraron datos válidos para {source_name}")
        return False
    return True

def get_date_range(df, column='fecha'):
    """Get min and max date"""
    if df.empty or column not in df.columns:
        return None, None
    return df[column].min(), df[column].max()

def filter_by_date_range(df, start_date, end_date, column='fecha'):
    """Filter by date range"""
    if df.empty or column not in df.columns:
        return df
    
    mask = (df[column] >= pd.to_datetime(start_date)) & (df[column] <= pd.to_datetime(end_date))
    return df[mask]
