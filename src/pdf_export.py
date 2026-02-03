"""
SIPOR Dashboard - PDF Export Module
Converts HTML to PDF using WeasyPrint
"""

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


def html_to_pdf(html_string):
    """
    Convert HTML string to PDF bytes using WeasyPrint
    
    Args:
        html_string: Complete HTML document as string
        
    Returns:
        PDF as bytes
        
    Raises:
        ImportError: If weasyprint is not installed
    """
    if not WEASYPRINT_AVAILABLE:
        raise ImportError(
            "WeasyPrint no está instalado. "
            "Instálalo con: pip install weasyprint"
        )
    
    # Convert HTML to PDF
    # base_url="." allows relative paths for images
    pdf_bytes = HTML(string=html_string, base_url=".").write_pdf()
    
    return pdf_bytes
