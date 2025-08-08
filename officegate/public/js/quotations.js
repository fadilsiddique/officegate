
frappe.ui.form.on('Quotation Item', {
    item_code: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Item',
                    filters: { 'name': row.item_code },
                    fieldname: ['image', 'item_name']
                },
                callback: function (r) {
                    if (r.message && r.message.image) {
                        // Show image preview dialog
                        let dialog = new frappe.ui.Dialog({
                            title: `Item: ${row.item_code}`,
                            size: 'small',
                            fields: [
                                {
                                    fieldtype: 'HTML',
                                    options: `
                                        <div style="text-align: center; padding: 20px;">
                                            <img src="${r.message.image}" 
                                                 style="max-width: 300px; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                                            <p style="margin-top: 15px; font-weight: bold;">${r.message.item_name || row.item_code}</p>
                                            <p style="font-size: 12px; color: #666; margin-top: 10px;">Press Enter or Escape to continue to Qty field</p>
                                        </div>
                                    `
                                }
                            ],
                            primary_action_label: 'Continue (Enter)',
                            primary_action: function () {
                                dialog.hide();
                                focus_qty_field(cdn);
                            }
                        });

                        dialog.show();

                        // Handle keyboard events
                        dialog.$wrapper.on('keydown', function (e) {
                            if (e.keyCode === 13 || e.keyCode === 27) { // Enter or Escape
                                e.preventDefault();
                                dialog.hide();
                                focus_qty_field(cdn);
                            }
                        });

                        // Auto close after 3 seconds
                        setTimeout(() => {
                            if (dialog && dialog.$wrapper.is(':visible')) {
                                dialog.hide();
                                focus_qty_field(cdn);
                            }
                        }, 3000);
                    } else {
                        // No image, directly focus qty field
                        focus_qty_field(cdn);
                    }
                }
            });
        } else {
            // No item selected, focus qty field anyway
            focus_qty_field(cdn);
        }
    }
});

// Helper function to focus qty field
function focus_qty_field(cdn) {
    setTimeout(() => {
        let row = $(`[data-name="${cdn}"]`);
        let qty_field = row.find('[data-fieldname="qty"] input');
        if (qty_field.length) {
            qty_field.focus().select();
        }
    }, 200);
}