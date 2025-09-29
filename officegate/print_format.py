import frappe

def _get_allowed_formats():
    # safely get list from site_config
    return frappe.get_site_config().get("allowed_print_formats", [])

# --- Permission query ---
def get_permission_query_conditions(user):
    if not user or user == "Administrator":
        return ""

    allowed_formats = _get_allowed_formats()
    if not allowed_formats:
        return "1=0"

    names = "', '".join([frappe.db.escape(f) for f in allowed_formats])
    return f"`tabPrint Format`.name in ({names})"

# --- Override for dropdown ---
def get_print_formats(doctype, docname=None):
    allowed_formats = _get_allowed_formats()
    if not allowed_formats:
        return []

    existing = frappe.get_all(
        "Print Format",
        filters={"doctype": doctype, "name": ["in", allowed_formats]},
        pluck="name"
    )
    return existing
