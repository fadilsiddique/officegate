# reserved_stock_report.py - Complete Working Version
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Actual Quantity"),
            "fieldname": "actual_qty",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("In Transit Quantity"),
            "fieldname": "in_transit_qty",
            "fieldtype": "Float",
            "width": 140
        },
        {
            "label": _("Purchase Order Qty"),
            "fieldname": "po_qty",
            "fieldtype": "Float",
            "width": 130
        },
        {
            "label": _("Available Quantity"),
            "fieldname": "available_qty",
            "fieldtype": "Float",
            "width": 130
        },
        {
            "label": _("Reserved Quantity"),
            "fieldname": "reserved_qty",
            "fieldtype": "Float",
            "width": 130
        },
        {
            "label": _("Quantity After Reservation"),
            "fieldname": "qty_after_reservation",
            "fieldtype": "Float",
            "width": 170
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
            "label": _("Sales Order"),
            "fieldname": "sales_order",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 150
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120
        },
        {
            "label": _("Actions"),
            "fieldname": "actions",
            "fieldtype": "Data",
            "width": 100
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    # Get items with stock or reservations
    items_query = """
        SELECT DISTINCT
            i.item_code,
            i.item_name,
            i.item_group,
            COALESCE(bin.actual_qty, 0) as actual_qty,
            COALESCE(bin.warehouse, 'All Warehouses') as warehouse
        FROM 
            `tabItem` i
        LEFT JOIN 
            `tabBin` bin ON i.item_code = bin.item_code
        WHERE 
            i.disabled = 0
            AND (bin.actual_qty > 0 OR bin.actual_qty IS NULL)
            {conditions}
        
        UNION
        
        SELECT DISTINCT
            i.item_code,
            i.item_name,
            i.item_group,
            COALESCE(bin.actual_qty, 0) as actual_qty,
            COALESCE(sre.warehouse, 'All Warehouses') as warehouse
        FROM 
            `tabItem` i
        INNER JOIN 
            `tabStock Reservation Entry` sre ON i.item_code = sre.item_code
        LEFT JOIN 
            `tabBin` bin ON (i.item_code = bin.item_code AND sre.warehouse = bin.warehouse)
        WHERE 
            i.disabled = 0
            AND sre.docstatus = 1
            {conditions}
        ORDER BY 
            item_code, warehouse
    """.format(conditions=conditions)
    
    items = frappe.db.sql(items_query, filters, as_dict=1)
    
    data = []
    processed_items = set()
    
    for item in items:
        item_warehouse_key = f"{item.item_code}_{item.warehouse}"
        
        if item_warehouse_key in processed_items:
            continue
            
        # Get reservation details
        reservations = get_item_reservations(item.item_code, item.warehouse, filters)
        
        # Get purchase order quantity
        po_qty = get_purchase_order_qty(item.item_code, item.warehouse)
        
        # Get in-transit quantity (material transfers)
        in_transit_qty = get_material_transfer_qty(item.item_code, item.warehouse)
        
        # Calculate totals
        total_reserved = sum([flt(r.reserved_qty) for r in reservations])
        available_qty = flt(item.actual_qty) + flt(in_transit_qty) + flt(po_qty)
        qty_after_reservation = available_qty - total_reserved
        
        # Show items with stock, PO, in-transit, or reservations
        if available_qty > 0 or total_reserved > 0:
            main_row = {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "actual_qty": flt(item.actual_qty),
                "in_transit_qty": flt(in_transit_qty),
                "po_qty": flt(po_qty),
                "available_qty": available_qty,
                "reserved_qty": total_reserved,
                "qty_after_reservation": qty_after_reservation,
                "warehouse": item.warehouse if item.warehouse != 'All Warehouses' else '',
                "customer": "",
                "sales_order": "",
                "actions": "",
                "indent": 0,
                "is_group": 1 if reservations else 0
            }
            data.append(main_row)
            processed_items.add(item_warehouse_key)
            
            # Add reservation detail rows
            for reservation in reservations:
                detail_row = {
                    "item_code": "",
                    "item_name": "",
                    "actual_qty": "",
                    "in_transit_qty": "",
                    "po_qty": "",
                    "available_qty": "",
                    "reserved_qty": flt(reservation.reserved_qty),
                    "qty_after_reservation": "",
                    "customer": reservation.customer,
                    "sales_order": reservation.sales_order,
                    "warehouse": "",
                    "actions": f"""<button class='btn btn-xs btn-danger' 
                                  onclick='unreserve_stock("{reservation.name}")'>
                                  Unreserve</button>""",
                    "indent": 1,
                    "is_group": 0
                }
                data.append(detail_row)
    
    return data

def get_item_reservations(item_code, warehouse, filters):
    """Get all reservations for a specific item and warehouse"""
    conditions = ""
    filter_values = {"item_code": item_code}
    
    if warehouse and warehouse != 'All Warehouses':
        conditions += " AND sre.warehouse = %(warehouse)s"
        filter_values["warehouse"] = warehouse
        
    if filters and filters.get("customer"):
        conditions += " AND so.customer = %(customer)s"
        filter_values["customer"] = filters.get("customer")
        
    if filters and filters.get("sales_order"):
        conditions += " AND sre.voucher_no = %(sales_order)s"
        filter_values["sales_order"] = filters.get("sales_order")
    
    query = """
        SELECT 
            sre.name,
            sre.item_code,
            sre.reserved_qty,
            COALESCE(sre.delivered_qty, 0) as delivered_qty,
            (sre.reserved_qty - COALESCE(sre.delivered_qty, 0)) as pending_qty,
            sre.warehouse,
            sre.voucher_no as sales_order,
            sre.status,
            so.customer,
            so.customer_name
        FROM 
            `tabStock Reservation Entry` sre
        INNER JOIN 
            `tabSales Order` so ON sre.voucher_no = so.name
        WHERE 
            sre.docstatus = 1 
            AND sre.item_code = %(item_code)s
            AND sre.status IN ('Reserved', 'Partially Delivered')
            AND (sre.reserved_qty - COALESCE(sre.delivered_qty, 0)) > 0
            {conditions}
        ORDER BY 
            sre.creation
    """.format(conditions=conditions)
    
    reservations = frappe.db.sql(query, filter_values, as_dict=1)
    
    # Use pending quantity
    for reservation in reservations:
        reservation.reserved_qty = reservation.pending_qty
    
    return reservations

def get_purchase_order_qty(item_code, warehouse):
    """Get Purchase Order quantities pending for an item"""
    conditions = ""
    if warehouse and warehouse != 'All Warehouses':
        conditions = " AND poi.warehouse = %(warehouse)s"
    
    query = """
        SELECT 
            COALESCE(SUM(poi.qty - COALESCE(poi.received_qty, 0)), 0) as po_pending_qty
        FROM 
            `tabPurchase Order Item` poi
        INNER JOIN 
            `tabPurchase Order` po ON poi.parent = po.name
        WHERE 
            poi.item_code = %(item_code)s
            AND po.docstatus = 1
            AND po.status NOT IN ('Closed', 'Cancelled')
            AND (poi.qty - COALESCE(poi.received_qty, 0)) > 0
            {conditions}
    """.format(conditions=conditions)
    
    result = frappe.db.sql(query, {
        "item_code": item_code,
        "warehouse": warehouse
    }, as_dict=1)
    
    return flt(result[0].po_pending_qty) if result else 0

def get_material_transfer_qty(item_code, warehouse):
    """Get Material Transfer quantities in transit"""
    if warehouse == 'All Warehouses':
        return 0
        
    query = """
        SELECT 
            COALESCE(SUM(sed.qty), 0) as transfer_qty
        FROM 
            `tabStock Entry Detail` sed
        INNER JOIN 
            `tabStock Entry` se ON sed.parent = se.name
        WHERE 
            sed.item_code = %(item_code)s
            AND se.purpose = 'Material Transfer'
            AND se.docstatus = 1
            AND sed.t_warehouse = %(warehouse)s
            AND se.name NOT IN (
                SELECT se2.name 
                FROM `tabStock Entry Detail` sed2
                INNER JOIN `tabStock Entry` se2 ON sed2.parent = se2.name
                WHERE sed2.item_code = %(item_code)s
                AND se2.purpose = 'Material Receipt'
                AND se2.docstatus = 1
                AND sed2.s_warehouse = %(warehouse)s
                AND se2.posting_date >= se.posting_date
            )
    """
    
    result = frappe.db.sql(query, {
        "item_code": item_code,
        "warehouse": warehouse
    }, as_dict=1)
    
    return flt(result[0].transfer_qty) if result else 0

def get_conditions(filters):
    conditions = ""
    
    if filters:
        if filters.get("item_group"):
            conditions += " AND i.item_group = %(item_group)s"
            
        if filters.get("item_code"):
            conditions += " AND i.item_code = %(item_code)s"
            
        if filters.get("item_name"):
            conditions += " AND i.item_name LIKE %(item_name)s"
            filters["item_name"] = f"%{filters.get('item_name')}%"
            
        if filters.get("warehouse"):
            conditions += " AND bin.warehouse = %(warehouse)s"
    
    return conditions

@frappe.whitelist()
def debug_reservations(item_code=None):
    """Debug function to check reservation data"""
    conditions = ""
    values = {}
    
    if item_code:
        conditions = "AND sre.item_code = %(item_code)s"
        values["item_code"] = item_code
    
    query = f"""
        SELECT 
            sre.name,
            sre.item_code,
            sre.reserved_qty,
            sre.delivered_qty,
            sre.status,
            sre.docstatus,
            sre.warehouse,
            sre.voucher_no,
            so.customer
        FROM 
            `tabStock Reservation Entry` sre
        LEFT JOIN 
            `tabSales Order` so ON sre.voucher_no = so.name
        WHERE 
            sre.docstatus = 1
            {conditions}
        ORDER BY 
            sre.creation DESC
        LIMIT 10
    """
    
    result = frappe.db.sql(query, values, as_dict=1)
    return result

@frappe.whitelist()
def unreserve_stock(stock_reservation_entry):
    """Cancel stock reservation entry"""
    try:
        doc = frappe.get_doc("Stock Reservation Entry", stock_reservation_entry)
        if doc.docstatus == 1:
            doc.cancel()
            frappe.db.commit()
            return {"status": "success", "message": "Stock reservation cancelled successfully"}
        else:
            return {"status": "error", "message": "Stock reservation entry is not submitted"}
    except Exception as e:
        frappe.log_error(f"Error unreserving stock: {str(e)}")
        return {"status": "error", "message": str(e)}