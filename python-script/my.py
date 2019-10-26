import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os,random
import logging
from random import randint

_logger = logging.getLogger(__name__)


try:
    db = 'SAALDB'
    username = 'feliciaebikon@gmail.com'
    password = 'felicity12'
    port = '8069'
    host = 'localhost'
    url = "http://localhost:8069"
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % (url))
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})


reader = csv.reader(open('/Users/admin/Desktop/Development/Odoo12/src/odoo/saalcsv.csv', 'rb'))

# SAMPLE CODE

for row in reader:
   print row[1]
#     invoice_template = {
#         'partner_id' : customer.id,
#         'state': 'draft',
#         # This is ID for "Customers Invoices" journal
#          'journal_id': cust_invoices_journal.id,
         
#          #'journal_id': 1,
#          'account_id': customer.property_account_receivable_id.id,
#          # This is ID for default bank account, already registered
#          'partner_bank_id': 1,
#          'payment_term_id': odoo.env.ref("account.account_payment_term_net").id,
#      })

# template_id = models.execute_kw(db, uid,password, 'invoice.template','create',invoice_template)


#  InvoiceLine = odoo.env["account.invoice.line"]

    invoice_line = {
        "invoice": invoice,
        "invoice_id": invoice_id,
        "product_id": product_id,
        "name": product_name,
        "quantity": product_quantity,
        "price_unit": product_price,
        # Not sure about this one:
        "uom_id": 1,
         # No tax
        "invoice_line_tax_ids": [odoo_tax_id],
        'journal_id': 1,
        'account_id': cust_invoices_journal.default_credit_account_id.id,
    }

    result = models.execute_kw(db,uid,password,'account.invoice.line','create'invoice_line)

    # Product creation
    product_product = {
        "default_code": product_ref,
        "name": product_name,
        'product_tmpl_id': product_id,
        #'default_code': row[0],
        "list_price": product_price
        'active': True
    }

    product_id = models.execute_kw(db,uid,password,'product.product','create',product_product)

 

# Invoice creation

invoice_invoice = {
    "partner_id": partner_id,
    "account_id": odoo_invoice_account_id
}

invoice_id = models.execute_kw(db,uid,password,'account.invoice','create',invoice_invoice)


invoice = models.execute_kw(db,uid,password,'account.invoice','read',invoice_id)







# Partner = odoo.env["res.partner"]
#     # This partner already exists in DB
#     customer = Partner.browse([22])


# Invoice = odoo.env["account.invoice"]
#     invoice_id = Invoice.create({
#         'partner_id' : customer.id,
#         'state': 'draft',
#         # This is ID for "Customers Invoices" journal
#         'journal_id': cust_invoices_journal.id,
         
#         #'journal_id': 1,
#         'account_id': customer.property_account_receivable_id.id,
#         # This is ID for default bank account, already registered
#         'partner_bank_id': 1,
#         'payment_term_id': odoo.env.ref("account.account_payment_term_net").id,
#     })

#     InvoiceLine = odoo.env["account.invoice.line"]
#     InvoiceLine.create({
#         "invoice_id": invoice_id,
#         "name": "A basic product",
#         "quantity": 6,
#         "price_unit": 100.0,
#         # Not sure about this one:
#         "uom_id": 1,
#         # No tax
#         "invoice_line_tax_ids": [],
#         'journal_id': 1,
#         'account_id': cust_invoices_journal.default_credit_account_id.id,
       
#     })

#     inv = Invoice.browse([invoice_id])
#     print("Before validating:", inv.state)

#     inv.action_invoice_open()

#     inv = Invoice.browse([invoice_id])
#     print("After validating:", inv.state)



# cust_invoices_journal = odoo.env["account.journal"].browse([1])


