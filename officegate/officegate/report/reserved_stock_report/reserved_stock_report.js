// Copyright (c) 2025, Your Company and contributors
// For license information, please see license.txt

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

		// Format actual_qty in green and bold
		if (column.fieldname == "actual_qty" && data.actual_qty) {
			value = `<span style="color: green; font-weight: bold;">${data.actual_qty}</span>`;
		}

		// Format ordered_qty in orange and bold
		if (column.fieldname == "ordered_qty" && data.ordered_qty) {
			value = `<span style="color: orange; font-weight: bold;">${data.ordered_qty}</span>`;
		}

		// Format reserved_qty in red and bold
		if (column.fieldname == "reserved_qty" && data.reserved_qty) {
			value = `<span style="color: red; font-weight: bold;">${data.reserved_qty}</span>`;
		}

		// Format reserved_qty_detail in red and bold
		if (column.fieldname == "reserved_qty_detail" && data.reserved_qty_detail) {
			value = `<span style="color: red; font-weight: bold;">${data.reserved_qty_detail}</span>`;
		}

		// Add unreserve button
		if (column.fieldname == "unreserve" && value == "Unreserve" && data._voucher_type == "Sales Order") {
			value = `<button class="btn btn-xs btn-danger unreserve-btn" 
                        data-item="${data._item_code}" 
                        data-voucher-type="${data._voucher_type}" 
                        data-voucher-no="${data._voucher_no}">
                        ${__("Unreserve")}
                    </button>`;
		}

		return value;
	},

	"onload": function (report) {
		// Handle unreserve button clicks
		report.$report.on('click', '.unreserve-btn', function () {
			let $btn = $(this);
			let item_code = $btn.data('item');
			let voucher_type = $btn.data('voucher-type');
			let voucher_no = $btn.data('voucher-no');

			frappe.confirm(
				__('Are you sure you want to unreserve stock for {0} from {1}?', [item_code, voucher_no]),
				function () {
					// Disable button
					$btn.prop('disabled', true).text(__('Unreserving...'));

					frappe.call({
						method: "your_app.your_module.report.item_stock_status_report.item_stock_status_report.unreserve_stock",
						args: {
							item_code: item_code,
							voucher_type: voucher_type,
							voucher_no: voucher_no
						},
						callback: function (r) {
							if (r.message.status === "success") {
								frappe.show_alert({
									message: r.message.message,
									indicator: 'green'
								});
								// Refresh the report
								report.refresh();
							} else {
								frappe.show_alert({
									message: r.message.message,
									indicator: 'red'
								});
								// Re-enable button
								$btn.prop('disabled', false).text(__('Unreserve'));
							}
						},
						error: function () {
							frappe.show_alert({
								message: __('An error occurred while unreserving stock'),
								indicator: 'red'
							});
							// Re-enable button
							$btn.prop('disabled', false).text(__('Unreserve'));
						}
					});
				}
			);
		});
	}
};