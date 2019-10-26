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

    assert uid,'com.login failed'
    version = common.version()
    # assert version['server_version'] == '10.0','Server not 10.0'
except Exception, e:
    raise


TODAY = datetime.now().strftime('%d.%m.%Y')
DATAFOLDER = 'data'

# Extract Sheets into data/sheetname-dd.mm.YY.csv
def csvextract(xlsfile):
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


def create_vendor(pname):
    try:
        p_name = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['name', '=', pname]]], \
                                       {'fields': ['id']})
            # Create Name on Teller as Customer if not in DB
        if not p_name:
            p_n = models.execute_kw(db, uid, password, 'res.partner', 'create', \
                    [{'name': pname, 'customer': True, 'supplier': True}])
            assert p_n, 'Vendor Creation Fails'
        else:
            p_n = p_name[0]['id']
        return p_n
    except Exception, e:
        raise

def create_product(prodname):
    try:

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
WORKSHEET = 'MAIN'
csvextract(WBFILE)
EXPFILE = 'data/' + WORKSHEET + '.csv'

with open(EXPFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            prodname = row['PRODUCT'].upper()
            assert prodname,"No PRDUCT - probably end of file"

            description = row['DESCRIPTION'].upper()
            assert description,"No DESCRIPTION - probably end of file"

            e_date = row['DATE']
            assert e_date,"No date - probably end of file"
            if ('/' not in str(e_date)) and ('.' not in str(e_date)):
                ddt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(e_date) - 2)
                e_date = ddt.strftime('%Y-%m-%d')
            else:
                e_date = (datetime.strptime(e_date, '%d/%m/%Y')).strftime('%Y-%m-%d')


            price_unit = row['RATE']
            assert price_unit,"No Rate"
            qty = row['QTY']
            assert qty,"No qty"
            vendor = row['VENDOR']
            assert vendor,"No VENDOR"

            product_id = create_product(prodname)
            assert product_id,'not valid produt'

            vendor_id = create_vendor(vendor)
            assert vendor_id,'not valid vendor'


            invoice_name = 'BILL/' + str(vendor_id) + '/' + e_date + '/' + str(random.random()*1000000)

            # Use Purchase Journal
            journal_obj = models.execute_kw(db, uid, password, 'account.journal', 'search_read', \
                                  [[['type', '=', 'purchase']]], {'fields': ['id']})

            assert journal_obj,'not valid journal_obj'
            journal_id = journal_obj[0]['id']
            print 'journal id',journal_id
            # 24 is for expenses id in invoice lines
            account_id = 24
            # 13 is for account payable id
            account_payable_id = 13
            ref_name = vendor + '-' + description + '-' + qty + price_unit + '-' + e_date

            inv_obj = models.execute_kw(db, uid, password, 'account.invoice', 'search_read', \
                                  [[['reference', '=', ref_name]]], {'fields': ['id']})

            if inv_obj:
                print 'invoice for ',description,' exists'
                # continue
                
                # Product info                
            lines = [
                        (0, 0,
                         {
                             'product_id': product_id,
                             'quantity': qty,
                             'account_id': account_id,
                             'name': description,
                             'price_unit': price_unit,
                             'uom_id': 1
                         }
                         )
                    ]
            account_bill = models.execute_kw(db, uid, password, 'account.invoice', 'create', \
                                        [{'name': invoice_name,
                                         'journal_id': journal_id,
                                         'reference': ref_name,
                                         'partner_id': vendor_id,
                                         'date_invoice': e_date,
                                         'date_due': e_date,
                                         'account_id': account_payable_id,
                                         'type': invoice_type,
                                         'invoice_line_ids': lines}])
            assert account_bill, 'Bill Creation Failed'
            print 'Expense  bill for',ref_name,' created successfully!!!'
        except Exception, e:
            print 'Bill Creation Error.',str(e)
            raise

