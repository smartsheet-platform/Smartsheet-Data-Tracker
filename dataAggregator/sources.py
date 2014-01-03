# ----------------------------------------------------------------------
#   Copyright 2014 Smartsheet, Inc.
#  
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#  
#    http://www.apache.org/licenses/LICENSE-2.0
#  
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and       
#  limitations under the License.             
# ----------------------------------------------------------------------

import os
import requests
import csv
import MySQLdb
import sys
import ldap
import logging
import config

theConfig = config.Config()

# read app config
appConfig = theConfig.getConfigFromFile("app.json")
logger = theConfig.getLogger(appConfig)


class Sources:
	def __init__(self):
		return self

class CSVSource:

	def __init__(self, sourceConfig):
		self.csvData = []

		# Example CSV Configuration
		# {
		#	"sourceId": "employees",
		#	"connectorClassName": "CSVSource",
		#	"fileName": "employees.csv",
		#	"isStrict": false
		# }
		# list required fields other than 'sourceId' and 'connectorClassName' from sourceConfig entry
		# 'sourceId' and 'connectorClassName' are required for every source, and are already being checked
		requiredFields = "fileName"
		csvSourceConfig = theConfig.validateSourceConfig(sourceConfig, logger, requiredFields)

		# open CSV File
		with open(os.path.dirname(os.path.realpath(__file__))  + '/' + csvSourceConfig['fileName']) as sourceFile:
			sourceReader = csv.reader(sourceFile)
			
			# save CSV contents to memory
			for readerRow in sourceReader:
				self.csvData.append(readerRow)

		return None

	def findSourceMatch(self, lookupVal, lookupIndex):
		matchingRow = []

		# query csv file
		for sourceRow in self.csvData:
			if len(sourceRow):
				if sourceRow[lookupIndex] == lookupVal:
					matchingRow = sourceRow
					break

		return matchingRow

class MySQLSource:

	def __init__(self, sourceConfig):

		# Example MySQL Configuration
		# {
		#	"sourceId": "productDB",
		#	"connectorClassName": "MySQLSource",
		#	"dbServer": "localhost",
		#	"dbUser": "root",
		#	"dbPassword": "root",
		#	"dbName": "dvDB",
		#	"lookupQuery": "SELECT sku,name,description,price,quantity FROM product WHERE sku = %s",
		#	"isStrict": false
		# }
		#
		# list required fields other than 'sourceId' and 'connectorClassName' from sourceConfig entry
		# 'sourceId' and 'connectorClassName' are required for every source, and are already being checked
		requiredFields = "dbServer,dbUser,dbPassword,dbName,lookupQuery"
		self.mySqlConfig = theConfig.validateSourceConfig(sourceConfig, logger, requiredFields)

		# open db connection
		try:
		    self.con = MySQLdb.connect(self.mySqlConfig['dbServer'], self.mySqlConfig['dbUser'], self.mySqlConfig['dbPassword'], self.mySqlConfig['dbName'])
		except MySQLdb.Error, e:
			logger.error("Error connecting to MySQL database: {}: {}".format(e.args[0],e.args[1]))
			theConfig.endBadly()
		return None

	def findSourceMatch(self, lookupVal, lookupIndex):
		matchingRecord = {}

		# query db
		try:
			cur = self.con.cursor()
			cur.execute(self.mySqlConfig['lookupQuery'], lookupVal)
			matchingRecord = cur.fetchone()
		except MySQLdb.Error, e:
			logger.error("DB Error {}: {}".format(e.args[0],e.args[1]))
		
		return matchingRecord

class OpenLDAPSource:

	def __init__(self, sourceConfig):
		
		# Example OpenLDAP Configuration
		# {
		#	"sourceId": "openldap",
		#	"connectorClassName": "OpenLDAPSource",
		#	"ldapServer": "127.0.0.1",
		#	"baseDN": "dc=smartsheet,dc=com",
		#	"orgUnit": "ou=people",
		#	"adminUser": "cn=admin",
		#	"adminPass": "smart",
		#	"searchFilter": "cn=*{}*",
		#	"retrieveAttributes": "givenName,sn,roomNumber,mail,telephoneNumber",
		#	"ldapTimeout": 0,
		#	"isStrict": false
		# }
		# list required fields other than 'sourceId' and 'connectorClassName' from sourceConfig entry
		# 'sourceId' and 'connectorClassName' are required for every source, and are already being checked
		requiredFields = "ldapServer,baseDN,orgUnit,adminUser,adminPass,searchFilter,retrieveAttributes,ldapTimeout"
		self.ldapConfig = theConfig.validateSourceConfig(sourceConfig, logger, requiredFields)

		# bind to LDAP server
		try:
			self.l = ldap.open(self.ldapConfig["ldapServer"])
			self.l.simple_bind_s(self.ldapConfig["adminUser"] + "," + self.ldapConfig["baseDN"],self.ldapConfig["adminPass"])
			logger.info("Connected to LDAP at {}".format(self.ldapConfig["ldapServer"]))
		except ldap.LDAPError, error_message:
			logger.error("Couldn't connect to LDAP because of the following reason: {}".format(error_message), exc_info=TRUE)
		return None

	def findSourceMatch(self, lookupVal, lookupKey):
		matchingRecord = {}
		base = self.ldapConfig["orgUnit"] + "," + self.ldapConfig["baseDN"]
		scope = ldap.SCOPE_SUBTREE
		searchFilter = self.ldapConfig["searchFilter"].format(lookupVal)
		retrieve_attributes = []
		search_result_set = []
		timeout = self.ldapConfig["ldapTimeout"]

		if len(self.ldapConfig["retrieveAttributes"]):
			for attr in self.ldapConfig["retrieveAttributes"].split(","):
				retrieve_attributes.append(str(attr))

		# query LDAP server
		try:
			search_results = self.l.search_s(base, scope, searchFilter, retrieve_attributes)
			
			for dn,entry in search_results:
				for key,val in entry.items():
					matchingRecord[key] = val[0]	
		except ldap.LDAPError, error_message:
			logger.error("LDAP Query busted because of the following reason: {} ".format(error_message, exc_info=TRUE))
		
		return matchingRecord

class RestGETSource:

	def __init__(self, sourceConfig):
		# authorize api connection
		self.apiConfig = sourceConfig;

		# Example REST GET Configuration
		# {
		#	"sourceId": "markitOnDemandAPI",
		#	"connectorClassName": "RestGETSource",
		#	"apiUrl": "http://dev.markitondemand.com/Api/v2/Quote/json?symbol={}",
		#	"isArray": false,
		#	"isStrict": false
		# }
		# 
		# list required fields other than 'sourceId' and 'connectorClassName' from sourceConfig entry
		# 'sourceId' and 'connectorClassName' are required for every source, and are already being checked
		requiredFields = "apiUrl,isArray"
		self.apiConfig = theConfig.validateSourceConfig(sourceConfig, logger, requiredFields)

		return None

	def findSourceMatch(self, lookupVal, lookupIndex):
		matchingRecord = {}

		# query API
		resp = requests.get(self.apiConfig['apiUrl'].format(lookupVal))
		respJSON = resp.json()

		#build matchingRecord array
		if self.apiConfig['isArray']:
			for key,val in respJSON[0].items():
				matchingRecord[key] = val
		else:
			for key,val in respJSON.items():
				matchingRecord[key] = val

		return matchingRecord

