# -*- coding: utf-8 -*-
import mysql.connector
import os
import csv
import sys
import time

# Prueba por GIT 3



def loteHandler (fileName):
	''' Registrando nuevo archivo en MySQL y obteniendo número de lote'''
	try:
		fechaFormat = time.strftime("%Y-%m-%d %H:%M:%S")
		stmt = """INSERT INTO archivo (nombre, cargado_mysql) VALUES ('{}', '{}')""".format(fileName, fechaFormat) 
		mysCursor.execute(stmt)
	except mysql.connector.IntegrityError as err:
		print("Ops! Ocurrió un error: {}".format(err))
		sys.exit(1) # exiing with a non zero value is better for returning from an error

	return mysCursor.lastrowid

# Abriendo conexion a MySQL
cnx = mysql.connector.connect(user='root', password='..LetyTyle',
                              host='127.0.0.1',
                              database='RRHH')
	
mysCursor = cnx.cursor()


# Seteando variables!
# Windows
##workingPath = "C:\Argensun\RRHH\Fichadas"
##destinationPath = "C:\Argensun\RRHH\Fichadas\Procesados"
# Linux
workingPath = "/home/rodrigerar/Dropbox/Proyectos/RRHH/files"
destinationPath = "/home/rodrigerar/Dropbox/Proyectos/RRHH/files/Procesados"

# Buscando archivo/s de novedades
filesList = os.listdir(workingPath)

for fileName in filesList:
	if fileName.lower().endswith( ".txt" ):
		data = []
		numeroLote = loteHandler(fileName)
		with open(os.path.join(workingPath, fileName), "r") as myFile:
			myFileReader = csv.reader(myFile)
			for row in myFileReader:
				data.append((numeroLote, row[1],row[3],row[0],row[2]))
		myFile.close()

		# Cargando novedades en MySQL
		try:
			mysCursor.execute("SET FOREIGN_KEY_CHECKS=0")
			stmt = "INSERT INTO fichada (id_archivo, fecha_hora, id_dispositivo, numero_legajo, id_tipo_evento) VALUES (%s, %s, %s, %s, %s)" 
			mysCursor.executemany(stmt, data)
			mysCursor.execute("SET FOREIGN_KEY_CHECKS=1")
		except mysql.connector.IntegrityError as err:
			print("Ops! Ocurrió un error: {}".format(err))
			sys.exit(1) # exiing with a non zero value is better for returning from an error

		cnx.commit()

		# Moviendo archivo
		# Windows
		##destinationFile = "{}\\PROCESADO_{}_{}".format(destinationPath, time.strftime("%Y%m%d%H%M%S"), fileName)
		##os.rename(workingPath+"\\"+fileName, destinationFile)

cnx.close()
