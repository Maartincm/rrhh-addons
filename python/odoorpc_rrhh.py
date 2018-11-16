import os
os.environ['http_proxy']=''
import odoorpc

# Preparando la conexion
#odoo = odoorpc.ODOO('localhost', port=8069) # Conexion local!
odoo = odoorpc.ODOO('https://argensun.staging.e-mips.com.ar', port=443) # Conexion Eynes!

# Login
#odoo.login('RRHH', 'admin', 'admin') # Conexion local!
odoo.login('argensun', 'admin', 'admin') # Conexion Eynes

# Insertando en hr.attendance
Attendance = odoo.env['hr.attendance']
#Attendance.create({'employee_id': 1, 'check_in': '2018-07-17 13:00:00', 'check_out': '2018-07-17 14:00:00'})
#Attendance.create({'employee_id': 1, 'check_in': '2018-07-17 13:00:00'})
Attendance.create({'employee_id': 1, 'check_out': '2018-07-17 13:00:00'})

