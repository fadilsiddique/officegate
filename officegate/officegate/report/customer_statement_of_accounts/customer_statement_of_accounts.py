# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, add_days

def execute(filters=None):
    if not filters:
        filters = {}
    
    validate_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def validate_filters(filters):
    if not filters.get("customer"):
        frappe.throw(_("Customer is mandatory"))
    
    if not filters.get("from_date"):
        filters["from_date"] = add_days(nowdate(), -30)
    
    if not filters.get("to_date"):
        filters["to_date"] = nowdate()

def get_columns():
    return [
        {
            "fieldname": "date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 90
        },
        {
            "fieldname": "our_ref",
            "label": _("Our Ref"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "your_ref",
            "label": _("Your Ref"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "debit",
            "label": _("Debit"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "credit",
            "label": _("Credit"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "balance",
            "label": _("Balance"),
            "fieldtype": "Currency",
            "width": 120
        }
    ]

def get_data(filters):
    customer = filters.get("customer")
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    company = filters.get("company") or frappe.defaults.get_user_default("Company")
    
    # Get opening balance
    opening_balance = get_opening_balance(customer, from_date, company)
    
    # Get all transactions
    transactions = get_customer_transactions(customer, from_date, to_date, company)
    
    data = []
    running_balance = opening_balance
    
    # Add opening balance row if non-zero
    if opening_balance != 0:
        data.append({
            "date": add_days(from_date, -1),
            "our_ref": "Opening Balance",
            "your_ref": "",
            "debit": opening_balance if opening_balance > 0 else 0,
            "credit": abs(opening_balance) if opening_balance < 0 else 0,
            "balance": opening_balance,
            "indent": 0
        })
    
    # Process transactions
    for transaction in transactions:
        debit = transaction.get("debit", 0)
        credit = transaction.get("credit", 0)
        
        running_balance += debit - credit
        
        data.append({
            "date": transaction.get("posting_date"),
            "our_ref": transaction.get("our_ref", ""),
            "your_ref": transaction.get("your_ref", ""),
            "debit": debit if debit > 0 else 0,
            "credit": credit if credit > 0 else 0,
            "balance": running_balance,
            "voucher_type": transaction.get("voucher_type"),
            "voucher_no": transaction.get("voucher_no"),
            "indent": 0
        })
    
    return data

def get_opening_balance(customer, from_date, company):
    """Get opening balance for customer before from_date"""
    
    # Get balance from GL entries
    gl_balance = frappe.db.sql("""
        SELECT IFNULL(SUM(debit - credit), 0) as balance
        FROM `tabGL Entry`
        WHERE party_type = 'Customer'
        AND party = %s
        AND company = %s
        AND posting_date < %s
        AND is_cancelled = 0
    """, (customer, company, from_date))
    
    return flt(gl_balance[0][0]) if gl_balance else 0

def get_customer_transactions(customer, from_date, to_date, company):
    """Get all customer transactions within date range"""
    
    conditions = get_conditions(customer, from_date, to_date, company)
    
    # Sales Invoices
    sales_invoices = frappe.db.sql("""
        SELECT 
            si.posting_date,
            CONCAT('INV-', si.name) as our_ref,
            si.po_no as your_ref,
            si.grand_total as debit,
            0 as credit,
            'Sales Invoice' as voucher_type,
            si.name as voucher_no,
            si.due_date
        FROM `tabSales Invoice` si
        WHERE si.customer = %(customer)s
        AND si.company = %(company)s
        AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND si.docstatus = 1
        AND si.status NOT IN ('Cancelled', 'Draft')
        ORDER BY si.posting_date, si.creation
    """, {
        "customer": customer,
        "company": company,
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=1)
    
    # Payment Entries
    payment_entries = frappe.db.sql("""
        SELECT 
            pe.posting_date,
            CONCAT('PMT-', pe.name) as our_ref,
            pe.reference_no as your_ref,
            0 as debit,
            pe.paid_amount as credit,
            'Payment Entry' as voucher_type,
            pe.name as voucher_no
        FROM `tabPayment Entry` pe
        WHERE pe.party = %(customer)s
        AND pe.company = %(company)s
        AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND pe.docstatus = 1
        AND pe.payment_type = 'Receive'
        ORDER BY pe.posting_date, pe.creation
    """, {
        "customer": customer,
        "company": company,
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=1)
    
    # Credit Notes (Sales Returns)
    credit_notes = frappe.db.sql("""
        SELECT 
            si.posting_date,
            CONCAT('CRN-', si.name) as our_ref,
            si.return_against as your_ref,
            0 as debit,
            ABS(si.grand_total) as credit,
            'Sales Invoice' as voucher_type,
            si.name as voucher_no
        FROM `tabSales Invoice` si
        WHERE si.customer = %(customer)s
        AND si.company = %(company)s
        AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND si.docstatus = 1
        AND si.is_return = 1
        AND si.status NOT IN ('Cancelled', 'Draft')
        ORDER BY si.posting_date, si.creation
    """, {
        "customer": customer,
        "company": company,
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=1)
    
    # Journal Entries
    journal_entries = frappe.db.sql("""
        SELECT 
            je.posting_date,
            CONCAT('JE-', je.name) as our_ref,
            je.user_remark as your_ref,
            CASE WHEN jea.debit > 0 THEN jea.debit ELSE 0 END as debit,
            CASE WHEN jea.credit > 0 THEN jea.credit ELSE 0 END as credit,
            'Journal Entry' as voucher_type,
            je.name as voucher_no
        FROM `tabJournal Entry` je
        INNER JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
        WHERE jea.party = %(customer)s
        AND je.company = %(company)s
        AND je.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND je.docstatus = 1
        AND jea.party_type = 'Customer'
        ORDER BY je.posting_date, je.creation
    """, {
        "customer": customer,
        "company": company,
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=1)
    
    # Combine all transactions and sort by date
    all_transactions = sales_invoices + payment_entries + credit_notes + journal_entries
    all_transactions = sorted(all_transactions, key=lambda x: (x.posting_date, x.our_ref))
    
    return all_transactions

def get_conditions(customer, from_date, to_date, company):
    conditions = {
        "customer": customer,
        "company": company,
        "from_date": from_date,
        "to_date": to_date
    }
    return conditions

@frappe.whitelist()
def get_customer_details(customer):
    """Get customer details for the report header"""
    customer_doc = frappe.get_doc("Customer", customer)
    
    # Get primary contact
    primary_contact = frappe.db.get_value("Dynamic Link", {
        "link_doctype": "Customer",
        "link_name": customer,
        "parenttype": "Contact"
    }, "parent")
    
    contact_details = {}
    if primary_contact:
        contact_doc = frappe.get_doc("Contact", primary_contact)
        contact_details = {
            "phone": contact_doc.phone,
            "mobile": contact_doc.mobile_no,
            "email": contact_doc.email_id
        }
    
    # Get primary address
    primary_address = frappe.db.get_value("Dynamic Link", {
        "link_doctype": "Customer",
        "link_name": customer,
        "parenttype": "Address"
    }, "parent")
    
    address_details = {}
    if primary_address:
        address_doc = frappe.get_doc("Address", primary_address)
        address_details = {
            "address_line1": address_doc.address_line1,
            "address_line2": address_doc.address_line2,
            "city": address_doc.city,
            "state": address_doc.state,
            "country": address_doc.country,
            "pincode": address_doc.pincode
        }
    
    return {
        "customer_name": customer_doc.customer_name,
        "customer_code": customer_doc.name,
        "customer_group": customer_doc.customer_group,
        "territory": customer_doc.territory,
        "contact_details": contact_details,
        "address_details": address_details
    }

# Report Summary Functions
def get_report_summary(data, filters):
    """Generate report summary for dashboard"""
    if not data:
        return []
    
    total_debit = sum([flt(row.get("debit", 0)) for row in data])
    total_credit = sum([flt(row.get("credit", 0)) for row in data])
    outstanding_balance = data[-1].get("balance", 0) if data else 0
    
    return [
        {
            "value": total_debit,
            "label": _("Total Debit"),
            "datatype": "Currency",
            "indicator": "Blue"
        },
        {
            "value": total_credit,
            "label": _("Total Credit"),
            "datatype": "Currency",
            "indicator": "Green"
        },
        {
            "value": outstanding_balance,
            "label": _("Outstanding Balance"),
            "datatype": "Currency",
            "indicator": "Red" if outstanding_balance > 0 else "Green"
        }
    ]