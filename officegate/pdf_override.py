# 

import frappe
from officegate.pdf_generator import ChromiumPDFGenerator

@frappe.whitelist()
def download_pdf(doctype, name, print_format=None):
    """
    Generate PDF for a document using headless Chromium.
    """
    html = frappe.get_print(doctype, name, print_format=print_format)
    generator = ChromiumPDFGenerator()
    pdf_data = generator.generate_pdf(html)
    
    frappe.response.filename = f"{doctype}-{name}.pdf"
    frappe.response.filecontent = pdf_data
    frappe.response.type = "download"
