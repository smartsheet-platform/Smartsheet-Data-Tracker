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

import os
import csv
import logging
import config

# debugging
import pdb

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

		"""
		 Example CSV Configuration
		 {
			"sourceId": "employees",
			"connectorClassName": "CSVSource",
			"fileName": "employees.csv",
			"isStrict": false
		 }
		 list required fields other than 'sourceId' and 'connectorClassName' from sourceConfig entry
		 'sourceId' and 'connectorClassName' are required for every source, and are already being checked
		"""
		requiredFields = "fileName"
		csvSourceConfig = theConfig.validateSourceConfig(sourceConfig, logger, requiredFields)

		# open CSV File
		with open(os.getcwd() + '/' + csvSourceConfig['fileName']) as sourceFile:
			sourceReader = csv.reader(sourceFile)
			
			# save CSV contents to memory
			for readerRow in sourceReader:
				self.csvData.append(readerRow)

		return None

	def findSourceMatch(self, lookupVal, lookupKey):
		matchingRow = []

		# query csv file
		for sourceRow in self.csvData:
			if len(sourceRow):
				if sourceRow[lookupKey] == lookupVal:
					matchingRow = sourceRow
					break

		return matchingRow