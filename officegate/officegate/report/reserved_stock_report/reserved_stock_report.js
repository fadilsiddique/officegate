frappe.query_reports["Reserved Stock Report"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "sales_order",
			"label": __("Sales Order"),
			"fieldtype": "Link",
			"options": "Sales Order"
		},
		{
			"fieldname": "purchase_order",
			"label": __("Purchase Order"),
			"fieldtype": "Link",
			"options": "Purchase Order"
		}
	],

	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// Format parent rows (item rows)
		if (data.indent === 0) {
			if (column.fieldname === "item_code") {
				value = `<b>${value}</b>`;
			}
			else if (column.fieldname === "actual_qty") {
				value = `<b style="color: green;">${value}</b>`;
			}
			else if (column.fieldname === "reserved_qty") {
				value = `<b style="color: red;">${value}</b>`;
			}
			else if (column.fieldname === "ordered_qty") {
				value = `<b style="color: orange;">${value}</b>`;
			}
		}

		// Format child rows (reservation details)
		if (data.indent === 1) {
			if (column.fieldname === "document_name") {
				value = `<b>${value}</b>`;
			}
			else if (column.fieldname === "unreserve" && data.stock_reservation_entry) {
				value = `<button class="btn btn-xs btn-danger" 
                    onclick="unreserve_stock('${data.stock_reservation_entry}')">
                    Unreserve
                </button>`;
			}
		}

		return value;
	}
};

function unreserve_stock(stock_reservation_entry) {
	frappe.confirm(
		__('Are you sure you want to cancel this stock reservation?'),
		function () {
			frappe.call({
				method: 'frappe.client.cancel',
				args: {
					doctype: 'Stock Reservation Entry',
					name: stock_reservation_entry
				},
				callback: function (r) {
					if (!r.exc) {
						frappe.show_alert({
							message: __('Stock reservation cancelled successfully'),
							indicator: 'green'
						});
						frappe.query_report.refresh();
					}
				}
			});
		}
	);
}