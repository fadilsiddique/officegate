import frappe
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright


@frappe.whitelist()
def download_pdf(doctype, name, format=None, doc=None, no_letterhead=0):
    if not doc:
        doc = frappe.get_doc(doctype, name)

    # Generate HTML
    html = frappe.get_print(
        doctype,
        name,
        print_format=format,
        doc=doc,
        no_letterhead=no_letterhead
    )

    # Get site URL from Frappe
    base_url = frappe.utils.get_url()

    # Replace relative src/href with absolute URLs
    html = html.replace('src="/', f'src="{base_url}/')
    html = html.replace('href="/', f'href="{base_url}/')

    # Convert HTML → PDF with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        pdf_bytes = page.pdf(format="A4", print_background=True)
        browser.close()

    # Return PDF response
    frappe.local.response.filename = f"{name}.pdf"
    frappe.local.response.filecontent = pdf_bytes
    frappe.local.response.type = "pdf"
