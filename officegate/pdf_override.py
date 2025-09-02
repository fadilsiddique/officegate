import frappe
from playwright.sync_api import sync_playwright
import atexit

_browser_instance = None
_playwright_instance = None

def get_browser():
    global _browser_instance, _playwright_instance
    if _browser_instance is None:
        _playwright_instance = sync_playwright().start()
        # Frappe Cloud: DO NOT set executable_path
        _browser_instance = _playwright_instance.chromium.launch(
            headless=True,
            args=["--no-sandbox"]  # still needed
        )
        atexit.register(close_browser)
    return _browser_instance

def close_browser():
    global _browser_instance, _playwright_instance
    if _browser_instance:
        _browser_instance.close()
        _browser_instance = None
    if _playwright_instance:
        _playwright_instance.stop()
        _playwright_instance = None

@frappe.whitelist()
def download_pdf(doctype, name, format=None, doc=None, no_letterhead=0):
    if not doc:
        doc = frappe.get_doc(doctype, name)

    html = frappe.get_print(
        doctype,
        name,
        print_format=format,
        doc=doc,
        no_letterhead=no_letterhead
    )

    base_url = frappe.utils.get_url()
    html = html.replace('src="/', f'src="{base_url}/')
    html = html.replace('href="/', f'href="{base_url}/')

    browser = get_browser()
    page = browser.new_page()
    page.set_content(html, wait_until="networkidle")
    pdf_bytes = page.pdf(format="A4", print_background=True)
    page.close()

    frappe.local.response.filename = f"{name}.pdf"
    frappe.local.response.filecontent = pdf_bytes
    frappe.local.response.type = "pdf"
