"""
SIPOR Dashboard - Vista Cliente
Reporte Final PDF (Header Yara / Gráficas Agrupadas)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import base64

from src.styles import COLORS, PATIO_WARM, BODEGA_COLD, show_header, get_plotly_template
from src.loader import load_inventario, validate_data_exists

def render_cliente_view():
    """Render the client view as a static PDF report with Yara branding"""
    
    # 1. Load Data
    df_inventario = load_inventario()
    if not validate_data_exists(df_inventario, "Inventario"):
        return
    
    # Snapshot Logic
    latest_date = df_inventario['fecha'].max()
    df = df_inventario[df_inventario['fecha'] == latest_date].copy()
    
    # --- 1. ENCABEZADO YARA (Contextual) ---
    c_head1, c_head2 = st.columns([0.5, 6])
    with c_head1:
        # Yara Logo - Small
        try:
             st.image("assets/yara_logo.png", width=40)
        except:
             st.markdown("**YARA**")
             
    with c_head2:
        # Styled Text inline-ish
        st.markdown(f"""
        <div style="display: flex; align-items: center; height: 40px;">
            <span style="font-family: Arial, sans-serif; font-size: 16px; color: {COLORS['dark']}; margin-right: 20px;">
                Yara – Planta Sur · CTG
            </span>
            <span style="border-left: 2px solid #ddd; height: 20px; margin-right: 20px;"></span>
            <span style="font-family: Arial, sans-serif; font-size: 14px; color: {COLORS['gray']};">
                Corte: <b>{latest_date.strftime('%d-%m-%Y')}</b>
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"<h3 style='text-align:center; margin-top:-20px; color:{COLORS['blue']}'>BALANCE ACTUAL DE INSUMOS</h3>", unsafe_allow_html=True)
    st.markdown("---")

    # Data Subsets
    df_estibas = df[df['insumo'].astype(str).str.contains("Estiba", case=False, na=False)]
    df_carpas = df[df['insumo'].astype(str).str.contains("Carpa", case=False, na=False)]
    df_plasticos = df[df['insumo'].astype(str).str.contains("Plastico|Plástico", case=False, na=False)]
    df_espacios = df[df['insumo'].astype(str).str.contains("Espacio", case=False, na=False)]

    # --- 2. KPIs (UNA SOLA FILA) ---
    k1, k2, k3, k4 = st.columns(4)
    
    # ESTIBAS
    with k1:
        render_kpi_group("ESTIBAS", df_estibas, ['Disponible', 'Por Reparar']) 
        
    # CARPAS
    with k2:
        render_kpi_group("CARPAS", df_carpas, ['Disponible', 'Por Reparar'])
        
    # PLASTICOS
    with k3:
        render_kpi_group("PLÁSTICOS", df_plasticos, ['Disponible'])
        
    # ESPACIOS
    with k4:
        render_espacios_kpi(df_espacios)
        
    st.markdown("---")

    # ... (Charts Section) ...
    
    # Store figures for PDF
    figs = {
        'estibas': None,
        'carpas': None,
        'plasticos': None,
        'espacios': None
    }

    # Chart 1: Estibas
    if not df_estibas.empty:
        figs['estibas'] = create_subzone_grouped_chart(df_estibas, "Estibas")
        st.plotly_chart(figs['estibas'], use_container_width=True)
    
    # Chart 2: Carpas
    if not df_carpas.empty:
        st.markdown("---")
        figs['carpas'] = create_subzone_grouped_chart(df_carpas, "Carpas")
        st.plotly_chart(figs['carpas'], use_container_width=True)
        
    # Chart 3: Plasticos
    if not df_plasticos.empty:
        st.markdown("---")
        figs['plasticos'] = create_subzone_grouped_chart(df_plasticos, "Plásticos")
        st.plotly_chart(figs['plasticos'], use_container_width=True)

    # Chart 4: Espacios
    if not df_espacios.empty:
        st.markdown("---")
        st.markdown(f"#### 🏗️ Disponibilidad de Espacios")
        figs['espacios'] = create_espacios_chart(df_espacios)
        st.plotly_chart(figs['espacios'], use_container_width=True)

    # --- PDF EXPORT LOGIC ---
    # Moved to sidebar or bottom? User wants "Button".
    st.markdown("---")
    
    # Prepare Data for PDF KPIs
    # Helper to sum up states
    def sum_state(d, s): 
        # Flexible match
        return d[d['estado'].astype(str).str.contains(s, case=False, na=False)]['cantidad'].sum() if not d.empty else 0

    kpi_data = {
        'estibas': {
            'disponible': sum_state(df_estibas, 'disponible'),
            'reparar': sum_state(df_estibas, 'reparar'),
            'clasificar': sum_state(df_estibas, 'clasificar')
        },
        'carpas': {
            'disponible': sum_state(df_carpas, 'disponible'),
            'reparar': sum_state(df_carpas, 'reparar'),
            'clasificar': sum_state(df_carpas, 'clasificar')
        },
        'plasticos': {
            'disponible': sum_state(df_plasticos, 'disponible'),
            'reparar': sum_state(df_plasticos, 'reparar')
        },
        'espacios': {
            'total': df_espacios['cantidad'].sum() if not df_espacios.empty else 0,
            'sizes': {}
        }
    }
    
    if not df_espacios.empty:
       brk = 'subtipo_insumo' if 'subtipo_insumo' in df_espacios.columns else 'insumo'
       for k, v in df_espacios.groupby(brk)['cantidad'].sum().sort_values(ascending=False).items():
           if v > 0: kpi_data['espacios']['sizes'][k] = v



    # --- PDF/HTML EXPORT BUTTON ---
    st.markdown("---")
    
    try:
        from src.pdf_report import build_pdf_html
        import base64
        import plotly.io as pio
        
        # Set default renderer to use kaleido
        pio.renderers.default = "png"
        
        # if st.button("📥 Descargar Reporte PDF Ejecutivo"):
        #     with st.spinner("Generando reporte..."):
        #         try:
        #             # Prepare KPI data for PDF
        #             pdf_kpis = {
        #                 "ESTIBAS": {
        #                     "Disponibles": int(kpi_data['estibas']['disponible']),
        #                     "Reparar": int(kpi_data['estibas']['reparar']),
        #                     "Clasificar": int(kpi_data['estibas']['clasificar'])
        #                 },
        #                 "CARPAS": {
        #                     "Disponibles": int(kpi_data['carpas']['disponible']),
        #                     "Reparar": int(kpi_data['carpas']['reparar']),
        #                     "Clasificar": int(kpi_data['carpas']['clasificar'])
        #                 },
        #                 "PLÁSTICOS": {
        #                     "Disponibles": int(kpi_data['plasticos']['disponible']),
        #                     "Reparar": int(kpi_data['plasticos']['reparar'])
        #                 },
        #                 "ESPACIOS": {
        #                     "Total": int(kpi_data['espacios']['total']),
        #                     **{f"{k}": int(v) for k, v in list(kpi_data['espacios']['sizes'].items())[:3]}
        #                 }
        #             }
        #             
        #             # Convert Plotly figures to static images (base64) using Kaleido
        #             charts_html = ""
        #             for fig_name, fig in [('estibas', figs['estibas']), 
        #                                  ('carpas', figs['carpas']),
        #                                  ('plasticos', figs['plasticos']),
        #                                  ('espacios', figs['espacios'])]:
        #                 if fig is not None:
        #                     # Convert to static image using kaleido explicitly
        #                     img_bytes = fig.to_image(
        #                         format="png", 
        #                         engine="kaleido",
        #                         width=600, 
        #                         height=300, 
        #                         scale=2
        #                     )
        #                     img_b64 = base64.b64encode(img_bytes).decode()
        #                     charts_html += f'<div class="chart"><img src="data:image/png;base64,{img_b64}"></div>'
        #             
        #             # Generate HTML
        #             html = build_pdf_html(
        #                 fecha=latest_date.strftime("%d-%m-%Y"),
        #                 kpis=pdf_kpis,
        #                 charts_html=charts_html
        #             )
        #             
        #             # Download as HTML file (user can print to PDF from browser)
        #             st.download_button(
        #                 label="⬇️ Guardar Reporte HTML",
        #                 data=html.encode('utf-8'),
        #                 file_name=f"SIPOR_Balance_{latest_date.strftime('%Y%m%d')}.html",
        #                 mime="text/html"
        #             )
        #             
        #             st.success("✅ Reporte generado! Abre el archivo HTML y usa Ctrl+P → Guardar como PDF")
        #             st.info("""
        #             📄 **Cómo convertir a PDF:**
        #             1. Abre el archivo HTML descargado
        #             2. Presiona Ctrl+P (Cmd+P en Mac)  
        #             3. Selecciona "Guardar como PDF"
        #             4. Guarda el PDF
        #             """)
        #         
        #         except Exception as e:
        #             st.error(f"Error al generar reporte: {str(e)}")
        #         
    except ImportError as e:
        # st.warning("Kaleido no está instalado")
        pass

# --- HELPER FUNCTIONS ---

def render_kpi_group(title, df, focus_states):
    st.markdown(f"**{title}**")
    if df.empty:
        st.caption("-")
        return
        
    df_st = df.groupby('estado')['cantidad'].sum().reset_index()
    
    def get_val(term):
        match = df_st[df_st['estado'].astype(str).str.contains(term, case=False, na=False)]
        return match['cantidad'].sum() if not match.empty else 0
    
    # Render metrics
    has_val = False
    for state in focus_states:
        val = get_val(state)
        # Map fuzzy terms
        if 'Reparar' in state: val = get_val('reparar')
        if 'Disponible' in state: val = get_val('disponible')
        
        if val > 0:
            st.metric(state, f"{int(val):,}")
            has_val = True
            
    # Check for 'Clasificar' explicitly for all groups if > 0
    val_clas = get_val('clasificar')
    if val_clas > 0:
        st.metric("Por Clasificar", f"{int(val_clas):,}")
        has_val = True
            
    if not has_val:
        st.caption("Sin inventario")

def render_espacios_kpi(df):
    st.markdown("**ESPACIOS**")
    if df.empty:
        st.caption("-")
        return
    
    total = df['cantidad'].sum()
    if total > 0:
        st.metric("Total", f"{int(total):,}")
        
        breakdown_col = 'subtipo_insumo' if 'subtipo_insumo' in df.columns else 'insumo'
        sizes = df.groupby(breakdown_col)['cantidad'].sum().sort_values(ascending=False)
        
        txt = []
        for s, v in sizes.items():
            if v > 0:
                txt.append(f"{s}: {int(v)}")
        if txt:
            st.caption(" | ".join(txt))
    else:
        st.caption("Sin espacios")

def get_location_type(zona_name):
    """Normalize and categorize based on ZONA column only"""
    s = str(zona_name).strip().upper()
    if 'PATIO' in s: return 'Patios'
    if 'BODEGA' in s: return 'Bodegas'
    return 'Patios' # Fallback for safety or exclude? User said "Otros" must not exist. 
    # If data has bad zones, we might prefer "Otros" but user forbids it.
    # Let's map anything else to Patios or Bodegas if possible, or filtered out in chart.

def get_location_color(loc_type):
    if loc_type == 'Patios': return COLORS['yellow']
    if loc_type == 'Bodegas': return COLORS['gray']
    return COLORS['yellow'] # Default to yellow if unsure to avoid "Blue/Otros"

def render_subzone_grouped_chart(df, insumo_label):
    fig = create_subzone_grouped_chart(df, insumo_label)
    st.plotly_chart(fig, use_container_width=True)

def create_subzone_grouped_chart(df, insumo_label):
    st.markdown(f"#### Distribución de {insumo_label} por Subzona")
    
    # Group by Zona AND Subzone to get correct location type from Zona
    df_viz = df.groupby(['zona', 'subzona'])['cantidad'].sum().reset_index().sort_values(['zona', 'subzona'])
    
    # Add Location Type for Coloring using ZONA
    df_viz['Ubicación'] = df_viz['zona'].apply(get_location_type)
    
    # Map colors
    color_map = {
        'Patios': COLORS['yellow'],
        'Bodegas': COLORS['gray'],
        'Bodegas': COLORS['gray'] # Duplicate key safety
    }
    
    fig = px.bar(
        df_viz, 
        x='subzona', 
        y='cantidad', 
        color='Ubicación',
        text='cantidad',
        title="",
        color_discrete_map=color_map,
        category_orders={"Ubicación": ["Patios", "Bodegas"]}
    )
    
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    
    layout = get_plotly_template()['layout'].copy()
    layout.pop('margin', None)
    layout.pop('xaxis', None) 
    layout.pop('yaxis', None)

    fig.update_layout(
        **layout,
        margin=dict(l=20,r=20,t=10,b=40),
        height=250,
        xaxis_title="", yaxis_title="Cantidad",
        legend_title_text="",
        xaxis={'tickangle': -45}
    )
    return fig

def render_espacios_chart(df):
    
    # 0. STRICT FILTER: Only Available > 0
    df = df[df['cantidad'] > 0]
    df = df[df['estado'].astype(str).str.contains("disponible", case=False, na=False)]
    
    if df.empty:
        st.info("No hay espacios disponibles.")
        return

    fig = create_espacios_chart(df)
    st.plotly_chart(fig, use_container_width=True)

def create_espacios_chart(df):
    breakdown_col = 'subtipo_insumo' if 'subtipo_insumo' in df.columns else 'insumo'
    
    # 1. Group Data (Strictly Subzona + Size)
    # Removing Zona from groupby to avoid fragmentation
    df_viz = df.groupby(['subzona', breakdown_col])['cantidad'].sum().reset_index()
    
    # 2. Sort
    df_viz = df_viz.sort_values(['subzona'])

    # 3. Create Chart
    # X=Subzona, Y=Qty, Color=Size
    fig = px.bar(
        df_viz, 
        x='subzona', 
        y='cantidad', 
        color=breakdown_col,
        text='cantidad',
        title="",
        labels={breakdown_col: "Tamaño (TM)"},
        height=300
    )
    
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='inside')
    
    # Update layout
    layout = get_plotly_template()['layout'].copy()
    layout.pop('margin', None)
    layout.pop('xaxis', None) 
    layout.pop('yaxis', None)

    fig.update_layout(
        **layout,
        margin=dict(l=20,r=20,t=20,b=40),
        xaxis_title="", yaxis_title="Cantidad",
        legend_title_text="Tamaño",
        xaxis={'tickangle': -45}
    )
    return fig
