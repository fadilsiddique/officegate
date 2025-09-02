import frappe
from officegate.pdf_generator import ChromiumPDFGenerator


@frappe.whitelist()
def download_pdf(docname: str):
    """
    Example endpoint to generate PDF for a DocType using Playwright.
    """
    doc = frappe.get_doc("Your DocType", docname)
    
    # URL to render in PDF (can be your Frappe public route)
    url = frappe.utils.get_url(f"/printview?doctype={doc.doctype}&name={doc.name}&format=Standard&no_letterhead=1")
    
    generator = ChromiumPDFGenerator()
    pdf_bytes = generator.generate_pdf_from_url(url)
    
    # Attach PDF to the document in Frappe
    frappe.get_doc({
        "doctype": "File",
        "file_name": f"{docname}.pdf",
        "attached_to_doctype": doc.doctype,
        "attached_to_name": doc.name,
        "content": pdf_bytes,
        "is_private": 1
    }).insert()
    
    return {"message": "PDF generated and attached successfully"}
