import streamlit as st

from src.cliente import render_cliente_view
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
# Vista Cliente (ÚNICA)
# ---------------------------
render_cliente_view()

