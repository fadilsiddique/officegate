# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "item_code",
            "label": _("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 200
        },
        {
            "fieldname": "actual_qty",
            "label": _("Actual Qty"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "ordered_qty",
            "label": _("Ordered Qty"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "reserved_qty",
            "label": _("Reserved Qty"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "voucher_type",
            "label": _("Voucher Type"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "voucher_no",
            "label": _("Voucher No"),
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 150
        },
        {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200
        },
        {
            "fieldname": "reserved_qty_detail",
            "label": _("Reserved Qty"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "unreserve",
            "label": _("Action"),
            "fieldtype": "Button",
            "width": 100
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    # Get item-wise stock summary
    stock_data = frappe.db.sql(f"""
        SELECT 
            bin.item_code,
            SUM(bin.actual_qty) as actual_qty,
            SUM(bin.ordered_qty) as ordered_qty,
            SUM(bin.reserved_qty) as reserved_qty
        FROM `tabBin` bin
        WHERE 1=1 {conditions['bin_conditions']}
        GROUP BY bin.item_code
        HAVING SUM(bin.reserved_qty) > 0 OR SUM(bin.ordered_qty) > 0
        ORDER BY bin.item_code
    """, filters, as_dict=1)
    
    data = []
    
    for item in stock_data:
        # Add parent row with item summary
        parent_row = {
            "item_code": f"<b>{item.item_code}</b>",
            "actual_qty": item.actual_qty,
            "ordered_qty": item.ordered_qty,
            "reserved_qty": item.reserved_qty,
            "voucher_type": "",
            "voucher_no": "",
            "customer": "",
            "reserved_qty_detail": "",
            "unreserve": "",
            "indent": 0
        }
        data.append(parent_row)
        
        # Get reservation details for Sales Orders
        so_details = get_sales_order_details(item.item_code, filters)
        for detail in so_details:
            child_row = {
                "item_code": "",
                "actual_qty": "",
                "ordered_qty": "",
                "reserved_qty": "",
                "voucher_type": "Sales Order",
                "voucher_no": f"<b>{detail.voucher_no}</b>",
                "customer": detail.customer,
                "reserved_qty_detail": detail.reserved_qty,
                "unreserve": "Unreserve",
                "indent": 1,
                "_item_code": item.item_code,
                "_voucher_no": detail.voucher_no,
                "_voucher_type": "Sales Order"
            }
            data.append(child_row)
        
        # Get ordered details for Purchase Orders
        po_details = get_purchase_order_details(item.item_code, filters)
        for detail in po_details:
            child_row = {
                "item_code": "",
                "actual_qty": "",
                "ordered_qty": "",
                "reserved_qty": "",
                "voucher_type": "Purchase Order",
                "voucher_no": f"<b>{detail.voucher_no}</b>",
                "customer": detail.supplier or "",
                "reserved_qty_detail": detail.ordered_qty,
                "unreserve": "",
                "indent": 1,
                "_item_code": item.item_code,
                "_voucher_no": detail.voucher_no,
                "_voucher_type": "Purchase Order"
            }
            data.append(child_row)
    
    return data

def get_conditions(filters):
    bin_conditions = ""
    so_conditions = ""
    po_conditions = ""
    
    if filters.get("item_code"):
        bin_conditions += " AND bin.item_code = %(item_code)s"
        so_conditions += " AND soi.item_code = %(item_code)s"
        po_conditions += " AND poi.item_code = %(item_code)s"
    
    if filters.get("customer"):
        so_conditions += " AND so.customer = %(customer)s"
    
    if filters.get("sales_order"):
        so_conditions += " AND so.name = %(sales_order)s"
    
    if filters.get("purchase_order"):
        po_conditions += " AND po.name = %(purchase_order)s"
    
    return {
        "bin_conditions": bin_conditions,
        "so_conditions": so_conditions,
        "po_conditions": po_conditions
    }

def get_sales_order_details(item_code, filters):
    conditions = get_conditions(filters)
    
    return frappe.db.sql(f"""
        SELECT 
            so.name as voucher_no,
            so.customer,
            soi.item_code,
            (soi.stock_qty - soi.delivered_qty) as reserved_qty
        FROM `tabSales Order` so
        INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
        WHERE so.docstatus = 1
            AND so.status NOT IN ('Closed', 'Completed')
            AND soi.item_code = %(item_code)s
            AND (soi.stock_qty - soi.delivered_qty) > 0
            {conditions['so_conditions']}
        ORDER BY so.transaction_date DESC
    """, {"item_code": item_code, **filters}, as_dict=1)

def get_purchase_order_details(item_code, filters):
    conditions = get_conditions(filters)
    
    return frappe.db.sql(f"""
        SELECT 
            po.name as voucher_no,
            po.supplier,
            poi.item_code,
            (poi.stock_qty - poi.received_qty) as ordered_qty
        FROM `tabPurchase Order` po
        INNER JOIN `tabPurchase Order Item` poi ON po.name = poi.parent
        WHERE po.docstatus = 1
            AND po.status NOT IN ('Closed', 'Completed')
            AND poi.item_code = %(item_code)s
            AND (poi.stock_qty - poi.received_qty) > 0
            {conditions['po_conditions']}
        ORDER BY po.transaction_date DESC
    """, {"item_code": item_code, **filters}, as_dict=1)

# Client-side script for handling unreserve button
@frappe.whitelist()
def unreserve_stock(item_code, voucher_type, voucher_no):
    """Unreserve stock from Sales Order using standard ERPNext function"""
    try:
        if voucher_type == "Sales Order":
            so = frappe.get_doc("Sales Order", voucher_no)
            
            # Find the item in sales order
            for item in so.items:
                if item.item_code == item_code and item.stock_reserved_qty > 0:
                    # Use standard ERPNext unreserve function
                    item.unreserve_stock()
            
            so.save()
            frappe.db.commit()
            
            return {"message": _("Stock unreserved successfully"), "status": "success"}
        else:
            return {"message": _("Unreserve is only applicable for Sales Orders"), "status": "error"}
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Unreserve Stock Error"))
        return {"message": str(e), "status": "error"}