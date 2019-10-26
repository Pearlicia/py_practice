


# Configuration
url = "http://localhost:8069"
db = "SAALDB"
username = "feliciaebikon@gmail.com"
password = "felicity12"

import xmlrpclib

# Logging in
common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

uid = common.authenticate(db, username, password, {})

# Calling methods

models = xmlrpcli.ServerProxy('{}/xmlrpc/2/object'.format(url))
models.execute_kw(db, uid, password,
    'res.partner', 'check_access_rights',
    ['read'], {'raise_exception': False})

# List records

models.execute_kw(db, uid, password,
    'res.partner', 'search',
    [[['is_company', '=', True], ['customer', '=', True]]])

# Pagination / search limit

models.execute_kw(db, uid, password,
    'res.partner', 'search',
    [[['is_company', '=', True], ['customer', '=', True]]],
    {'offset': 10, 'limit': 5})


# Count records

models.execute_kw(db, uid, password,
    'res.partner', 'search_count',
    [[['is_company', '=', True], ['customer', '=', True]]])

# Read records

ids = models.execute_kw(db, uid, password,
    'res.partner', 'search',
    [[['is_company', '=', True], ['customer', '=', True]]],
    {'limit': 1})
[record] = models.execute_kw(db, uid, password,
    'res.partner', 'read', [ids])
# count the number of fields fetched by default
len(record)

# Picking 3 fields deemed interesting

models.execute_kw(db, uid, password,
    'res.partner', 'read',
    [ids], {'fields': ['name', 'country_id', 'comment']})

# Listing record fields

models.execute_kw(
    db, uid, password, 'res.partner', 'fields_get',
    [], {'attributes': ['string', 'help', 'type']})


# Search and read

models.execute_kw(db, uid, password,
    'res.partner', 'search_read',
    [[['is_company', '=', True], ['customer', '=', True]]],
    {'fields': ['name', 'country_id', 'comment'], 'limit': 5})


# Create records, insert data in database

id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
    'name': "Felicia Ebikon",
}])


# Update records

models.execute_kw(db, uid, password, 'res.partner', 'write', [[id], {
    'name': "Felicity Ebikon"
}])
# get record name after having changed it
models.execute_kw(db, uid, password, 'res.partner', 'name_get', [[id]])


# Delete records

models.execute_kw(db, uid, password, 'res.partner', 'unlink', [[id]])
# check if the deleted record is still in the database
models.execute_kw(db, uid, password,
    'res.partner', 'search', [[['id', '=', id]]])