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

from utils import config

import ldap
import logging

# debugging
import pdb

theConfig = config.Config()

# read app config
appConfig = theConfig.getConfigFromFile("app.json")
logger = theConfig.getLogger(appConfig)

#class Sources:
#	def __init__(self):
#		return self

class OpenLDAPCon:

	def __init__(self, sourceConfig):
		
		"""
		 Example OpenLDAP Configuration
		 {
			"sourceId": "openldap",
			"connectorClassName": "OpenLDAPCon",
			"ldapServer": "127.0.0.1",
			"baseDN": "dc=smartsheet,dc=com",
			"orgUnit": "ou=people",
			"adminUser": "cn=admin",
			"adminPass": "smart",
			"searchFilter": "cn=*{}*",
			"retrieveAttributes": "givenName,sn,roomNumber,mail,telephoneNumber",
			"ldapTimeout": 0,
			"isStrict": false
		 }
		 list required fields other than 'sourceId' and 'connectorClassName' from sourceConfig entry
		 'sourceId' and 'connectorClassName' are required for every source, and are already being checked
		"""
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