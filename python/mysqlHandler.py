import os
import csv
import mysql.connector

class mysqlHandler:
	''' Representa una conexión a base de datos MySQL. Lee los parámetros
	    de conexión desde un archivo de texto.'''

	def __init__(self):
		self.getConnInfo()
		self.connect()

	def getConnInfo(self):
		''' Lee los datos de conexion a MySQL, desde un archivo de configuracion,
		    donde se encuentra la siguiente informacion:
		    host, usuario, password y base de datos.'''

		ConfigPath = "/home/rodrigerar/Dropbox/Proyectos/SIGOR/Python"
		ConfigFile = os.path.join (ConfigPath, "mysqlHandler.conf")

		with open (ConfigFile, "r") as myConfigFile:
			FileReader = csv.reader(myConfigFile)
			for row in FileReader:
				if (row [0] == 'username'):
					self.myUser = row [1]
				elif (row [0] == 'password'):
					self.myPass = row [1]
				elif (row [0] == 'database'):
					self.myDb = row [1]
				elif (row [0] == 'host'):
					self.myHost = row [1]

		myConfigFile.close();


	def connect(self):
		''' Se conecta a MySQL, utilizando los datos de conexión obtenidos por el método
		    getConnectionInfo.'''
		self.myCnx = mysql.connector.connect(user= self.myUser,password=self.myPass, host=self.myHost, database=self.myDb)
		self.myCur = self.myCnx.cursor(buffered=True)


	def disconnect(self):
		''' Cierra la conexión a MySQL!.'''
		self.myCnx.close()


	def sigorSetMonedas(self, jsonRequest):
		''' Escribe el tipo de cambio, en la base de datos de SIGOR!'''
		myQuery = """CALL uspSetMonedas ('[{}]', @uspSetMonedasRspJson);""".format(jsonRequest)
		self.myCur.execute(myQuery)
		self.myCnx.commit()

	def sigorSetPizarra(self, jsonRequest):
		''' Actualiza los valores de pizarra, en la base de datos de SIGOR!'''
		myQuery = """CALL uspSetPizarra ('{}', @uspSetPizarraRspJson);""".format(jsonRequest)
		self.myCur.execute(myQuery)
		self.myCnx.commit()
