// reserved_stock_report.js

function unreserve_stock(reservation_entry) {
	frappe.confirm(
		__('Are you sure you want to unreserve this stock? This will cancel the Stock Reservation Entry.'),
		function () {
			frappe.call({
				method: 'officegate.officegate.report.reserved_stock_report.reserved_stock_report.unreserve_stock',
				args: {
					stock_reservation_entry: reservation_entry
				},
				callback: function (r) {
					if (r.message && r.message.status === 'success') {
						frappe.msgprint({
							message: r.message.message,
							indicator: 'green'
						});
						// Refresh the report
						frappe.query_report.refresh();
					} else {
						frappe.msgprint({
							message: r.message ? r.message.message : 'Error occurred while unreserving stock',
							indicator: 'red'
						});
					}
				},
				error: function (r) {
					frappe.msgprint({
						message: 'Error occurred while unreserving stock',
						indicator: 'red'
					});
				}
			});
		}
	);
}

frappe.query_reports["Reserved Stock Report"] = {
	"filters": [
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"width": "80"
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "80",
			"get_query": function () {
				return {
					filters: {
						"disabled": 0
					}
				};
			}
		},
		{
			"fieldname": "item_name",
			"label": __("Item Name"),
			"fieldtype": "Data",
			"width": "80"
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "80"
		},
		{
			"fieldname": "sales_order",
			"label": __("Sales Order"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": "80",
			"get_query": function () {
				return {
					filters: {
						"docstatus": 1,
						"status": ["!=", "Closed"]
					}
				};
			}
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": "80",
			"get_query": function () {
				return {
					filters: {
						"disabled": 0
					}
				};
			}
		}
	],

	onload: function (report) {
		// Add refresh button
		report.page.add_inner_button(__('Refresh'), function () {
			report.refresh();
		});

		// Add debug button for troubleshooting
		report.page.add_inner_button(__('Debug Reservations'), function () {
			frappe.call({
				method: 'your_app.your_module.report.reserved_stock_report.reserved_stock_report.debug_reservations',
				callback: function (r) {
					if (r.message) {
						console.log('Reservation Data:', r.message);
						frappe.msgprint({
							title: 'Debug Info',
							message: `Found ${r.message.length} reservation entries. Check console for details.`,
							indicator: 'blue'
						});
					} else {
						frappe.msgprint('No reservation entries found');
					}
				}
			});
		});

		// Set auto-refresh every 30 seconds for real-time updates
		setInterval(function () {
			if (report.page.is_visible()) {
				report.refresh();
			}
		}, 30000);
	},

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "actions" && data && data.actions) {
			return data.actions;
		}

		// Highlight negative quantities in red
		if (column.fieldname == "qty_after_reservation" && data && data.qty_after_reservation < 0) {
			value = `<span style="color: red; font-weight: bold;">${value}</span>`;
		}

		// Highlight reserved quantities in orange
		if (column.fieldname == "reserved_qty" && data && data.reserved_qty > 0 && data.indent == 0) {
			value = `<span style="color: orange; font-weight: bold;">${value}</span>`;
		}

		return value;
	},

	get_datatable_options(options) {
		return Object.assign(options, {
			checkboxColumn: false,
			inlineFilters: true,
			treeView: true
		});
	}
};