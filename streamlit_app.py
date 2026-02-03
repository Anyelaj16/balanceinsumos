import streamlit as st

from src.cliente import render_cliente_view
from src.direccion import render_direccion_view
from src.styles import apply_custom_css

# ---------------------------
# Configuración general
# ---------------------------
st.set_page_config(
    page_title="SIPOR | Balance de Insumos",
    layout="wide"
)

apply_custom_css()

# ---------------------------
# Navegación
# ---------------------------
st.sidebar.title("SIPOR")
vista = st.sidebar.radio(
    "Selecciona una vista",
    ["Cliente", "Dirección"]
)

if vista == "Cliente":
    render_cliente_view()
else:
    render_direccion_view()
