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

	// Custom print HTML function
	"get_print_html": function (columns, data, filters, summary) {
		let customer_details = frappe.query_report.customer_details || {};

		// Calculate totals
		let total_debit = 0;
		let total_credit = 0;
		let outstanding_balance = 0;

		data.forEach(row => {
			total_debit += (row.debit || 0);
			total_credit += (row.credit || 0);
			outstanding_balance = row.balance || 0;
		});

		// Generate HTML
		let html = `
		<style>
			@page { size: A4; margin: 10mm; }
			* { margin: 0; padding: 0; box-sizing: border-box; }
			body { font-family: Arial, sans-serif; font-size: 11px; line-height: 1.4; color: #333; }
			.container { max-width: 210mm; margin: 0 auto; padding: 15mm; }
			.header { display: flex; justify-content: space-between; margin-bottom: 20px; border-bottom: 1px solid #ddd; padding-bottom: 15px; }
			.company-info { flex: 1; }
			.company-logo { display: flex; align-items: center; margin-bottom: 10px; }
			.logo-placeholder { width: 50px; height: 50px; background: #f0f0f0; border: 2px solid #ddd; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-size: 10px; color: #666; }
			.company-details h1 { font-size: 16px; color: #2c5cc5; margin-bottom: 2px; font-weight: bold; }
			.company-details p { font-size: 10px; color: #666; margin: 1px 0; }
			.statement-title { text-align: right; flex: 1; }
			.statement-title h2 { font-size: 18px; color: #2c5cc5; margin-bottom: 5px; }
			.statement-date { font-size: 10px; color: #666; }
			.customer-section { display: flex; justify-content: space-between; margin-bottom: 20px; }
			.customer-info, .sales-info { flex: 1; }
			.customer-info h3 { font-size: 11px; margin-bottom: 8px; color: #333; }
			.customer-details p, .sales-details p { font-size: 10px; margin: 2px 0; color: #555; }
			.sales-info { text-align: right; margin-left: 50px; }
			.statement-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 10px; }
			.statement-table th { background-color: #f8f9fa; border: 1px solid #ddd; padding: 8px; text-align: center; font-weight: bold; }
			.statement-table td { border: 1px solid #ddd; padding: 6px; text-align: left; }
			.statement-table td.number { text-align: right; }
			.statement-table td.center { text-align: center; }
			.statement-table tr:nth-child(even) { background-color: #fafafa; }
			.summary-section { display: flex; justify-content: flex-end; margin-top: 20px; }
			.summary-table { border-collapse: collapse; font-size: 11px; min-width: 200px; }
			.summary-table td { border: 1px solid #ddd; padding: 8px; }
			.summary-table .label { background-color: #f8f9fa; font-weight: bold; text-align: right; }
			.summary-table .amount { text-align: right; min-width: 100px; }
			.balance-positive { color: #d32f2f; font-weight: bold; }
			.balance-negative { color: #2e7d32; font-weight: bold; }
			.opening-balance { background-color: #e3f2fd !important; font-weight: bold; }
		</style>
		
		<div class="container">
			<!-- Header Section -->
			<div class="header">
				<div class="company-info">
					<div class="company-logo">
						<div class="logo-placeholder">LOGO</div>
						<div class="company-details">
							<h1>CAPITAL ONE</h1>
							<p>office furniture</p>
						</div>
					</div>
				</div>
				<div class="statement-title">
					<h2>Customer Statement</h2>
					<div class="statement-date">
						<strong>Date:</strong> ${frappe.datetime.str_to_user(filters.to_date)}
					</div>
				</div>
			</div>

			<!-- Customer Information Section -->
			<div class="customer-section">
				<div class="customer-info">
					<h3>C/Name: ${customer_details.customer_name || ''}</h3>
					<p><strong>Tel:</strong> ${customer_details.contact_details?.phone || 'N/A'}</p>
					<p><strong>Mob:</strong> ${customer_details.contact_details?.mobile || 'N/A'}</p>
					<p><strong>Email:</strong> ${customer_details.contact_details?.email || 'N/A'}</p>
					<p><strong>Location:</strong> ${customer_details.address_details?.city || 'N/A'}</p>
				</div>
				<div class="sales-info">
					<p><strong>Sales:</strong> ${frappe.session.user}</p>
					<p><strong>Mob:</strong> N/A</p>
					<p><strong>Email:</strong> ${frappe.session.user}</p>
				</div>
			</div>

			<!-- Statement Table -->
			<table class="statement-table">
				<thead>
					<tr>
						${columns.map(col => `<th>${col.label}</th>`).join('')}
					</tr>
				</thead>
				<tbody>
					${data.map(row => {
			let isOpeningBalance = row.our_ref && row.our_ref.includes('Opening Balance');
			let balanceClass = row.balance > 0 ? 'balance-positive' : (row.balance < 0 ? 'balance-negative' : '');

			return `<tr ${isOpeningBalance ? 'class="opening-balance"' : ''}>
							<td class="center">${row.date ? frappe.datetime.str_to_user(row.date) : ''}</td>
							<td>${row.our_ref || ''}</td>
							<td>${row.your_ref || ''}</td>
							<td class="number">${row.debit > 0 ? format_currency(row.debit, null, 2) : ''}</td>
							<td class="number">${row.credit > 0 ? format_currency(row.credit, null, 2) : ''}</td>
							<td class="number ${balanceClass}">${format_currency(row.balance || 0, null, 2)}</td>
						</tr>`;
		}).join('')}
				</tbody>
			</table>

			<!-- Summary Section -->
			<div class="summary-section">
				<table class="summary-table">
					<tr>
						<td class="label">Total:</td>
						<td class="amount">${format_currency(total_debit, null, 2)}</td>
						<td class="amount">${format_currency(total_credit, null, 2)}</td>
						<td class="amount">${format_currency(outstanding_balance, null, 2)}</td>
					</tr>
					<tr>
						<td class="label">Outstanding:</td>
						<td class="amount" colspan="2">${format_currency(outstanding_balance, null, 2)}</td>
						<td class="amount"></td>
					</tr>
					<tr>
						<td class="label">Total Invoices:</td>
						<td class="amount" colspan="2">${data.length}</td>
						<td class="amount"></td>
					</tr>
				</table>
			</div>
		</div>`;

		return html;
	},

	"onload": function (report) {
		// Add custom buttons
		report.page.add_inner_button(__("Print Statement"), function () {
			let filters = report.get_values();
			if (!filters.customer) {
				frappe.msgprint(__("Please select a customer first"));
				return;
			}

			// Custom print function that doesn't rely on ERPNext's print system
			frappe.query_reports["Customer Statement of Accounts"].custom_print(report, filters);
		});

		report.page.add_inner_button(__("Send Email"), function () {
			let filters = report.get_values();
			if (!filters.customer) {
				frappe.msgprint(__("Please select a customer first"));
				return;
			}

			frappe.call({
				method: "officegate.officegate.report.customer_statement_of_accounts.customer_statement_of_accounts.send_statement_email",
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
	},

	"get_datatable_options": function (options) {
		return Object.assign(options, {
			checkboxColumn: false,
			inlineFilters: true,
			treeView: false
		});
	},

	// Print settings
	"print_settings": {
		"orientation": "Portrait",
		"page_size": "A4"
	}
};