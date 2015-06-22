"""
 ----------------------------------------------------------------------
   Copyright 2015 Smartsheet, Inc.

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

import requests
import logging
import re

# debugging
import pdb

theConfig = config.Config()

# read app config
appConfig = theConfig.getConfigFromFile("app.json")
logger = theConfig.getLogger(appConfig)

class RestGETJiraCon:
	def __init__(self, sourceConfig):
		# authorize api connection
		self.apiConfig = sourceConfig;

		"""
		 Example REST GET JIRA Search Configuration ( to be set in the settings/sources.json file )
		 {
			"sourceId": "jiraAPI",
			"connectorClassName": "RestGETJiraSearchCon",
			"apiUrl": "https://yourOrg.atlassian.net/rest/api/latest/search?jql={}~\"{}\"",
			"username": "yourName",
			"password": "yourPassword",
			"isArray": true,
			"isStrict": false
		 },

		 list required fields other than 'sourceId' and 'connectorClassName' from sourceConfig entry
		 'sourceId' and 'connectorClassName' are required for every source, and are already being checked
		"""
		requiredFields = "apiUrl,isArray"
		self.apiConfig = theConfig.validateSourceConfig(sourceConfig, logger, requiredFields)

		return None

	def findSourceMatch(self, lookupVal, lookupKey):
		matchingRecord = {}
		respJSON = {}

		# query API
		try:
			params = None
			args = len(tuple(re.finditer("{}", self.apiConfig['apiUrl'])))
			if 'username' in self.apiConfig:
				if args == 2:
					resp = requests.get(self.apiConfig['apiUrl'].format(lookupKey,lookupVal), params=params, auth=(self.apiConfig['username'], self.apiConfig['password']))
				else:
					resp = requests.get(self.apiConfig['apiUrl'].format(lookupVal), params=params, auth=(self.apiConfig['username'], self.apiConfig['password']))
			elif 'base64Basic' in self.apiConfig:
				headers = {'Authorization': 'Basic '+ self.apiConfig['base64Basic']}
				if args == 2:
					resp = requests.get(self.apiConfig['apiUrl'].format(lookupKey,lookupVal), params=params, headers=headers)
				else:
					resp = requests.get(self.apiConfig['apiUrl'].format(lookupVal), params=params, headers=headers)
		except KeyError:
			resp = requests.get(self.apiConfig['apiUrl'].format(lookupVal))

		try:
			respJSON = resp.json()
		except ValueError, error_message:
			logger.error("ValueError for lookupMapping value '{}': {}".format(lookupVal, error_message))
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
			if type(key) is not int:
				flattened[(str(path) if path else "") + (key.capitalize()) if path else str(key)] = response
			else:
				flattened[(str(path) if path else "") + (str(key)) if path else str(key)] = response
		elif isinstance(response, list):
			for i, item in enumerate(response):
				self.parseJiraFields(item, i, "".join(filter(None,[path,key.capitalize()])), flattened)
		else:
			for new_key, value in response.items():
				self.parseJiraFields(value, new_key, path + (key.capitalize()) if path and type(key) is not int else str(key), flattened)
		return flattened