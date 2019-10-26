
import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os,random
import uuid
import logging
from xlrd import open_workbook
from random import randint

_logger = logging.getLogger(__name__)

# Command line ArgumentHandling
try:
    import argparse

    parser = argparse.ArgumentParser(description='Script for creating Payroll from csv file')
    parser.add_argument('-f', '--csvfile', help='e.g -f customer.csv', required=True)
    args = vars(parser.parse_args())
except ImportError:
    parser = None

WBFILE = args['csvfile']


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
    print 'odoo version', version
    # assert version['server_version'] == '10.0','Server not 10.0'
except Exception, e:
    raise

TODAY = datetime.now().strftime('%d.%m.%Y')

# cycle through all products and update them

def create_customer(cname,mobile,phone,email,barcode):
    try:
        cust_obj = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
          [[['customer', '=', True]]], {'fields': ['id', 'name', 'phone','mobile','email','barcode']})
        # cust_obj = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
        #  [[['customer', '=', True],['supplier','=',True]]], {'fields': ['id', 'name', 'phone','mobile','email','barcode']})
        if not cust_obj::
            # create product
            p_n = models.execute_kw(db, uid, password, 'res_partner', 'create', \
                    [{ 'name': cname,'phone':phone,'mobile':mobile,'email':email,'barcode':barcode }])
            assert p_n, 'prod create failed'
            print cname, " created!!!"
            return p_n
        else:
            print "Customer ", cname, " Exists"
            return cust_obj[0]['id']
    except Exception, e:
        raise

# the csvextract function extracts into respective worksheets.csv



with open(WBFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            if row.has_key('NAME'):
                cname = row['NAME']
            assert cname,"No name"
            mobile = row['MOBILE']
            assert mobile,"No mobile"
            phone = row['PHONE']
            assert phone,"No phone"
            email = row['EMAIL']
            assert email,"No email"
            if row.has_key('BARCODE'):
                barcode = row['BARCODE']
            if not barcode:
                barcode = cname + uuid.uuid4().hex[:6].upper()+ mobile + phone + email
            # create customer if not exist
            cust_id = create_customer(cname,mobile,phone,email,barcode)
            assert cust_id,"customer creation failed"
            print('Customer',cname, " created")

        except Exception, e:
            print 'Product Creation Error.'
            raise

