import frappe
from frappe import _
from frappe.utils import flt, nowdate
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def create_delivery_note_from_invoice(invoice_name, target_doc=None):
    # Prevent duplicate Delivery Note creation
    existing = frappe.get_all(
        "Delivery Note Item",
        filters={"against_sales_invoice": invoice_name},
        fields=["parent"]
    )
    if existing:
        return existing[0].parent

    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("set_po_nos")
        target.run_method("calculate_taxes_and_totals")

    def update_item(source_doc, target_doc, source_parent):
        target_doc.qty = flt(source_doc.qty) - flt(source_doc.delivered_qty)
        target_doc.stock_qty = target_doc.qty * flt(source_doc.conversion_factor)
        target_doc.base_amount = target_doc.qty * flt(source_doc.base_rate)
        target_doc.amount = target_doc.qty * flt(source_doc.rate)

    doc = get_mapped_doc(
        "Sales Invoice",
        invoice_name,
        {
            "Sales Invoice": {
                "doctype": "Delivery Note",
                # Disabled validation to allow draft Sales Invoice
                # "validation": {"docstatus": ["=", 1]},
            },
            "Sales Invoice Item": {
                "doctype": "Delivery Note Item",
                "field_map": {
                    "name": "si_detail",
                    "parent": "against_sales_invoice",
                    "serial_no": "serial_no",
                    "sales_order": "against_sales_order",
                    "so_detail": "so_detail",
                    "cost_center": "cost_center",
                },
                "postprocess": update_item,
                "condition": lambda doc: doc.delivered_by_supplier != 1,
            },
            "Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "reset_value": True},
            "Sales Team": {
                "doctype": "Sales Team",
                "field_map": {"incentives": "incentives"},
                "add_if_empty": True,
            },
        },
        target_doc,
        set_missing_values,
    )

    doc.insert()
    frappe.db.commit()

    # Optional: update SI with DN reference (requires custom fields)
    try:
        si = frappe.get_doc("Sales Invoice", invoice_name)
        si.db_set("delivery_note_created", 1)
        si.db_set("linked_delivery_note", doc.name)  # Make sure this field exists in SI
    except Exception as e:
        frappe.log_error(f"Failed to update Sales Invoice: {e}")

    return doc.name


def validate_no_duplicate_against_invoice(doc, method):
    checked_invoices = set()
    for item in doc.items:
        if item.against_sales_invoice:
            if not item.si_detail:
                continue

            # Check if another DN item exists with the same Sales Invoice and si_detail
            existing = frappe.db.exists(
                "Delivery Note Item",
                {
                    "against_sales_invoice": item.against_sales_invoice,
                    "si_detail": item.si_detail,
                    "parent": ["!=", doc.name]
                }
            )
            if existing:
                if item.against_sales_invoice not in checked_invoices:
                    checked_invoices.add(item.against_sales_invoice)
                    frappe.throw(
                        _("A Delivery Note already exists for this Sales Invoice: {0}").format(item.against_sales_invoice)
                    )

