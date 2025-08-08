frappe.ui.form.on('Sales Invoice', {
    after_save(frm) {
        if (!frm.doc.delivery_note_created) {
            frappe.call({
                method: "officegate.api.create_delivery_note_from_invoice",
                args: {
                    invoice_name: frm.doc.name
                },
                callback(r) {
                    if (r.message) {
                        frappe.msgprint("Delivery Note created: " + r.message);
                        // frm.set_value("delivery_note_created", 1);
                        frm.save();
                    }
                }
            });
        }
    }
});
