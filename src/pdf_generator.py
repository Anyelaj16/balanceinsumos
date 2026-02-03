import tempfile
import os
from fpdf import FPDF
from datetime import datetime
import plotly.io as pio

# Constants for layout
PAGE_WIDTH = 210
PAGE_HEIGHT = 297
MARGIN = 10

class PDFReport(FPDF):
    def __init__(self, date_str):
        super().__init__()
        self.date_str = date_str
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self):
        # Logo Yara (Left)
        # Assuming asset path relative to execution
        logo_path = "assets/yara_logo.png"
        if os.path.exists(logo_path):
            self.image(logo_path, x=MARGIN, y=8, w=15) # Small logo
        
        # Header Text
        self.set_font("Arial", "", 12)
        self.set_xy(30, 8)
        self.cell(0, 10, "Yara - Planta Sur - CTG", ln=0)
        
        # Date (Right aligned)
        self.set_font("Arial", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Corte: {self.date_str}", ln=1, align='R')
        
        # Line
        self.set_draw_color(200, 200, 200)
        self.line(MARGIN, 25, PAGE_WIDTH - MARGIN, 25)
        
        # Main Title (Center)
        self.set_y(30)
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 51, 102) # Blueish
        self.cell(0, 10, "BALANCE ACTUAL DE INSUMOS", ln=1, align='C')
        self.ln(5)

    def check_page_break(self, h):
        if self.get_y() + h > PAGE_HEIGHT - MARGIN:
            self.add_page()

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

    def chapter_kpis(self, estibas_data, carpas_data, plasticos_data, espacios_data):
        self.set_font("Arial", "B", 12)
        self.set_text_color(0)
        # self.cell(0, 10, "Resumen Ejecutivo", ln=1)
        
        # Grid layout: 4 Columns
        col_w = (PAGE_WIDTH - 2 * MARGIN) / 4
        h = 25
        
        y_start = self.get_y()
        
        # Helper to draw box
        def draw_kpi_box(x, title, metrics):
            self.set_xy(x, y_start)
            self.set_font("Arial", "B", 10)
            self.cell(col_w, 6, title, ln=2, align='L')
            self.set_font("Arial", "", 9)
            for label, value in metrics:
                self.cell(col_w, 5, f"{label}: {value}", ln=2)
                
        # Estibas
        metrics = []
        if estibas_data['disponible'] > 0: metrics.append(("Disp", int(estibas_data['disponible'])))
        if estibas_data['reparar'] > 0: metrics.append(("Rep", int(estibas_data['reparar'])))
        if estibas_data['clasificar'] > 0: metrics.append(("Clasif", int(estibas_data['clasificar'])))
        draw_kpi_box(MARGIN, "ESTIBAS", metrics)

        # Carpas
        metrics = []
        if carpas_data['disponible'] > 0: metrics.append(("Disp", int(carpas_data['disponible'])))
        if carpas_data['reparar'] > 0: metrics.append(("Rep", int(carpas_data['reparar'])))
        if carpas_data['clasificar'] > 0: metrics.append(("Clasif", int(carpas_data['clasificar'])))
        draw_kpi_box(MARGIN + col_w, "CARPAS", metrics)
        
        # Plasticos
        metrics = []
        if plasticos_data['disponible'] > 0: metrics.append(("Disp", int(plasticos_data['disponible'])))
        if plasticos_data['reparar'] > 0: metrics.append(("Rep", int(plasticos_data['reparar'])))
        draw_kpi_box(MARGIN + 2*col_w, "PLÁSTICOS", metrics)
        
        # Espacios
        metrics = []
        if espacios_data['total'] > 0:
            metrics.append(("Total", int(espacios_data['total'])))
            # Top 2 sizes to fit
            for k, v in list(espacios_data['sizes'].items())[:2]:
                metrics.append((k, int(v)))
        else:
            metrics.append(("Total", 0))
            
        draw_kpi_box(MARGIN + 3*col_w, "ESPACIOS", metrics)
        
        self.set_y(y_start + h + 5)
        self.line(MARGIN, self.get_y(), PAGE_WIDTH - MARGIN, self.get_y())
        self.ln(5)

    def chapter_chart(self, fig, title):
        if fig is None: return
        
        self.set_font("Arial", "B", 11)
        self.cell(0, 8, title, ln=1)
        
        # Save fig to temp image
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                # Convert Plotly fig to image (requires kaleido)
                # scale=2 for better resolution
                img_bytes = fig.to_image(format="png", width=800, height=350, scale=2)
                tmp.write(img_bytes)
                tmp_path = tmp.name
            
            # Embed in PDF
            # Width = full page width margins
            self.image(tmp_path, x=MARGIN, w=PAGE_WIDTH - 2*MARGIN)
            self.ln(5)
            
            # Clean up
            os.unlink(tmp_path)
            
        except Exception as e:
            self.set_font("Arial", "I", 10)
            self.cell(0, 10, f"Error generando gráfica: {str(e)}", ln=1)


def generate_pdf_report(date_str, kpi_data, figs):
    pdf = PDFReport(date_str)
    
    # KPIs
    pdf.chapter_kpis(
        kpi_data['estibas'],
        kpi_data['carpas'],
        kpi_data['plasticos'],
        kpi_data['espacios']
    )
    
    # Charts
    if figs['estibas']:
        pdf.chapter_chart(figs['estibas'], "Distribución de Estibas por Subzona")
        
    if figs['carpas']:
        pdf.chapter_chart(figs['carpas'], "Distribución de Carpas por Subzona")
        
    if figs['plasticos']:
        pdf.chapter_chart(figs['plasticos'], "Distribución de Plásticos por Subzona")
        
    if figs['espacios']:
        pdf.check_page_break(60) # Ensure space
        pdf.chapter_chart(figs['espacios'], "Disponibilidad de Espacios")

    return pdf.output(dest='S') # Return as byte string
