import frappe
from pathlib import Path
from playwright.sync_api import sync_playwright


class ChromiumPDFGenerator:
    """
    Frappe Cloud compatible PDF generator using Playwright.
    Uses the pre-installed Chromium with channel="chromium".
    """

    def __init__(self):
        pass  # No manual Chromium setup needed

    def generate_pdf_from_url(self, url: str, output_path: str = None) -> bytes:
        """
        Generate PDF from a URL.

        :param url: Full URL to the page to print
        :param output_path: Optional path to save the PDF
        :return: PDF bytes if output_path is None
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, channel="chromium")
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            
            if output_path:
                page.pdf(path=output_path)
                result = None
            else:
                result = page.pdf()
            
            browser.close()
            return result
