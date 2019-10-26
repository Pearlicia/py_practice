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

try:
    db = 'db1'
    username = 'admin2'
    password = 'a'
    port = '8069'
    host = 'localhost'
    url = 'http://%s:%s' % (host, port)
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % (url))
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})

    assert uid, 'com.login failed'
    version = common.version()
    # assert version['server_version'] == '10.0','Server not 10.0'
except Exception as e:
    raise


def csvextract(xlsfile):
    wb = open_workbook(xlsfile)

    print('SHEETS IN SALES FILE')

    for i in range(0, wb.nsheets - 1):
        sheet = wb.sheet_by_index(i)
        # print (sheet.name)

        path = DATAFOLDER + '/%s.csv'
        with open(path % (sheet.name.replace(" ", "")), "w") as file:
            writer = csv.writer(file, delimiter=",", quotechar='"',
                                quoting=csv.QUOTE_ALL, skipinitialspace=True)

            header = [cell.value for cell in sheet.row(0)]
            writer.writerow(header)

            for row_idx in range(1, sheet.nrows):
                row = [int(cell.value) if isinstance(cell.value, float) else cell.value
                       for cell in sheet.row(row_idx)]
                for i in range(len(row)):
                    if isinstance(row[i], basestring):
                        row[i] = row[i].encode('ascii', 'ignore')
                writer.writerow(row)


def create_vendor(pname):
    try:
        p_name = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['name', '=', pname]]],
                                   {'fields': ['id']})
        # Create Name on Teller as Customer if not in DB
        if not p_name:
            p_n = models.execute_kw(db, uid, password, 'res.partner', 'create',
                                    [{'name': pname, 'customer': True, 'supplier': True}])
            assert p_n, 'Vendor Creation Fails'
        else:
            p_n = p_name[0]['id']
        return p_n
    except Exception as e:
        raise


def create_product(prodname):
    try:

        prod_obj = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                                     [[['name', '=', prodname]]], {'fields': ['id']})
        if prod_obj:
            product_id = prod_obj[0]['id']
        else:
            product_id = models.execute_kw(
                db, uid, password, 'product.product', 'create', [{'name': prodname}])

        assert product_id, 'not valid product_id'
        return product_id
    except Exception as e:
        print(str(e))
        raise
