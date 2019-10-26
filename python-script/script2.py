
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
    db = 'SAALDB'
    username = 'feliciaebikon@gmail.com'
    password = 'felicity21'
    port = '8069'
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
        with open(path % (sheet.name.replace(" ", "") + ' ' + tdate), "w") as file:
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

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

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
            
        inv_upd = models.execute_kw(db, uid, password, 'account.invoice', 'write', [[invoice_id], {'invoice_line_ids':lin$
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

if 'xls' in WBFILE:
    tdate = find_between(WBFILE, ' ', ".xls")
    # the EXPENSES csv file in data dir extracted from xls file
    EXPFILE = 'data/EXPENSES ' + tdate + '.csv'
    csvextract(WBFILE)

elif 'csv' in WBFILE:
    tdate = find_between(WBFILE, ' ', ".csv")
    EXPFILE = WBFILE
else:
    assert tdate,'file may not be .xls or .csv'


tdate = str(tdate).replace('.', '/')
if ('/' not in str(tdate)) and ('.' not in str(tdate)):
    ddt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(tdate) - 2)
    e_date = ddt.strftime('%Y-%m-%d')
else:
    e_date = (datetime.strptime(tdate, '%d/%m/%Y')).strftime('%Y-%m-%d')
print ('tdate: ' + str(tdate) + ' = ' + str(e_date))
with open(EXPFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
           
            assert e_date,"No good date"
            
            prodname = row['TITLE'].upper()
            assert prodname,"No Title - probably end of file"    
            
            price_unit = row['RATE']
            assert price_unit,"No Rate"
            qty = row['QTY']
            assert qty,"No qty"
            
            location = row['LOCATION']
            assert location,"No location field"
            location = location + ' ' + str(e_date)
                
            
            product_id = create_product(prodname)
            assert product_id,'not valid produt'

             vendor_obj = models.execute_kw(db, uid, password, 'res.partner', 'search_read', \
                                                    [[['name', '=', 'Sundry Vendor']]],
                                                    {'fields': ['id', 'name']})
            vendor_id = vendor_obj[0]['id']
            assert vendor_id,'no vendor_id'

            invoice_name = 'BILL/' + str(vendor_id) + '/' + e_date + '/' + str(random.random()*1000000)

            # account_invoice_obj = env['account.invoice']
            # Use Sales Journal
            journal_obj = models.execute_kw(db, uid, password, 'account.journal', 'search_read', \
                                  [[['type', '=', 'purchase']]], {'fields': ['id']}) 
            
           
            assert journal_obj,'not valid journal_obj'
            journal_id = journal_obj[0]['id']
            print 'journal id',journal_id
            account_id = 13
            prod_account_id = get_product_ids(prodname)[1]
            print "prod account_id",prod_account_id
            # Product info                
            lines = [
                        (0, 0,
                         {
                             'product_id': product_id,
                             'quantity': qty,
                             'account_id': account_id,
                             'name': prodname,
                             'price_unit': price_unit,
                             'uom_id': 1
                         }
                         )
                    ]
            if loc != location:
                
                account_bill = models.execute_kw(db, uid, password, 'account.invoice', 'create', \
                                                   [{'name': invoice_name,

                                                        'journal_id': journal_id,
                                                        
                                                        'reference': location,
                                                        'partner_id': vendor_id,
                                                        'date_invoice': e_date,
                                                        'date_due': e_date,
                                                        'account_id': account_id,
                                                        'type': invoice_type,
                                                        'invoice_line_ids': lines}])
                assert account_bill, 'Bill Creation Failed'
                loc = location
                print ('bill Created')
            else:
                
                account_upd = update_invoice(account_bill)
                assert account_upd,'bill not updated'

            print('Creating bill for DAILY EXPENSES product ',prodname,' ....')

            print 'Invoice for EXPENSE  created successfully!!!'
            # Validate Invoice
            #account_invoice_customer0.action_invoice_open()
            # Check that invoice is open
            #assert account_invoice_customer0.state == 'open','Invoice not properly validated'
        except Exception, e:
            print 'Bill Creation Error.',str(e)
            raise
print('Total Invoiced',total_inv)


           


