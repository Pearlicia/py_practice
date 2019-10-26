import odoorpc

import settings
"""settings module contains various constants used
to connect with Odoo on my VPS"""


if __name__ == "__main__":
    odoo = odoorpc.ODOO(settings.ODOO_HOST, port=settings.ODOO_PORT, timeout=10)
    odoo.login(settings.ODOO_DB, settings.ODOO_USER, settings.ODOO_PASSWORD)

    Partner = odoo.env["res.partner"]
    # This partner already exists in DB
    customer = Partner.browse([22])

    Invoice = odoo.env["account.invoice"]
    invoice_id = Invoice.create({
        'partner_id' : customer.id,
        'state': 'draft',
        # This is ID for "Customers Invoices" journal
        'journal_id': 1,
        'account_id': customer.property_account_receivable_id.id,
        # This is ID for default bank account, already registered
        'partner_bank_id': 1,
        'payment_term_id': odoo.env.ref("account.account_payment_term_net").id,
    })

    InvoiceLine = odoo.env["account.invoice.line"]
    InvoiceLine.create({
        "invoice_id": invoice_id,
        "name": "A basic product",
        "quantity": 6,
        "price_unit": 100.0,
        # Not sure about this one:
        "uom_id": 1,
        # No tax
        "invoice_line_tax_ids": [],
        'journal_id': 1,
        'account_id': customer.property_account_receivable_id.id,
    })

    inv = Invoice.browse([invoice_id])
    print("Before validating:", inv.state)

    inv.action_invoice_open()

    inv = Invoice.browse([invoice_id])
    print("After validating:", inv.state)


    # result
    # Before validating: draft
    # After validating: paid

    # fix

cust_invoices_journal = odoo.env["account.journal"].browse([1])
# [...]
invoice_id = Invoice.create({
    # [...]
    'journal_id': cust_invoices_journal.id,
    'account_id': customer.property_account_receivable_id.id,
    # [...]
})
# [...]
InvoiceLine.create({
    # [...]
    'account_id': cust_invoices_journal.default_credit_account_id.id,
    # [...]
})