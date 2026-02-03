"""
SIPOR Dashboard - Styles and Color Palette
Provides consistent styling across the application
"""

import streamlit as st

# SIPOR Corporate Color Palette
# Extracted from Logo:
# Yellow/Gold: #D4AF37 -> Adjusted to #F5A800 for web vibrancy matching previous, but slightly deeper for premium feel
# Dark Grey/Black: #2C3E50
# Blue (Colombian flag): #003A8F
# Red (Colombian flag): #E74C3C

COLORS = {
    'yellow': '#F5A800',  # Primary Brand Color
    'blue': '#003366',    # Deep professional blue
    'dark': '#2B2B2B',    # Text/Header dark
    'light': '#F8F9FA',   # Background light
    'white': '#FFFFFF',
    
    # Semantic Colors
    'success': '#27AE60', # Green
    'warning': '#F39C12', # Orange
    'danger': '#C0392B',  # Deep Red
    'info': '#2980B9',    # Info Blue
    
    # Specific Supply Colors (Visual separation)
    'estibas': '#8D6E63', # Wood-like brown
    'carpas': '#2980B9',  # Tarp blue
    'plasticos': '#27AE60',  # Green for Plastics
    'espacios': '#95A5A6', # Concrete gray
    
    'gray': '#7F8C8D',
    'yellow_light': '#FFF3CD',
    'blue_light': '#D6EAF8',
}

# Gradient Scales for stacked bars
PATIO_WARM = ['#F5A800', '#F39C12', '#E67E22', '#D35400'] # Yellows to Oranges
BODEGA_COLD = ['#5D6D7E', '#34495E', '#2E4053', '#1B2631'] # Cool Greys/Blues


def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown(f"""
    <style>
        /* Main app styling */
        .main {{
            background-color: {COLORS['light']};
        }}
        
        /* Header styling */
        h1 {{
            color: {COLORS['dark']};
            font-weight: 700;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid {COLORS['yellow']};
            margin-bottom: 1.5rem;
        }}
        
        h2 {{
            color: {COLORS['blue']};
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
        
        h3 {{
            color: {COLORS['dark']};
            font-weight: 500;
            font-size: 1.2rem;
            margin-top: 1rem;
        }}
        
        /* Card styling */
        .card {{
            background-color: {COLORS['white']};
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }}
        
        /* Metric styling */
        [data-testid="stMetricValue"] {{
            color: {COLORS['blue']};
            font-weight: 700;
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {COLORS['gray']};
            font-weight: 500;
            font-size: 0.9rem;
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid #E0E0E0;
        }}
        
        /* Print-specific styles for PDF export */
        @media print {{
            /* Hide Streamlit elements */
            [data-testid="stSidebar"],
            [data-testid="stStatusWidget"],
            header,
            footer,
            .stDeployButton {{
                display: none !important;
            }}
            
            /* Page setup */
            @page {{
                size: A4 portrait;
                margin: 1.5cm;
            }}
            
            body {{
                margin: 0;
                padding: 0;
            }}
            
            /* Prevent page breaks inside elements */
            .element-container,
            .stPlotlyChart,
            [data-testid="stMetric"] {{
                page-break-inside: avoid;
            }}
            
            /* Optimize chart sizes for print */
            .stPlotlyChart {{
                max-height: 250px !important;
            }}
            
            /* Ensure KPIs stay together */
            [data-testid="column"] {{
                page-break-inside: avoid;
            }}
        }}
        
        [data-testid="stSidebar"] * {{
            color: {COLORS['dark']} !important;
        }}
        
        /* Button styling */
        .stButton > button {{
            background-color: {COLORS['yellow']};
            color: {COLORS['dark']};
            font-weight: 600;
            border-radius: 4px;
            border: none;
        }}
        
        .stButton > button:hover {{
            background-color: #FFC107;
            color: {COLORS['dark']};
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px;
        }}

        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            background-color: {COLORS['white']};
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            color: {COLORS['gray']};
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {COLORS['white']};
            color: {COLORS['blue']};
            border-bottom: 2px solid {COLORS['blue']};
        }}

    </style>
    """, unsafe_allow_html=True)


def create_metric_card(label, value, delta=None, help_text=None):
    """
    Create a styled metric card using standard Streamlit metric
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)


def get_plotly_template():
    """
    Get custom Plotly template with SIPOR branding
    """
    return {
        'layout': {
            'font': {'family': 'Arial, sans-serif', 'color': COLORS['dark']},
            'plot_bgcolor': COLORS['white'],
            'paper_bgcolor': COLORS['white'],
            'title': {
                'font': {'size': 16, 'color': COLORS['blue'], 'family': 'Arial, sans-serif'},
                'x': 0,
                'xanchor': 'left'
            },
            'xaxis': {
                'gridcolor': '#E0E0E0',
                'linecolor': '#E0E0E0',
                'title': {'font': {'size': 12, 'color': COLORS['gray']}}
            },
            'yaxis': {
                'gridcolor': '#E0E0E0',
                'linecolor': '#E0E0E0',
                'title': {'font': {'size': 12, 'color': COLORS['gray']}}
            },
            'legend': {
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': 1.02,
                'xanchor': 'right',
                'x': 1
            },
            'margin': {'l': 40, 'r': 40, 't': 60, 'b': 40},
        }
    }


def show_header(title, subtitle=None):
    """
    Display a styled header with optional subtitle
    """
    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='color: {COLORS['gray']}; font-size: 1.1rem; margin-top: -1rem; margin-bottom: 2rem;'>{subtitle}</p>", 
                   unsafe_allow_html=True)


def add_logo_header():
    """Add SIPOR branding to the sidebar (Minimized)"""
    col1, col2, col3 = st.sidebar.columns([1,1,1]) # Centered but smaller column ratio
    with col2:
        try:
             # Use standard st.image with reduced width context
             # Reducing column width effectively makes it smaller
             st.image("assets/sipor_logo.png", width=None, use_column_width=True) 
        except:
             st.markdown(f"<h3 style='color:{COLORS['yellow']}; text-align:center;'>SIPOR</h3>", unsafe_allow_html=True)
