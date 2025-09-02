# import frappe
# from urllib.parse import urljoin
# from playwright.sync_api import sync_playwright


# @frappe.whitelist()
# def download_pdf(doctype, name, format=None, doc=None, no_letterhead=0):
#     if not doc:
#         doc = frappe.get_doc(doctype, name)

#     # Generate HTML
#     html = frappe.get_print(
#         doctype,
#         name,
#         print_format=format,
#         doc=doc,
#         no_letterhead=no_letterhead
#     )

#     # Get site URL from Frappe
#     base_url = frappe.utils.get_url()

#     # Replace relative src/href with absolute URLs
#     html = html.replace('src="/', f'src="{base_url}/')
#     html = html.replace('href="/', f'href="{base_url}/')

#     # Convert HTML → PDF with Playwright
#     with sync_playwright() as p:
#         browser = p.chromium.launch()
#         page = browser.new_page()
#         page.set_content(html, wait_until="networkidle")
#         pdf_bytes = page.pdf(format="A4", print_background=True)
#         browser.close()

#     # Return PDF response
#     frappe.local.response.filename = f"{name}.pdf"
#     frappe.local.response.filecontent = pdf_bytes
#     frappe.local.response.type = "pdf"

import os
import frappe
from frappe.utils import get_url
from playwright.sync_api import sync_playwright

@frappe.whitelist()
def download_pdf(doctype, name, print_format=None, doc=None, no_letterhead=0):
    """
    Generate PDF of a Frappe document using Playwright (Chromium).

    Args:
        doctype (str): DocType name
        name (str): Name of the document
        print_format (str, optional): Print Format to use
        doc (frappe.model.document.Document, optional): Frappe doc object
        no_letterhead (int, optional): 0/1, skip letterhead

    Returns:
        Sets frappe.local.response with PDF content for download.
    """

    # Fetch the document if not provided
    if not doc:
        doc = frappe.get_doc(doctype, name)

    # Render HTML from print format
    html = frappe.get_print(
        doctype=doctype,
        name=name,
        print_format=print_format,
        doc=doc,
        no_letterhead=no_letterhead
    )

    # Convert relative URLs to absolute URLs
    base_url = get_url()
    html = html.replace('src="/', f'src="{base_url}/')
    html = html.replace('href="/', f'href="{base_url}/')

    # Launch Chromium via Playwright
    with sync_playwright() as p:
        browser_launch_args = {}
        
        # Optional: Use custom executable path (if Frappe Cloud has it in env)
        chromium_path = os.environ.get("CHROMIUM_PATH")
        if chromium_path:
            browser_launch_args["executable_path"] = chromium_path

        browser = p.chromium.launch(headless=True, **browser_launch_args)
        page = browser.new_page()

        # If session is active, add sid for internal pages
        if frappe.session and frappe.session.sid:
            page.set_extra_http_headers({"Cookie": f"sid={frappe.session.sid}"})

        page.set_content(html, wait_until="networkidle")
        
        # PDF options
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
        )

        browser.close()

    # Return PDF response to browser
    frappe.local.response.filename = f"{name}.pdf"
    frappe.local.response.filecontent = pdf_bytes
    frappe.local.response.type = "pdf"

