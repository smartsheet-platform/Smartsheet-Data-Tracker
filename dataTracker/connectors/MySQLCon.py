"""
 ----------------------------------------------------------------------
   Copyright 2014 Smartsheet, Inc.
  
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
  
    http://www.apache.org/licenses/LICENSE-2.0
  
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and       
  limitations under the License.             
 ----------------------------------------------------------------------
"""

import MySQLdb
import logging
import config

# debugging
import pdb

theConfig = config.Config()

# read app config
appConfig = theConfig.getConfigFromFile("app.json")
logger = theConfig.getLogger(appConfig)

#class Sources:
#	def __init__(self):
#		return self

class MySQLCon:

	def __init__(self, sourceConfig):

		"""
		 Example MySQL Configuration
		 {
			"sourceId": "productDB",
			"connectorClassName": "MySQLSource",
			"dbServer": "localhost",
			"dbUser": "root",
			"dbPassword": "root",
			"dbName": "dvDB",
			"lookupQuery": "SELECT sku,name,description,price,quantity FROM product WHERE sku = %s",
			"isStrict": false
		 }
		
		 list required fields other than 'sourceId' and 'connectorClassName' from sourceConfig entry
		 'sourceId' and 'connectorClassName' are required for every source, and are already being checked
		"""
		requiredFields = "dbServer,dbUser,dbPassword,dbName,lookupQuery"
		self.mySqlConfig = theConfig.validateSourceConfig(sourceConfig, logger, requiredFields)

		# open db connection
		try:
		    self.con = MySQLdb.connect(self.mySqlConfig['dbServer'], self.mySqlConfig['dbUser'], self.mySqlConfig['dbPassword'], self.mySqlConfig['dbName'])
		except MySQLdb.Error, e:
			logger.error("Error connecting to MySQL database: {}: {}".format(e.args[0],e.args[1]))
			theConfig.endBadly()
		return None

	def findSourceMatch(self, lookupVal, lookupKey):
		matchingRecord = {}

		# query db
		try:
			cur = self.con.cursor()
			cur.execute(self.mySqlConfig['lookupQuery'], lookupVal)
			matchingRecord = cur.fetchone()
		except MySQLdb.Error, e:
			logger.error("DB Error {}: {}".format(e.args[0],e.args[1]))
		
		return matchingRecord