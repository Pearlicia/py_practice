# We list all Odoo customers
from __future__ import print_function
import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os,random
import logging
from xlrd import open_workbook
from random import randint

_logger = logging.getLogger(__name__)

try:
    db = 'SMARTDB'
    username = 'admin'
    password = 'Adm1n'
    port = '8081'
    host = 'localhost'
    url = 'http://%s:%s' % (host, port)
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % (url))
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})

    assert uid, 'com.login failed'
    version = common.version()
    # print 'odoo version', version
    # assert version['server_version'] == '10.0','Server not 10.0'
except Exception, e:
    raise



def list_customers():
    try:
        cust = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                         [[['supplier', '=', True]]], {'fields': ['id', 'name', 'phone','mobile','email','barcode']})
        return cust
    except Exception, e:
        raise


customers = list_customers()

header = "Name,Phone,Mobile,Email,Barcode".upper()

print(header)
for customer in customers:
    if not customer['name']:
        continue
    cmob = customer['mobile'] if customer['mobile']  else ""
    cphone = customer['phone'] if customer['phone']  else ""
    cemail = customer['email'] if customer['email']  else ""
    cbar = customer['barcode'] if customer['barcode']  else ""
    print(customer['name'],cphone,cmob,cemail,cbar,sep=",")
