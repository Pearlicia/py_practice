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
Create Invoice form Daily sales xls file
"""
# Command line ArgumentHandling
try:
    import argparse

    parser = argparse.ArgumentParser(description='Script for creating Payroll from csv file')
    parser.add_argument('-w', '--xlsfile', help='e.g -w xlsfile.xls', required=True)
    args = vars(parser.parse_args())
except ImportError:
    parser = None

WBFILE = args['xlsfile']

try:
    db = 'FIDODB'
    username = 'admin'
    password = 'YesAdmin'
    port = '8070'
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
              row = [int(cell.value) if isinstance(cell.value, float) else cell.value for cell in sheet.row(row_idx)]
              for i in range(len(row)):
                if isinstance(row[i],basestring):
                  row[i] = row[i].encode('ascii','ignore')
              writer.writerow(row)

def create_partner(pname, phone,email):
    try:
        p_name = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['name', '=', pname]]], \
                                       {'fields': ['id']})
            # Create Name on Teller as Customer if not in DB
        if not p_name:
            p_n = models.execute_kw(db, uid, password, 'res.partner', 'create', \
                    [{'name': pname, 'customer': True, 'supplier': False, 'phone': phone,'email': email}])
            assert p_n, 'Customer Creation Fails'
        else:
            p_n = p_name[0]['id']
        return p_n
    except Exception, e:
        raise
    
def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""
    
def get_bank_id(bank):
    try:
        if 'IBTC' in bank:
            id = 1
        elif 'STERL' in bank:
            id = 2
        elif 'GTB' in bank:
            id = 3
        elif 'FCMB' in bank:
            id = 4
        elif 'FIDEL' in bank:
           id = 5
        elif 'ACCESS' in bank:
           id = 6
        else:
            id = 10
        return id
    except Exception, e:
        raise

def get_team_id(location):
    try:
        
        if location == 'YENEGWE':
            teamid = 6
        elif location == 'SWALI':
            teamid = 8
        elif location == 'KPANSIA':
            teamid = 4
        elif location == 'OKUTUKUTU':
            teamid = 3
        elif location == 'OBUNNA':
            teamid = 5
        else:
            teamid = 1
        return teamid
    except Exception, e:
        raise

def update_invoice(invoice_id):
    try:
        lines = [
                (0, 0,
                 {
                     'product_id': product_id,
                     'quantity': qty,
                     'name': prodname,
                     'account_id': prod_acct_id,
                     'price_unit': price_unit,
                     'uom_id': 1
                 }
                 )
            ]
            
        inv_upd = models.execute_kw(db, uid, password, 'account.invoice', 'write', [[invoice_id], {'invoice_line_ids':lines}])
        assert inv_upd,'Invoice Update fails'
        return inv_upd
    except Exception, e:
        raise

# We use WBFILE below to preserve date of transaction
try:
    if 'xls' in WBFILE:
        tdate = find_between(WBFILE, ' ', ".xls")
        print tdate
        # the INVOICE csv file in data dir extracted from xls file
        INVOICE_FILE = 'data/INVOICE ' + tdate + '.csv'
        csvextract(WBFILE)
    elif 'csv' in WBFILE:
        tdate = find_between(WBFILE, ' ', ".csv")
        INVOICE_FILE = WBFILE
    else:
        assert tdate,'File needs to be csv or xls'
except Exception, e:
    raise

tdate = str(tdate).replace('.', '/')
if ('/' not in str(tdate)) and ('.' not in str(tdate)):
    print('I am in ordinal loop')
    ddt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(tdate) - 2)
    e_date = ddt.strftime('%Y-%m-%d')
    e_date2 = ddt.strftime('%Y-%m-%d-%H.%M.%S.%f')
else:
    e_date = (datetime.strptime(tdate, '%d/%m/%Y')).strftime('%Y-%m-%d')
    e_date2 = (datetime.strptime(tdate, '%d/%m/%Y')).strftime('%Y-%m-%d-%H.%M.%S.%f')
invoice_type = 'out_invoice'
total_inv = 0
with open(INVOICE_FILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            assert e_date,"wrong date"
            if row.has_key('PHONE'):
                phone = row['PHONE']
            else:
                phone = ""
            if row.has_key('EMAIL'):
                email = row['EMAIL']
            else: 
                email = ""
                    
            if row.has_key('QTY'):
                qty = row['QTY']
            assert qty,"No qty"
            if row.has_key('RATE3'):
                price_unit = row['RATE3']
            elif row.has_key('RATE'):
                price_unit = row['RATE']
                
            assert price_unit,'No Rate'
            prodname = row['PRODUCT'].strip().upper()
            assert prodname,"no product"
            if prodname == 'INCENTIVE-PUREWATER':
                continue
            if prodname == 'PURE WATER':
                prodname = 'PUREWATER'
            if prodname == 'PUERWATER':
                prodname = 'PUREWATER'
            if prodname == '50CL BOTTLE':
                prodname = 'CRATE50CL'
            if prodname == '50CL CRATE':
                prodname = 'CRATE50CL'
            if prodname == '50CLWATER':
                prodname = 'CRATE50CL'
            if prodname == '50cl Bottle':
                prodname = 'CRATE50CL'
            if prodname == '50 CL CRATE':
                prodname = 'CRATE50CL'
            if prodname == '60CL BOTTLE':
                prodname = 'CRATE60CL'
            if prodname == '60cl Bottle':
                prodname = 'CRATE60CL'
            if prodname == '75CL BOTTLE':
                prodname = 'CRATE75CL'
            if prodname == '75CL CRATE':
                prodname = 'CRATE75CL'
                            
            prod_obj = models.execute_kw(db, uid, password, 'product.product', 'search_read', \
                                  [[['name', '=', prodname]]], {'fields': ['id','property_account_income_id']}) 
            print 'product:',prodname
            assert prod_obj,'not valid prod_obj'
            product_id = prod_obj[0]['id']
            prod_acct_id = prod_obj[0]['property_account_income_id'][0]
                        
            if not row['CUSTOMER NAME']:
                upd_id = update_invoice(invoice_id)
                continue

            partner = row['CUSTOMER NAME'].strip().upper()
                        
            if row.has_key('LOCATION'):
                location = row['LOCATION']
            assert location,'NO LOCATION'

            partner_obj = models.execute_kw(db, uid, password, 'res.partner', 'search_read', \
                                  [[['name', '=', partner]]], {'fields': ['id']})
            
            print "partner: ",partner
            if not partner_obj:
                partner_id = create_partner(partner,phone,email)
            else:
                partner_id = partner_obj[0]['id']
            print "Partner id: ",partner_id
            
            assert partner_id,"Not valid Partner"
            
            
            bank = row['BANK']
            partner_bank_id = get_bank_id(bank)
            if row.has_key('EMAIL'):
                email = row['EMAIL']
            else:
                email = ""
            if row.has_key('PHONE'):
                phone = row['PHONE']
            else:
                phone=""
            
            invoice_name = 'FIDO_INVOICE/' + str(partner_id) + str(random.random()*1000000)+ '/' + e_date2
            # account_invoice_obj = env['account.invoice']
            # Use Sales Journal
            journal_obj = models.execute_kw(db, uid, password, 'account.journal', 'search_read', \
                                  [[['type', '=', 'sale']]], {'fields': ['id']}) 
                       
            assert journal_obj,'not valid journal_obj'
            journal_id = journal_obj[0]['id']
            print 'journal id',journal_id
            account_id = 7
            teamid = get_team_id(location)
                            
            assert teamid,"no location"
                
            payment_term_id = 1
            date_invoice = e_date
            print date_invoice
            # Product info
                
            lines = [
                (0, 0,
                 {
                     'product_id': product_id,
                     'quantity': qty,
                     'name': prodname,
                     'account_id': prod_acct_id,
                     'price_unit': price_unit,
                     'uom_id': 1
                 }
                 )
            ]
            print('Creating Invoice for Partner ',partner, 'product ',prodname,' ....')
            
            invoice_id = models.execute_kw(db, uid, password, 'account.invoice', 'create', \
                                                                  [{'name': invoice_name,
                                                                    'reference_type': "none",
                                                                    'payment_term_id': payment_term_id,
                                                                    'journal_id': journal_id,
                                                                    'partner_id': partner_id,
                                                                    'partner_bank_id': partner_bank_id,
                                                                    'date_invoice': date_invoice,
                                                                    'account_id': account_id,
                                                                    'team_id': teamid,
                                                                    'type': invoice_type,
                                                                    'invoice_line_ids': lines}])
            assert invoice_id, 'Invoice Creation Failed'
        
            
            total_inv = total_inv + (float(qty)*float(price_unit))
            
            print 'Invoice for ', partner, ' created successfully!!!'
            # Validate Invoice
            #account_invoice_customer0.action_invoice_open()
            # Check that invoice is open
            #assert account_invoice_customer0.state == 'open','Invoice not properly validated'
        except Exception, e:
            print 'Invoice Creation Error.',str(e)
            raise
        
