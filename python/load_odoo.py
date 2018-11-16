# -*- coding: utf-8 -*-
import mysql.connector
import os
import csv
import sys
import time
import odoorpc

def mysqlConnect():

	with open (configFile, "r") as myFile:
		fReader = csv.reader(myFile , delimiter=':')
		for row in fReader:
			if (row [0] == 'Username'):
				myUser = row [1].strip()
			elif (row [0] == 'Password'):
				myPass = row [1].strip()
			elif (row [0] == 'Database'):
				myDb = row [1].strip()
			elif (row [0] == 'Host'):
				myHost = row [1].strip()

	global myCnx

	try:
		myCnx = mysql.connector.connect(user=myUser, password=myPass, host=myHost, database=myDb)
	except mysql.connector.errors.Error as err:
		print("Ops! Ocurrió un error: {}".format(err))
		sys.exit(1)

	return myCnx


def getArchivos():

	global fData

	try:
		cursor = myCnx.cursor ()
		cursor.execute ("SELECT id, nombre FROM archivo WHERE cargado_odoo IS NULL")
		fData = cursor.fetchall ()
	except mysql.connector.errors.Error as err:
		print("Ops! Ocurrió un error: {}".format(err))
		sys.exit(1)

	return len(fData)


def odooConnect():

	global odoo
	global Attendance

	# Conectando a Odoo
	try:
		odoo = odoorpc.ODOO('localhost', port=8069)
		odoo.login('argensun', 'admin', 'admin') # 2) Setear los datos de conexión a Odoo.
		Attendance = odoo.env['hr.attendance']
	except odoorpc.error.RPCError as err:
		print("Ops! Ocurrió un error: {}".format(err))
		sys.exit(1)

	return odoo, Attendance


def getFichadas(idFile, nameFile):

	# Obteniendo fichadas y cargando en Odoo
	try:
		cursor = myCnx.cursor()
		query = '''SELECT 
					DATE_ADD(fecha_hora, INTERVAL 3 HOUR),
					numero_legajo,
	    			CASE id_tipo_evento
	    				WHEN 0 THEN 'Entrada'
	    				WHEN 1 THEN 'Salida'
	    				WHEN 2 THEN 'Salida'
	    				END
					FROM fichada WHERE id_archivo = {}'''.format(idFile)
		cursor.execute(query)
		data = cursor.fetchall()
	except mysql.connector.errors.Error as err:
		print("Ops! Ocurrió un error: {}".format(err))
		sys.exit(1)

	for row in data:
		if (row[2] == 'Entrada'):
			attendance = {'employee_id': row[1], 'check_in': ''}
			attendance['check_in'] = '{}'.format(row[0])
			Attendance.create(attendance)
		else:
			attendance = {'employee_id': row[1], 'check_out': ''}
			attendance['check_out'] = '{}'.format(row[0])
			Attendance.create(attendance)

	# Marcando el archivo como procesado.
	fechaCarga = time.strftime("%Y-%m-%d %H:%M:%S")
	query = '''UPDATE archivo SET cargado_odoo = '{}' WHERE id = {}'''.format(fechaCarga, idFile)
	cursor.execute(query)
	myCnx.commit()


##########
#        #
#  MAIN  #
#        #
##########

configPath = "/home/rodrigerar/Dropbox/Proyectos/RRHH/python" # 1) Setear el path donde se encuentra el erchivo mysql.conf
configFile = os.path.join (configPath, "mysql.conf")

# Conectando a MySQL:
mysqlConnect()
odooConnect()

# Buscando novedades para procesar:
if (getArchivos() != 0):
	# Procesando Novedades
	for row in fData :
		getFichadas(row[0], row[1])

myCnx.close()
