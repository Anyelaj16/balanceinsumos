"""
SIPOR Dashboard - PDF Report HTML Generator
Generates clean HTML for WeasyPrint conversion
"""

# CSS optimized for A4 landscape PDF
PDF_CSS = """
@page {
    size: A4 landscape;
    margin: 12mm;
}

body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    font-size: 11pt;
}

.page {
    width: 100%;
    display: grid;
    grid-template-rows: auto auto 1fr;
    gap: 12px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 8px;
    border-bottom: 2px solid #F5A800;
}

.header-left, .header-right {
    width: 120px;
}

.header-center {
    text-align: center;
    flex: 1;
}

.header-center h2 {
    margin: 0;
    color: #003366;
    font-size: 18pt;
}

.header-center .date {
    color: #666;
    font-size: 10pt;
}

.kpis {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

.kpi {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: center;
    border-radius: 4px;
    background: #f9f9f9;
}

.kpi-title {
    font-weight: bold;
    color: #003366;
    font-size: 10pt;
    margin-bottom: 6px;
}

.kpi-value {
    font-size: 9pt;
    color: #333;
    line-height: 1.4;
}

.charts {
    page-break-inside: avoid;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.chart {
    page-break-inside: avoid;
}

.chart img {
    width: 100%;
    height: auto;
    max-height: 280px;
}

img.logo {
    max-height: 45px;
    width: auto;
}
"""


def build_pdf_html(fecha, kpis, charts_html):
    """
    Generate complete HTML for PDF export
    
    Args:
        fecha: Date string (e.g., "01-02-2026")
        kpis: Dict with KPI data {title: values_dict, ...}
        charts_html: HTML string with embedded chart images
    
    Returns:
        Complete HTML string ready for WeasyPrint
    """
    
    # Build KPI HTML
    kpi_html = ""
    for title, values in kpis.items():
        values_text = "<br>".join([f"{k}: {v}" for k, v in values.items() if v > 0])
        if values_text:  # Only show KPIs with data
            kpi_html += f"""
            <div class="kpi">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{values_text}</div>
            </div>
            """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
        {PDF_CSS}
        </style>
    </head>
    <body>
        <div class="page">
            
            <!-- HEADER -->
            <div class="header">
                <div class="header-left">
                    <img src="assets/yara_logo.png" class="logo" alt="Yara">
                </div>
                <div class="header-center">
                    <h2>SIPOR – Balance Actual de Insumos</h2>
                    <div class="date">Corte: {fecha}</div>
                </div>
                <div class="header-right">
                    <img src="assets/sipor_logo.png" class="logo" alt="SIPOR">
                </div>
            </div>
            
            <!-- KPIs -->
            <div class="kpis">
                {kpi_html}
            </div>
            
            <!-- GRÁFICAS -->
            <div class="charts">
                {charts_html}
            </div>
            
        </div>
    </body>
    </html>
    """
