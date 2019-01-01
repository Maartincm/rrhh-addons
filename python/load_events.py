# -*- coding: utf-8 -*-
import mysql.connector
import os
import shutil
import csv
import sys
import time



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
cnx = mysql.connector.connect(user='root', password='Mum2010Xum',
                              host='10.0.1.17',
                              database='RRHH')
	
mysCursor = cnx.cursor()

# Seteando variables!
# Windows
workingPath = "C:\\Argensun\\RRHH\\Fichadas"
destinationPath = "C:\\Argensun\\RRHH\\Fichadas\\Procesados\\" + time.strftime('%Y%m')
# Checking if backup folder already exists or not. If not exists will create it.
try:
    os.stat(destinationPath)
except:
    os.mkdir(destinationPath)

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
		timeStamp = time.strftime("%Y%m%d%H%M%S")
		destinationFile = "{}\\PROCESADO_{}_{}".format(destinationPath, timeStamp, fileName)
		os.rename(workingPath+"\\"+fileName, destinationFile)

		# Comprimiento el archivo
		destinationFileZip = destinationFile.split(".")
		shutil.make_archive(destinationFileZip[0], "zip", destinationPath, destinationFile)
		os.remove(destinationFile) # Borrando el txt, despues de haberlo zipeado!

		# Subiendo archivo a Amazon S3
		osCommando = 'aws s3 cp --quiet "{}.zip" s3://argensunawsbackup/aws-anviz-prod/backups-fichadas/'.format(destinationFileZip[0])
		os.system(osCommando)

		# Taggeando archivo en el backet S3
		fileNameSplit = fileName.split(".")
		backetFile = "PROCESADO_{}_{}.zip".format(timeStamp, fileNameSplit[0])
		osCommando = 'aws s3api put-object-tagging --bucket argensunawsbackup --key aws-anviz-prod/backups-fichadas/{} \
						--tagging TagSet=[{{Key=backup-30D,Value=Retencion-30-dias}}]'.format(backetFile)
		os.system(osCommando)

cnx.close()
