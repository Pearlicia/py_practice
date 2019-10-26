# Script to create invoices from csv file containing invoice details
#
# for python3
import xmlrpc.client as xmlrpclib
# import xmlrpclib
from datetime import datetime
from datetime import date
import csv
import os
import random
import logging
from xlrd import open_workbook
from random import randint
from utils import create_product, create_vendor, csvextract,db,uid,password,models

_logger = logging.getLogger(__name__)

"""
Create Invoice form Daily sales csv file
"""
# Command line ArgumentHandling
try:
    import argparse

    parser = argparse.ArgumentParser(
        description='Script for creating Payroll from csv file')
    parser.add_argument('-w', '--xlsfile',
                        help='e.g -w xlsfile.csv', required=True)
    args = vars(parser.parse_args())
except ImportError:
    parser = None

WBFILE = args['xlsfile']

invoice_type = 'in_invoice'
total_inv = 0
account_bill = loc = None
WORKSHEET = 'MAIN'
EXPFILE = WBFILE

from pathlib import Path

filename = Path(EXPFILE).stem

GROUP = filename
acct_pay_name = filename +' Account Payable'
sn = 0
with open(EXPFILE, encoding='utf-8',errors='ignore') as csvfile:
    line = csv.DictReader(csvfile)

    
    for row in line:
        try:
            sn = sn + 1
            print(sn,row)
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
            price_unit = price_unit.replace(',','')
            qty = row['QTY']
            assert qty,"No qty"
            qty = qty.replace(',','')
            vendor = row['VENDOR']
            if 'SUNDRY' in vendor:
                vendor = GROUP +' '+ vendor
            assert vendor,"No VENDOR"
            
            product_id = create_product(prodname)
            assert product_id,'not valid produt'

            vendor_id = create_vendor(vendor)
            assert vendor_id,'not valid vendor'
            

            invoice_name = GROUP + '/'+ 'BILL/' + str(vendor_id) + '/' + e_date + '/' + str(random.random()*1000000)

            # Use Purchase Journal
            journal_obj = models.execute_kw(db, uid, password, 'account.journal', 'search_read', \
                                  [[['type', '=', 'purchase']]], {'fields': ['id']}) 
            
            assert journal_obj,'not valid journal_obj'
            journal_id = journal_obj[0]['id']
            print( 'journal id',journal_id)
            acct_pay_obj = models.execute_kw(db, uid, password, 'account.account', 'search_read', \
                                  [[['name', '=', acct_pay_name]]], {'fields': ['id']}) 
            # 24 is for expenses id in invoice lines
            account_id = 24
            # 13 is for account payable id
            account_payable_id = acct_pay_obj[0]['id']
            ref_name = GROUP + '-'+vendor + '-' + description + '-' + qty + price_unit + '-' + e_date

            inv_obj = models.execute_kw(db, uid, password, 'account.invoice', 'search_read', \
                                  [[['reference', '=', ref_name]]], {'fields': ['id']}) 

            if inv_obj:
                print( 'invoice for ',description,' exists')
                continue

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
            print( 'Expense  bill for',ref_name,' created successfully!!!')
        except Exception as e:
            print( 'Bill Creation Error.',str(e))
            raise
