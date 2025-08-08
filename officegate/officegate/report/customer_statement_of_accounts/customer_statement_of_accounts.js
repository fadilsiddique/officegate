// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Statement of Accounts"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"reqd": 1,
			"on_change": function () {
				// Auto-populate customer details when customer is selected
				if (frappe.query_report.get_filter_value('customer')) {
					frappe.call({
						method: "officegate.officegate.report.customer_statement_of_accounts.customer_statement_of_accounts.get_customer_details",
						args: {
							customer: frappe.query_report.get_filter_value('customer')
						},
						callback: function (r) {
							if (r.message) {
								frappe.query_report.customer_details = r.message;
							}
						}
					});
				}
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "include_opening_balance",
			"label": __("Include Opening Balance"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "group_by_reference",
			"label": __("Group by Reference"),
			"fieldtype": "Check",
			"default": 0
		}
	],

	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "balance") {
			if (data && data.balance < 0) {
				value = `<span style='color:green'>${value}</span>`;
			} else if (data && data.balance > 0) {
				value = `<span style='color:red'>${value}</span>`;
			}
		}

		if (column.fieldname == "our_ref") {
			if (data && data.voucher_no) {
				let route = "";
				if (data.voucher_type === "Sales Invoice") {
					route = `/app/sales-invoice/${data.voucher_no}`;
				} else if (data.voucher_type === "Payment Entry") {
					route = `/app/payment-entry/${data.voucher_no}`;
				} else if (data.voucher_type === "Journal Entry") {
					route = `/app/journal-entry/${data.voucher_no}`;
				}

				if (route) {
					value = `<a href="${route}" target="_blank">${value}</a>`;
				}
			}
		}

		return value;
	},

	"onload": function (report) {
		// Add custom buttons
		report.page.add_inner_button(__("Print Statement"), function () {
			let filters = report.get_values();
			if (!filters.customer) {
				frappe.msgprint(__("Please select a customer first"));
				return;
			}

			// Open print format
			let url = `/printview?doctype=Customer&name=${filters.customer}&format=Customer Statement&trigger_print=1`;

			// Add filter parameters to URL for print format
			let params = new URLSearchParams({
				from_date: filters.from_date,
				to_date: filters.to_date,
				company: filters.company
			});

			url += '&' + params.toString();
			window.open(url, '_blank');
		});

		report.page.add_inner_button(__("Send Email"), function () {
			let filters = report.get_values();
			if (!filters.customer) {
				frappe.msgprint(__("Please select a customer first"));
				return;
			}

			frappe.call({
				method: "your_app.your_module.report.customer_statement_of_accounts.customer_statement_of_accounts.send_statement_email",
				args: {
					customer: filters.customer,
					from_date: filters.from_date,
					to_date: filters.to_date,
					company: filters.company
				},
				callback: function (r) {
					if (r.message) {
						frappe.msgprint(__("Statement sent successfully"));
					}
				}
			});
		});

		report.page.add_inner_button(__("Export to Excel"), function () {
			let filters = report.get_values();
			report.export_report();
		});
	},

	"get_datatable_options": function (options) {
		return Object.assign(options, {
			checkboxColumn: false,
			inlineFilters: true,
			treeView: false
		});
	}
};

// Custom functions for additional features
frappe.query_reports["Customer Statement of Accounts"].send_statement_email = function (filters) {
	let d = new frappe.ui.Dialog({
		title: __("Send Customer Statement"),
		fields: [
			{
				fieldname: "to_email",
				label: __("To Email"),
				fieldtype: "Data",
				reqd: 1
			},
			{
				fieldname: "cc_email",
				label: __("CC Email"),
				fieldtype: "Data"
			},
			{
				fieldname: "subject",
				label: __("Subject"),
				fieldtype: "Data",
				default: __("Customer Statement of Accounts"),
				reqd: 1
			},
			{
				fieldname: "message",
				label: __("Message"),
				fieldtype: "Text Editor",
				default: __("Please find attached your statement of accounts.")
			}
		],
		primary_action: function () {
			let values = d.get_values();
			frappe.call({
				method: "your_app.your_module.report.customer_statement_of_accounts.customer_statement_of_accounts.send_email",
				args: {
					customer: filters.customer,
					from_date: filters.from_date,
					to_date: filters.to_date,
					company: filters.company,
					to_email: values.to_email,
					cc_email: values.cc_email,
					subject: values.subject,
					message: values.message
				},
				callback: function (r) {
					if (!r.exc) {
						d.hide();
						frappe.show_alert(__("Email sent successfully"));
					}
				}
			});
		},
		primary_action_label: __("Send Email")
	});
	d.show();
};