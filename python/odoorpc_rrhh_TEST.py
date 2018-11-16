import odoorpc

# Prepare the connection to the server
odoo = odoorpc.ODOO('localhost', port=8069)

# Check available databases
#print(odoo.db.list())

# Login
odoo.login('RRHH', 'admin', 'admin')

# Current user
user = odoo.env.user
#print(user.name)            # name of the user connected
#print(user.company_id.name) # the name of its company

Attendance = odoo.env['hr.attendance']
#attendance = Attendance.browse(1)
#print (attendance.employee_id, attendance.check_in, attendance.check_out)

for attendance in Attendance.browse([1, 2, 3]): 
	print (attendance.employee_id, attendance.check_in, attendance.check_out)

#Partner = odoo.env['res.partner']
#Partner.create({'name': "New Partner"})
Attendance.create({'employee_id': 1, 'check_in': '2018-07-16 15:20:00', 'check_out': '2018-07-16 15:21:00'})
#Attendance.create({employee_id: 1, check_in: '2018-07-16 09:00', check_out: '2018-07-16 18:00'})

# Simple 'raw' query
#user_data = odoo.execute('hr.attendance', 'read', [user.id])
#user_data = odoo.execute('hr.attendance', 'read', [4], ['employee_id'])
#print(user_data)



# Use all methods of a model
#if 'sale.order' in odoo.env:
#    Order = odoo.env['sale.order']
#    order_ids = Order.search([])
#    for order in Order.browse(order_ids):
#        print(order.name)
#        products = [line.product_id.name for line in order.order_line]
#        print(products)

# Update data through a record
#user.name = "Brian Jones"