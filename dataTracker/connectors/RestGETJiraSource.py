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

#import os
import requests
#import csv
#import MySQLdb
#import sys
#import ldap
import logging
import config
import re

# debugging
import pdb

theConfig = config.Config()

# read app config
appConfig = theConfig.getConfigFromFile("app.json")
logger = theConfig.getLogger(appConfig)

class Sources:
	def __init__(self):
		return self

class RestGETJiraSource:
	def __init__(self, sourceConfig):
		# authorize api connection
		self.apiConfig = sourceConfig;

		"""
		 Example REST GET Jira Search Configuration
		 {
			"sourceId": "jiraAPI",
			"connectorClassName": "RestGETJiraSearchSource",
			"apiUrl": "https://smartsheet-platform.atlassian.net/rest/api/latest/search?jql={}~\"{}\"",
			"username": "yourName",
			"password": "yourPassword",
			"isArray": true,
			"isStrict": false
		 },
		 
		 list required fields other than 'sourceId' and 'connectorClassName' from sourceConfig entry
		 'sourceId' and 'connectorClassName' are required for every source, and are already being checked
		"""
		requiredFields = "apiUrl,username,password,isArray"
		self.apiConfig = theConfig.validateSourceConfig(sourceConfig, logger, requiredFields)

		return None

	def findSourceMatch(self, lookupVal, lookupKey):
		matchingRecord = {}
	
		# query API
		try:
			if self.apiConfig['username']:
				params = None
				
				#if 'isSearch' in self.apiConfig and self.apiConfig['isSearch'] == True: 
				args = len(tuple(re.finditer("{}", self.apiConfig['apiUrl'])))
				if args == 2:	
					resp = requests.get(self.apiConfig['apiUrl'].format(lookupKey,lookupVal), params=params, auth=(self.apiConfig['username'], self.apiConfig['password']))
				else:
					resp = requests.get(self.apiConfig['apiUrl'].format(lookupVal), params=params, auth=(self.apiConfig['username'], self.apiConfig['password']))
		except KeyError:
			resp = requests.get(self.apiConfig['apiUrl'].format(lookupVal))
		
		respJSON = resp.json()

		try:
			if self.apiConfig['isArray']:
				if len(respJSON['issues']) > 0:
					matchingRecord['key'] = respJSON['issues'][0]['key']
					matchingRecord.update(self.parseJiraFields(respJSON['issues'][0]['fields']))
			else:
				matchingRecord.update(self.parseJiraFields(respJSON['fields']))

		except KeyError, error_message:
			logger.error("No Match for : {} ".format(self.apiConfig['apiUrl'].format(lookupVal)))
		
		return matchingRecord
	
	def parseJiraFields(self,response,key='',path='',flattened=None):
		
		if flattened is None:
			flattened = {}
		if type(response) not in(dict, list):
			flattened[(str(path) if path else "") + (key.capitalize()) if path and type(key) is not int else str(key)] = response
		elif isinstance(response, list):
			for i, item in enumerate(response):
				self.parseJiraFields(item, i, "".join(filter(None,[path,key.capitalize()])), flattened)
		else:
			for new_key, value in response.items():
				self.parseJiraFields(value, new_key, path + (key.capitalize()) if path and type(key) is not int else str(key), flattened)

		return flattened