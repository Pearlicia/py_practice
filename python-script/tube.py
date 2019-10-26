import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os,random
import logging
from xlrd import open_workbook
from random import randint

_logger = logging.getLogger(__name__)


try:
    dbname = 'SAALDB'
    username = 'feliciaebikon@gmail.com'
    pwd = 'felicity12'
    port = '8069'
    host = 'localhost'
    url = "http://localhost:8069"
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % (url))
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(dbname, username, pwd, {})

    assert uid,'com.login failed'
    version = common.version()
    # assert version['server_version'] == '10.0','Server not 10.0'
except Exception, e:
    raise

TODAY = datetime.now().strftime('%d.%m.%Y')
DATAFOLDER = 'data'


#sock_common = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/common")

#uid = sock_common.login(dbname, username, pwd)

#sock = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/object")

reader = csv.reader(open('saalcsv.csv', 'rb'))
for row in reader:
    print row[1]
    product_template = {
        'name': row[1],
        'standard_price': row[2],
        'list_price': row[2],
        'mes_type': 'fixed',
        'uom_id': 1,
        'uom_po_id': 1,
        'type': 'product',
        'procure_method': 'make_to_stock',
        'cost_method': 'standard',
        'categ_id': 1
    }

    template_id = sock.execute(dbname, uid,pwd, 'product.template','create',product_template)

    product_product = {
        'product_tmpl_id': product_id,
        'default_code': row[0],
        'active': True
    }

    product_id = sock.execute(dbname,uid,pwd,'product.product','create',product_product)

    
