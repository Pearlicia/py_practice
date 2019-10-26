
import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os,random
import logging
from xlrd import open_workbook
from random import randint

_logger = logging.getLogger(__name__)

# Command line ArgumentHandling
try:
    import argparse

    parser = argparse.ArgumentParser(description='Script for creating Payroll from csv file')
    parser.add_argument('-w', '--xlsfile', help='e.g -w xlsfile.csv', required=True)
    args = vars(parser.parse_args())
except ImportError:
    parser = None

WBFILE = args['xlsfile']


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

def create_product(prod_name):
    try:
        prod_obj = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                         [[['name', '=', prod_name]]], {'fields': ['id', 'name', 'property_account_expense_id']})
        if not prod_obj:
            # create product
            p_n = models.execute_kw(db, uid, password, 'product.product', 'create', \
                    [{ 'name': prod_name }])
            assert p_n, 'prod create failed'
            print prod_name, " created!!!"
            return p_n
        else:
            print "Product ", prod_name, " Exists"
            return prod_obj[0]['id']
    except Exception, e:
        raise

def csvextract(xlsfile):
    # extract cvs from xls file
    wb = open_workbook(xlsfile)

    print ('SHEETS IN SALES FILE')

    for i in range(0, wb.nsheets - 1):
        sheet = wb.sheet_by_index(i)
        # print (sheet.name)

        path = DATAFOLDER + '/%s.csv'
        with open(path % (sheet.name.replace(" ", "") ), "w") as file:
            writer = csv.writer(file, delimiter=",", quotechar='"', \
                  quoting=csv.QUOTE_ALL, skipinitialspace=True)

            header = [cell.value for cell in sheet.row(0)]
            writer.writerow(header)

            for row_idx in range(1, sheet.nrows):
                row = [int(cell.value) if isinstance(cell.value, float) else cell.value
                       for cell in sheet.row(row_idx)]
                for i in range(len(row)):
                  if isinstance(row[i],basestring):
                    row[i] = row[i].encode('ascii','ignore')
                writer.writerow(row)

DATAFOLDER = 'data'
WORKSHEET = 'MAIN'
invoice_type = 'in_invoice'
total_inv = 0
account_bill = loc = None
# the csvextract function extracts into respective worksheets.csv
csvextract(WBFILE)
EXPFILE = 'data/' + WORKSHEET + '.csv'



with open(EXPFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            prodname = row['PRODUCT'].upper()
            assert prodname,"No PRODUCT - probably end of file"

            product_id = create_product(prodname)
            assert product_id,'not valid produt'

        except Exception, e:
            print 'Product Creation Error.'
            raise

