app_name = "officegate"
app_title = "Officegate"
app_publisher = "Fadil"
app_description = "Office Gate Furnitures"
app_email = "fadil@upscapetech.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "officegate",
# 		"logo": "/assets/officegate/logo.png",
# 		"title": "Officegate",
# 		"route": "/officegate",
# 		"has_permission": "officegate.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/officegate/css/officegate.css"
app_include_js = ["/assets/officegate/js/quotations.js","/assets/officegate/js/custom.js"]

# include js, css files in header of web template
# web_include_css = "/assets/officegate/css/officegate.css"
# web_include_js = "/assets/officegate/js/officegate.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "officegate/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_list_js = {"Item" : "public/js/item_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "officegate/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "officegate.utils.jinja_methods",
# 	"filters": "officegate.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "officegate.install.before_install"
# after_install = "officegate.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "officegate.uninstall.before_uninstall"
# after_uninstall = "officegate.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "officegate.utils.before_app_install"
# after_app_install = "officegate.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "officegate.utils.before_app_uninstall"
# after_app_uninstall = "officegate.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "officegate.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
    "Delivery Note": {
        "validate": "officegate.api.validate_no_duplicate_against_invoice",
        "autoname": "officegate.doc_naming.delivery_note_autoname"
    },
    "Sales Invoice": {
        "autoname": "officegate.doc_naming.sales_invoice_autoname"
    },
    "Quotation": {
        "autoname": "officegate.doc_naming.quotation_autoname"
    },
    "Purchase Order": {
        "autoname": "officegate.doc_naming.purchase_order_autoname"
    },
    "Purchase Invoice": {
        "autoname": "officegate.doc_naming.purchase_invoice_autoname",
    },
    "Sales Order": {
        "autoname": "officegate.doc_naming.sales_order_autoname",
    },
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"officegate.tasks.all"
# 	],
# 	"daily": [
# 		"officegate.tasks.daily"
# 	],
# 	"hourly": [
# 		"officegate.tasks.hourly"
# 	],
# 	"weekly": [
# 		"officegate.tasks.weekly"
# 	],
# 	"monthly": [
# 		"officegate.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "officegate.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "officegate.event.get_events"
# }

# override_whitelisted_methods = {
#     "frappe.utils.print_format.download_pdf": "officegate.pdf_override.download_pdf"
# }

# permission_query_conditions = {
#     "Print Format": "officegate.print_format.get_permission_query_conditions"
# }

# override_whitelisted_methods = {
#     "frappe.desk.print_report.get_print_formats": "officegate.print_format.get_print_formats"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "officegate.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["officegate.utils.before_request"]
# after_request = ["officegate.utils.after_request"]

# Job Events
# ----------
# before_job = ["officegate.utils.before_job"]
# after_job = ["officegate.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"officegate.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

