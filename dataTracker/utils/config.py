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
import json
import logging
import logging.handlers
import sys

class Config:
	def __init__(self):
		loggers = {}

		return None

	def endBadly(self):
		print "Data Tracker ended badly due to an error. Please check the log for more details."
		sys.exit(1)

	def getConfigFromFile(self, fileName):
		config = []

		try:
			with open(os.getcwd() + "/settings/" + fileName) as theFile:
				config = json.load(theFile)
		except ValueError as e:
			print "Uh oh. The following problem occured while trying to read {}: {}".format(fileName,e)
			print "Please make sure the file contains properly formatted JSON."
		return config

	def getLogger(self, appConfig):
		global loggers

		# configure and return logging object
		logger = logging.getLogger(__name__)
		
		# add logging handler if one doesn't already exist, otherwise just send back logger obj
		# this reduces duplicate entries in log
		if not len(logger.handlers):
			logger.setLevel(eval(appConfig["logLevel"]))

			handler = logging.handlers.RotatingFileHandler(appConfig["logFileName"],mode='a',maxBytes=appConfig['logFileMaxBytes'],backupCount=appConfig['logFileBackupCount'])
			handler.setLevel(eval(appConfig["logLevel"]))

			formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
			handler.setFormatter(formatter)

			logger.addHandler(handler)

		return logger

	def validateMappingConfig(self, mappingConfig, theLogger):
		
		for mapping in mappingConfig:
			# verify mappingConfig is correct
			try:
				if mapping["sheetId"] <= 0:
					theLogger.error("A mapping has an invalid sheetId attribute in mapping.json.")
					self.endBadly()
				
				if len(mapping["sources"]):
					for source in mapping["sources"]:
						#print source
						# check sourceId
						if len(source["sourceId"]) == 0:
							theLogger.error("Mapping with sheetId {} has no sources. Each mapping needs at least one source.".format(mapping['sheetId']))
							self.endBadly()
						
						# check lookupMapping
						if len(source["lookupMapping"]) == 0:
							theLogger.error("Mapping with sheetId {} does not have a lookupMapping. Each mapping needs a lookupMapping.".format(mapping['sheetId']))
							self.endBadly()
						else:
							if ('lookupByRowId' not in source['lookupMapping']) or ('lookupByRowId' in source['lookupMapping'] and source['lookupMapping']['lookupByRowId'] == False):
								theLogger.info(source['lookupMapping'])
								# validate mapping
								self.validateMapping(source["lookupMapping"], theLogger, source["sourceId"], "lookup")

						# check outputMappings
						if len(source["outputMappings"]) == 0:
							theLogger.error("Mapping with sheetId {} has no outputMappings. Each mapping needs at least one outputMapping.".format(mapping['sheetId']))
							self.endBadly()
						else:
							# loop mappings and validate each
							for oMap in source["outputMappings"]:
								self.validateMapping(oMap, theLogger, source["sourceId"], "output")
				else:
					theLogger.error("Mapping with sheetId {} has an invalid source attribute in mapping.json.".format(mappingConfig['sheetId']))
					self.endBadly()

			except KeyError, error_message:
				if str(error_message) == '\'sheetId\'':
					theLogger.error("A mapping needs a sheetId setting specified in mapping.json.")
					self.endBadly()
				else:
					theLogger.error("Mapping with sheetId {} needs a {} specified in sources.json.".format(mapping['sheetId'], error_message))
					self.endBadly()

		return mappingConfig


	def validateMapping(self, mapping, theLogger, sourceId, mappingType):

		try:
			# check if sourceKey is blank doesn't matter if it's a str or int
			if len(str(mapping["sourceKey"])) == 0:
				theLogger.error("The sourceKey value is blank for a {} mapping attribute for sourceId {} in mapping.json.".format(mappingType,sourceId))
				self.endBadly()
			# check if sheetColumn is blank
			if len(mapping["sheetColumn"]) == 0:
				theLogger.error("The sheetColumn value is blank for a {} mapping attribute for sourceId {} in mapping.json.".format(mappingType,sourceId))
				self.endBadly()
		except KeyError, error_message:
				# this error happens if either of the mapping attributes don't exist
				theLogger.error("{}Mapping for sourceId {} is missing a {} attribute in mapping.json.".format(mappingType,sourceId,error_message))
				self.endBadly()

		return None


	def validateSourceConfig(self, sourceConfig, theLogger, requiredFields):
		
		# verify sourceConfig is correct
		try:
			if len(sourceConfig['sourceId']):
				sourceId = sourceConfig['sourceId']
			else:
				theLogger.error("A source with the connectorClassName of CSVSource needs a value for the sourceId setting in sources.json.")
				self.endBadly()	
			for field in requiredFields.split(','):
				if not isinstance(type(sourceConfig[field]), str) or len(sourceConfig[field]):
					tmpField = sourceConfig[field]
				else:
					theLogger.error("Source with id {} needs a value for the {} setting in sources.json.".format(sourceConfig['sourceId'], field))				
					self.endBadly()

			isStrict = sourceConfig['isStrict']
		except KeyError, error_message:
			if str(error_message) == '\'sourceId\'':
				theLogger.error("A source with the connectorClassName of CSVSource needs a sourceId setting specified in sources.json.")
				self.endBadly()			
			elif str(error_message) == '\'isStrict\'':
				sourceConfig['isStrict'] = False
			else:
				theLogger.error("Source with id {} needs a {} specified in sources.json.".format(sourceConfig['sourceId'], error_message))
				self.endBadly()

		return sourceConfig

		
