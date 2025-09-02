import os
import platform
import subprocess
import tempfile
from pathlib import Path

import frappe
from frappe.utils import get_url


class ChromiumPDFGenerator:
    """
    Minimal headless Chromium PDF generator.
    Works with Frappe Cloud bundled Chromium (if present).
    """

    EXECUTABLE_PATHS = {
        "linux": ["chromium", "headless_shell"],
        "darwin": ["chrome-mac", "headless_shell"],
        "windows": ["chrome-win", "headless_shell.exe"],
    }

    def __init__(self):
        self.chromium_path = self._find_chromium()

    def _find_chromium(self):
        bench_path = frappe.utils.get_bench_path()
        chromium_dir = os.path.join(bench_path, "chromium")
        platform_name = platform.system().lower()

        if platform_name not in self.EXECUTABLE_PATHS:
            frappe.throw(f"Unsupported platform: {platform_name}")

        exec_path = Path(chromium_dir).joinpath(*self.EXECUTABLE_PATHS[platform_name])
        if not exec_path.exists():
            frappe.throw(
                f"Chromium executable not found at {exec_path}. Cannot generate PDF."
            )
        return str(exec_path)

    def generate_pdf(self, html: str) -> bytes:
        # ensure absolute URLs
        html = html.replace('src="/', f'src="{get_url()}/')
        html = html.replace('href="/', f'href="{get_url()}/')

        # temporary HTML file
        with tempfile.NamedTemporaryFile("w+", suffix=".html", delete=False) as html_file:
            html_file.write(html)
            html_path = html_file.name

        # output PDF path
        pdf_path = f"/tmp/{frappe.generate_hash()}.pdf"

        # Chromium command
        command = [
            self.chromium_path,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            f"--print-to-pdf={pdf_path}",
            html_path,
        ]
        subprocess.run(command, check=True)

        # read PDF
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        # cleanup
        os.remove(html_path)
        os.remove(pdf_path)

        return pdf_data
