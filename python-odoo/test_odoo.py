# Script to create invoices from csv file containing invoice details
#

import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os,random
import logging
from xlrd import open_workbook
from random import randint

_logger = logging.getLogger(__name__)

"""
Create Invoice form Daily sales csv file
"""
# Command line ArgumentHandling
"""
try:
    import argparse

    parser = argparse.ArgumentParser(description='Script for creating Payroll from csv file')
    parser.add_argument('-w', '--xlsfile', help='e.g -w xlsfile.csv', required=True)
    args = vars(parser.parse_args())
except ImportError:
    parser = None

WBFILE = args['xlsfile']
"""
try:
    db = 'SMARTACQUADB'
    username = 'ebikonpearl@gmail.com'
    password = 'licia5555'
    port = '8081'
    host = 'localhost'
    url = 'http://%s:%s' % (host, port)
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % (url))
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})

    assert uid,'com.login failed'
    version = common.version()
    print "odoo version ",version['server_version']
    assert version['server_version'] == '12.0','Server not 12.0'
except Exception, e:
    raise


TODAY = datetime.now().strftime('%d.%m.%Y')
DATAFOLDER = 'data'

def create_vendor(pname, phone,email):
    try:
        p_name = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['name', '=', pname]]], \
                                       {'fields': ['id']})
            # Create Name on Teller as Customer if not in DB
        if not p_name:
            p_n = models.execute_kw(db, uid, password, 'res.partner', 'create', \
                    [{'name': pname, 'customer': False, 'supplier': True, 'phone': phone,'email': email}])
            assert p_n, 'Vendor Creation Fails'
        else:
            p_n = p_name[0]['id']
        return p_n
    except Exception, e:
        raise

def update_invoice(invoice_id):
    try:
        lines = [
                        (0, 0,
                         {
                             'product_id': product_id,
                             'quantity': qty,
                             'account_id': 2,
                             'name': prodname,
                             'price_unit': price_unit,
                             'uom_id': 1
                         }
                         )
                    ]
            
        inv_upd = models.execute_kw(db, uid, password, 'account.invoice', 'write', [[invoice_id], {'invoice_line_ids':lines}])
        assert inv_upd,'Invoice Update fails'
        return inv_upd
    except Exception, e:
        print str(e)
        raise

def get_invoice(type):
    try:
        inv_obj = models.execute_kw(db, uid, password, 'account.invoice', 'search_read', \
                         [[['type', '=',type]]],{'fields': ['id', 'invoice_line_ids']}) 
        assert inv_obj,"inv obj not good"
        return inv_obj
    
    except Exception, e:
        print str(e)
        raise

def get_product_ids(prodname):
    prod_obj = models.execute_kw(db, uid, password, 'product.product', 'search_read', \
                                                 [[['name', '=', prodname]]],
                                                 {'fields': ['id', 'property_account_expense_id']})
    assert prod_obj,"not valid product in get prod ids"
    
    product_id = prod_obj[0]['id']
    prod_acct_exp_id =  prod_obj[0]['property_account_expense_id']
    print "product id: ",product_id,"product_acc_exp_id",prod_acct_exp_id
    
    return [product_id,prod_acct_exp_id]

def create_product(prodname):
    try:
        
        print 'product name',prodname
        
        prod_obj = models.execute_kw(db, uid, password, 'product.product', 'search_read', \
                 [[['name', '=', prodname]]],{'fields': ['id']})
        if prod_obj:
            product_id = prod_obj[0]['id']
        else:
            product_id = models.execute_kw(db, uid, password, 'product.product', 'create', [{'name': prodname}])
    
        assert product_id, 'not valid product_id'
        return product_id
    except Exception, e:
        print str(e)
        raise


invoice_type = 'in_invoice'
total_inv = 0
account_bill = loc = None
vendor_obj = models.execute_kw(db, uid, password, 'res.partner', 'search_read', \
     [[['name', '=', 'Sundry Vendor']]], {'fields': ['id', 'name','phone','mobile','email','website','supplier','customer','barcode','user_id']})
print vendor_obj;
id = vendor_obj[0]['id']
print id
false=False
upd = models.execute_kw(db, uid, password, 'res.partner', 'write', [[id], {
    'mobile': "07067647125",'phone':false
}])
print "update id", upd
vendor_obj = models.execute_kw(db, uid, password, 'res.partner', 'search_read', \
     [[['name', '=', 'Sundry Vendor']]], {'fields': ['id', 'name','phone','mobile','email','website','supplier','customer','barcode','user_id']})
print vendor_obj;
vendor_obj = models.execute_kw(db, uid, password, 'res.partner', 'search_read', \
     [[['supplier', '=', True]]], {'fields': ['id', 'name','phone','mobile','email','website','supplier','customer','barcode','user_id']})
#for v in vendor_obj:
#    print(v['name'],v['phone'],v['email'])
journal_obj = models.execute_kw(db, uid, password, 'account.journal', 'search_read', [[['id', '>', 0]]], {'fields': ['id','name','type']}) 
inv_obj = models.execute_kw(db, uid, password, 'account.invoice', 'search_read', [[['id', '>', 0]]], {'fields': ['id','name','type','invoice_line_ids','number','reference','state','partner_id']}) 
# for inv in inv_obj:
#    print inv

    
#print journal_obj
