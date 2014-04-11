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

import requests
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

class RestGETCon:

	def __init__(self, sourceConfig):
		# authorize api connection
		self.apiConfig = sourceConfig;

		"""
		 Example REST GET Configuration ( to be set in the settings/sources.json file )
		 {
			"sourceId": "markitOnDemandAPI",
			"connectorClassName": "RestGETCon",
			"apiUrl": "http://dev.markitondemand.com/Api/v2/Quote/json?symbol={}",
			"isArray": false,
			"isStrict": false
		 }
		 
		 list required fields other than 'sourceId' and 'connectorClassName' from sourceConfig entry
		 'sourceId' and 'connectorClassName' are required for every source, and are already being checked
		"""
		requiredFields = "apiUrl,isArray"
		self.apiConfig = theConfig.validateSourceConfig(sourceConfig, logger, requiredFields)

		return None

	def findSourceMatch(self, lookupVal, lookupKey):
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