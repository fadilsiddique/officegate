# Custom Document Naming Functions for ERPNext
# File: custom_naming.py
# Place this file in your custom app or frappe-bench/sites/[site]/custom_naming.py

import frappe
from datetime import datetime
from frappe.model.naming import make_autoname

def get_company_prefix(company):
    """Get company-specific prefix"""
    if company == "Capital One Office Furniture":
        return "COF"
    elif company == "Office Gate Furniture Trading LLC":
        return "OGF"
    else:
        return "GEN"  # Generic prefix for other companies

def get_year_suffix(format_type="YYY"):
    """Get current year in specified format"""
    current_year = datetime.now().year
    if format_type == "YYY":
        return str(current_year)[-3:]  # Last 3 digits (025 for 2025)
    elif format_type == "YY":
        return str(current_year)[-2:]  # Last 2 digits (25 for 2025)
    else:
        return str(current_year)  # Full year (2025)

def quotation_autoname(doc, method=None):
    """
    Custom naming for Quotation
    Capital One Office Furniture: COF-YYY-0001
    Office Gate Furniture Trading LLC: OGF-YYY-0001
    """
    try:
        year_suffix = get_year_suffix("YYY")
        
        if doc.company == "Capital One Office Furniture":
            naming_series = f"COF-{year_suffix}-"
        elif doc.company == "Office Gate Furniture Trading LLC":
            naming_series = f"OGF-{year_suffix}-"
        else:
            naming_series = f"GEN-{year_suffix}-"
        
        doc.name = make_autoname(naming_series + ".#####")
        
    except Exception as e:
        frappe.log_error(f"Error in quotation_autoname: {str(e)}")
        # Fallback to default naming
        doc.name = make_autoname("QTN-.YYYY.-.#####")

def purchase_order_autoname(doc, method=None):
    """
    Custom naming for Purchase Order
    Capital One Office Furniture: LPO-YYY-0001
    Office Gate Furniture Trading LLC: OGF-LPO-YYY-0001
    """
    try:
        year_suffix = get_year_suffix("YYY")
        
        if doc.company == "Capital One Office Furniture":
            naming_series = f"LPO-{year_suffix}-"
        elif doc.company == "Office Gate Furniture Trading LLC":
            naming_series = f"OGF-LPO-{year_suffix}-"
        else:
            naming_series = f"GEN-LPO-{year_suffix}-"
        
        doc.name = make_autoname(naming_series + ".#####")
        
    except Exception as e:
        frappe.log_error(f"Error in purchase_order_autoname: {str(e)}")
        # Fallback to default naming
        doc.name = make_autoname("PO-.YYYY.-.#####")

def purchase_invoice_autoname(doc, method=None):
    """
    Custom naming for Purchase Order
    Capital One Office Furniture: LPO-YYY-0001
    Office Gate Furniture Trading LLC: OGF-LPO-YYY-0001
    """
    try:
        year_suffix = get_year_suffix("YYY")
        
        if doc.company == "Capital One Office Furniture":
            naming_series = f"PI-{year_suffix}-"
        elif doc.company == "Office Gate Furniture Trading LLC":
            naming_series = f"OG-LPO-{year_suffix}-"
        else:
            naming_series = f"GEN-LPO-{year_suffix}-"
        
        doc.name = make_autoname(naming_series + ".#####")
        
    except Exception as e:
        frappe.log_error(f"Error in purchase_order_autoname: {str(e)}")
        # Fallback to default naming
        doc.name = make_autoname("PO-.YYYY.-.#####")

def sales_invoice_autoname(doc, method=None):
    """
    Custom naming for Sales Invoice
    Capital One Office Furniture: INV-COF-YY-0001
    Office Gate Furniture Trading LLC: INV-OGF-YY-0001
    """
    try:
        year_suffix = get_year_suffix("YY")
        
        if doc.company == "Capital One Office Furniture":
            naming_series = f"INV-COF-{year_suffix}-"
            doc.name = make_autoname(naming_series + ".#####")
        elif doc.company == "Office Gate Furniture Trading LLC":
            naming_series = f"OG-{year_suffix}-"
            doc.name = make_autoname(naming_series + ".####")
        else:
            naming_series = f"INV-GEN-{year_suffix}-"
            doc.name = make_autoname(naming_series + ".#####")
        
        
        
    except Exception as e:
        frappe.log_error(f"Error in sales_invoice_autoname: {str(e)}")
        # Fallback to default naming
        doc.name = make_autoname("INV-.YYYY.-.#####")

def sales_order_autoname(doc, method=None):
    """
    Custom naming for Sales Invoice
    Capital One Office Furniture: INV-COF-YY-0001
    Office Gate Furniture Trading LLC: INV-OGF-YY-0001
    """
    try:
        year_suffix = get_year_suffix("YY")
        
        if doc.company == "Capital One Office Furniture":
            naming_series = f"SO-COF-{year_suffix}-"
        elif doc.company == "Office Gate Furniture Trading LLC":
            naming_series = f"INV-OGF-{year_suffix}-"
        else:
            naming_series = f"INV-GEN-{year_suffix}-"
        
        doc.name = make_autoname(naming_series + ".#####")
        
    except Exception as e:
        frappe.log_error(f"Error in sales_invoice_autoname: {str(e)}")
        # Fallback to default naming
        doc.name = make_autoname("INV-.YYYY.-.#####")

def delivery_note_autoname(doc, method=None):
    """
    Custom naming for Delivery Note
    Capital One Office Furniture: DN-COF-25-0001
    Office Gate Furniture Trading LLC: DN-OGF-25-0001
    """
    try:
        year_suffix = get_year_suffix("YY")
        
        if doc.company == "Capital One Office Furniture":
            naming_series = f"DN-COF-{year_suffix}-"
            doc.name = make_autoname(naming_series + ".#####")
        elif doc.company == "Office Gate Furniture Trading LLC":
            naming_series = f"DN-OG-{year_suffix}-"
            doc.name = make_autoname(naming_series + ".####")
        else:
            naming_series = f"DN-GEN-{year_suffix}-"
            doc.name = make_autoname(naming_series + ".#####")
        
        
        
    except Exception as e:
        frappe.log_error(f"Error in delivery_note_autoname: {str(e)}")
        # Fallback to default naming
        doc.name = make_autoname("DN-.YYYY.-.#####")

def purchase_invoice_autoname(doc, method=None):
    """
    Custom naming for Purchase Invoice (if needed)
    Capital One Office Furniture: PINV-COF-YY-0001
    Office Gate Furniture Trading LLC: PINV-OGF-YY-0001
    """
    try:
        year_suffix = get_year_suffix("YY")
        
        if doc.company == "Capital One Office Furniture":
            naming_series = f"PINV-COF-{year_suffix}-"
        elif doc.company == "Office Gate Furniture Trading LLC":
            naming_series = f"PINV-OGF-{year_suffix}-"
        else:
            naming_series = f"PINV-GEN-{year_suffix}-"
        
        doc.name = make_autoname(naming_series + ".#####")
        
    except Exception as e:
        frappe.log_error(f"Error in purchase_invoice_autoname: {str(e)}")
        # Fallback to default naming
        doc.name = make_autoname("PINV-.YYYY.-.#####")

def sales_order_autoname(doc, method=None):
    """
    Custom naming for Sales Order (if needed)
    Capital One Office Furniture: SO-COF-YYY-0001
    Office Gate Furniture Trading LLC: SO-OGF-YYY-0001
    """
    try:
        year_suffix = get_year_suffix("YYY")
        
        if doc.company == "Capital One Office Furniture":
            naming_series = f"SO-COF-{year_suffix}-"
        elif doc.company == "Office Gate Furniture Trading LLC":
            naming_series = f"SO-OGF-{year_suffix}-"
        else:
            naming_series = f"SO-GEN-{year_suffix}-"
        
        doc.name = make_autoname(naming_series + ".#####")
        
    except Exception as e:
        frappe.log_error(f"Error in sales_order_autoname: {str(e)}")
        # Fallback to default naming
        doc.name = make_autoname("SO-.YYYY.-.#####")

# Alternative: Single function to handle all document types
def universal_autoname(doc, method=None):
    """
    Universal naming function that can handle all document types
    Call this function and it will automatically detect document type
    """
    try:
        doctype = doc.doctype
        
        if doctype == "Quotation":
            quotation_autoname(doc, method)
        elif doctype == "Purchase Order":
            purchase_order_autoname(doc, method)
        elif doctype == "Sales Invoice":
            sales_invoice_autoname(doc, method)
        elif doctype == "Delivery Note":
            delivery_note_autoname(doc, method)
        elif doctype == "Purchase Invoice":
            purchase_invoice_autoname(doc, method)
        elif doctype == "Sales Order":
            sales_order_autoname(doc, method)
        else:
            # For other document types, use default naming
            frappe.log_error(f"Universal autoname called for unsupported doctype: {doctype}")
            
    except Exception as e:
        frappe.log_error(f"Error in universal_autoname: {str(e)}")

