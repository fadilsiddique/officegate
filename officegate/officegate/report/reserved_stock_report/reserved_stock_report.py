import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    """Define columns for the report"""
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
            "fieldname": "document_type",
            "label": _("Document Type"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "document_name",
            "label": _("Document"),
            "fieldtype": "Dynamic Link",
            "options": "document_type",
            "width": 150
        },
        {
            "fieldname": "party_type",
            "label": _("Party Type"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "party",
            "label": _("Party"),
            "fieldtype": "Dynamic Link",
            "options": "party_type",
            "width": 150
        },
        {
            "fieldname": "reservation_qty",
            "label": _("Reservation Qty"),
            "fieldtype": "Float",
            "width": 130
        },
        {
            "fieldname": "stock_reservation_entry",
            "label": _("Stock Reservation Entry"),
            "fieldtype": "Link",
            "options": "Stock Reservation Entry",
            "width": 180
        },
        {
            "fieldname": "unreserve",
            "label": _(""),
            "fieldtype": "Button",
            "width": 100
        }
    ]

def get_data(filters):
    """Fetch and structure data for the report"""
    conditions = get_conditions(filters)
    
    # Get all items with stock (even without reservations)
    all_items = get_all_items_stock(conditions, filters)
    
    # Get reservation details
    reservations = get_reservation_details(conditions, filters)
    
    # Structure data in parent-child format
    data = []
    
    for item in all_items:
        # Parent row - Item summary
        parent_row = {
            "item_code": item.item_code,
            "actual_qty": item.actual_qty,
            "ordered_qty": item.ordered_qty,
            "reserved_qty": item.reserved_qty,
            "indent": 0,
            "bold": 1
        }
        data.append(parent_row)
        
        # Child rows - Reservation details
        item_reservations = [r for r in reservations if r.item_code == item.item_code]
        
        for res in item_reservations:
            child_row = {
                "item_code": "",
                "document_type": res.voucher_type,
                "document_name": res.voucher_no,
                "party_type": "Customer" if res.voucher_type == "Sales Order" else "Supplier" if res.voucher_type == "Purchase Order" else "",
                "party": res.party,
                "reservation_qty": res.reserved_qty,
                "stock_reservation_entry": res.name if res.voucher_type == "Sales Order" else "",
                "unreserve": "Unreserve" if res.voucher_type == "Sales Order" else "",
                "indent": 1
            }
            data.append(child_row)
    
    return data

def get_conditions(filters):
    """Build query conditions based on filters"""
    conditions = []
    
    if filters.get("item_code"):
        conditions.append("sre.item_code = %(item_code)s")
    
    if filters.get("customer"):
        conditions.append("""
            EXISTS (
                SELECT 1 FROM `tabSales Order` so 
                WHERE so.name = sre.voucher_no 
                AND so.customer = %(customer)s
            )
        """)
    
    if filters.get("sales_order"):
        conditions.append("sre.voucher_no = %(sales_order)s")
        conditions.append("sre.voucher_type = 'Sales Order'")
    
    if filters.get("purchase_order"):
        conditions.append("sre.voucher_no = %(purchase_order)s")
        conditions.append("sre.voucher_type = 'Purchase Order'")
    
    return " AND " + " AND ".join(conditions) if conditions else ""

def get_all_items_stock(conditions, filters):
    """Get all items with stock data, including those without reservations"""
    # Build item filter if specified
    item_filter = ""
    if filters and filters.get("item_code"):
        item_filter = "AND bin.item_code = %(item_code)s"
    
    query = f"""
        SELECT 
            bin.item_code,
            COALESCE(SUM(bin.actual_qty), 0) as actual_qty,
            COALESCE(SUM(bin.ordered_qty), 0) as ordered_qty,
            COALESCE(
                (SELECT SUM(sre.reserved_qty) 
                 FROM `tabStock Reservation Entry` sre 
                 WHERE sre.item_code = bin.item_code 
                 AND sre.docstatus = 1 
                 AND sre.status != 'Cancelled'), 0
            ) as reserved_qty
        FROM `tabBin` bin
        WHERE bin.actual_qty > 0 OR bin.ordered_qty > 0
        {item_filter}
        GROUP BY bin.item_code
        ORDER BY bin.item_code
    """
    
    items = frappe.db.sql(query, filters or {}, as_dict=1)
    
    # If filters are applied for sales order, purchase order, or customer
    # we need to filter items that have matching reservations
    if filters and (filters.get("sales_order") or filters.get("purchase_order") or filters.get("customer")):
        reservation_items = get_filtered_reservation_items(conditions, filters)
        reservation_item_codes = [r.item_code for r in reservation_items]
        items = [item for item in items if item.item_code in reservation_item_codes]
    
    return items

def get_filtered_reservation_items(conditions, filters):
    """Get items that have reservations matching the filters"""
    query = f"""
        SELECT DISTINCT sre.item_code
        FROM `tabStock Reservation Entry` sre
        LEFT JOIN `tabSales Order` so ON so.name = sre.voucher_no AND sre.voucher_type = 'Sales Order'
        LEFT JOIN `tabPurchase Order` po ON po.name = sre.voucher_no AND sre.voucher_type = 'Purchase Order'
        WHERE sre.docstatus = 1
        AND sre.status != 'Cancelled'
        {conditions}
    """
    return frappe.db.sql(query, filters or {}, as_dict=1)

def get_reservation_details(conditions, filters):
    """Get detailed reservation entries with party information"""
    query = f"""
        SELECT 
            sre.name,
            sre.item_code,
            sre.voucher_type,
            sre.voucher_no,
            sre.reserved_qty,
            CASE 
                WHEN sre.voucher_type = 'Sales Order' THEN so.customer
                WHEN sre.voucher_type = 'Purchase Order' THEN po.supplier
                ELSE NULL
            END as party
        FROM `tabStock Reservation Entry` sre
        LEFT JOIN `tabSales Order` so ON so.name = sre.voucher_no AND sre.voucher_type = 'Sales Order'
        LEFT JOIN `tabPurchase Order` po ON po.name = sre.voucher_no AND sre.voucher_type = 'Purchase Order'
        WHERE sre.docstatus = 1
        AND sre.status != 'Cancelled'
        {conditions}
        ORDER BY sre.item_code, sre.voucher_no
    """
    
    return frappe.db.sql(query, filters or {}, as_dict=1)