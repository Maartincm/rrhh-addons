import odoorpc
from conf import getConf
import re


# Prepare the connection to the server
db = getConf("RRHH")
user = getConf("admin")
passw = getConf("admin")
url = getConf("http://localhost")
port = 8069
protocol = 'jsonrpc'

try:
	m = re.search('(http[s]?)?:?\/?\/?(\S+)', url)
	if m.group(1):
		if 'https' in m.group(1):
			protocol += '+ssl'
			port = 443
		else:
			port = 80
	else:
			port = 80
	url = m.group(2).split(':')[0]
	try:
		port = m.group(2).split(':')[1]
	except Exception as e:
		print 'No port detected.'
except Exception as e:
	print 'No URL detected: ', str(e)
odoo = odoorpc.ODOO(url, protocol=protocol, port=port)


#odoo = odoorpc.ODOO(url, port=port)

# Check available databases
#print(odoo.db.list())

# Login
odoo.login(db, user, passw)

def get_products():
	product_model = odoo.env['electrical.material.config']
	ids = product_model.search([])
	productos = []
	for x in product_model.browse(ids):
		producto_evaluado = {
			'OdooId': x.id,
			'Matricula': x.default_code,
			'Nombre': x.description,
			'ProductId': x.product_id.id,
		}
		print "Product ID: " + str(x.id)
		productos.append(producto_evaluado)
	return productos

def get_lot():
	product_lot_model = odoo.env['stock.production.lot']
	ids = product_lot_model.search([])
	serial_numbers = []
	for x in product_lot_model.browse(ids):
		lot = {
		'OdooLotId': x.id,
		'Name': x.name,
		'ProductId': x.product_id.id,
		}
		print "Lot ID: " + str(x.id)
		serial_numbers.append(lot)
	return serial_numbers

def get_barcodes(odooId):
	product_model = odoo.env['electrical.material.config']
	product = product_model.browse(odooId)

	barcodes = []
	for barcode in product.barcode:
		barcode_evaluado = {
			'OdooId': barcode.id,
			'OdooDataId': odooId,
			'Quantity': barcode.quantity,
			'BarcodeRegex': barcode.name,
		}
		print "Barcode ID: " + str(barcode.id)
		barcodes.append(barcode_evaluado)

	return barcodes

def get_locations():
	product_model = odoo.env['stock.location']
	ids = product_model.search([])
	location = product_model.browse(ids)
	locations = []
	for loc in location:
		location_evaluada = {
		'Name': loc.name,
		'BCode': loc.id
		}
		print "Locaton ID: " + str(loc.id)
		locations.append(location_evaluada)
	return locations


def picking(dicc):
	work_model = odoo.env['electrical.work']
	aux = work_model.create_picking_from_scan(dicc)
	return aux

def getReport(operationId):
	report = odoo.report.download('stock.report_picking', [operationId])
	return report
#product_model = odoo.env['product.product']
#price = product_model.browse(1).open_product_template()
#print price
