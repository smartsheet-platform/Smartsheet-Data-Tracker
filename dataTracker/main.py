#!/usr/local/bin/env python

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


# written and tested with Python 2.7.5
# depencies to install: 
# requests ( http://docs.python-requests.org/en/latest/ )
# mysql-python ( http://mysql-python.sourceforge.net/ )
# python-ldap ( http://python-ldap.org/ )

import requests
import json
import sources
import os
import config
import sys
import logging
import datetime

def main():
	theConfig = config.Config()

	# read app config
	appConfig = theConfig.getConfigFromFile("app.json")
	logger = theConfig.getLogger(appConfig)


	logger.info('***Smartsheet Data Tracker Utility Started: {}'.format(str(datetime.datetime.now()).split('.')[0]))

	API_URL = appConfig["apiURL"]
	ACCESS_TOKEN = "Bearer " + appConfig["accessToken"]
	headers = {"Authorization": ACCESS_TOKEN}


	# read sources config
	# array of sources
	# 	sourceId
	#	connectorClassName
	#	sourceObject
	# 	...other custom attributes
	#
	sourceConfigs = theConfig.getConfigFromFile("sources.json")

	# loop source configs and initialize sourceConfig objects
	if len(sourceConfigs):
		for sourceConf in sourceConfigs:
			try:
				module = __import__('sources', fromlist=[sourceConf['connectorClassName']])
				sourceClass = getattr(module, sourceConf['connectorClassName'])
				sourceConf['sourceObject'] = sourceClass(sourceConf)
			except KeyError, error_message:
				logger.error('Source with id {} needs a connectorClassName attribute'.format(sourceConf['sourceId']))
				theConfig.endBadly()
	else:
		logger.error('There are no sources configured. Please add a properly formatted source node to the sources.json file.')
		theConfig.endBadly()

	# loop those mappings
	# read mapping config
	# 	sheetId
	# 	sources
	# 	lookupMapping {sourceKey, sheetColumn}
	# 	outputMappings {sourceKey, sheetColumn}
	#
	mappings = theConfig.getConfigFromFile("mapping.json")

	# validate mapping configs
	theConfig.validateMappingConfig(mappings, logger)

	print
	print ' Smartsheet Data Tracker'
	print '============================'
	if(appConfig['logFileName']):
		print 'Logging to file: {}'.format(appConfig['logFileName'])
	if len(mappings):

		for mapping in mappings:
			# get sheet
			getSheetUrl = API_URL + "/sheet/" + str(mapping['sheetId'])
			getSheetResponse = requests.get(getSheetUrl, headers=headers)
			
			if getSheetResponse.status_code == 200:
				theSheet = getSheetResponse.json()
			else:
				logger.debug('There was a problem getting sheet {}. '.format(mapping['sheetId']))
				logger.debug('API Response Status Code: {}'.format(getSheetResponse.status_code))
				
				if getSheetResponse.status_code == 403:
					logger.debug('Access forbidden. Probably forgot to add your API Access Token to main.py')
				elif getSheetResponse.status_code == 404:
					logger.debug('Sheet not found. Make sure the sheetId value in mapping.json is correct.')
				break

			logger.info('Updating sheet: {}'.format(theSheet['name']))

			# mapping columnIds with column names to make mapping.json more readable
			for mappingSource in mapping['sources']:
				# loop over all columns in sheet
				for col in theSheet['columns']:
					
					# check if column is lookup column
					if mappingSource['lookupMapping']['sheetColumn'] == col['title']:
						mappingSource['lookupMapping']['sheetColumnId'] = col['id']
					else:
						# check if column is output column
						for outMap in mappingSource['outputMappings']:
							if outMap['sheetColumn'] == col['title']:
								outMap['sheetColumnId'] = col['id']
						
				if 'sheetColumnId' not in mappingSource['lookupMapping']:
					logger.error("Lookup column {} not found in sheet {}".format(mappingSource['lookupMapping']['sheetColumn'], theSheet['name']))
					theConfig.endBadly()

				for outM in mappingSource['outputMappings']:
					if 'sheetColumnId' not in outM:
						logger.warning("Output column {} not found in sheet {}".format(outM['sheetColumn'], theSheet['name']))
			
			for sheetRow in theSheet['rows']:
				sourceMatch = [] # init sourceMatch
				payload = [] # init payload
				updateRowUrl = API_URL + "/row/" + str(sheetRow['id']) + "/cells"

				for mappingSource in mapping['sources']:
					logger.info('Source: {}'.format(mappingSource['sourceId']))

					for source in sourceConfigs: 
						if source['sourceId'] == mappingSource['sourceId']:
							currentSource = source
							break
					
					for cell in sheetRow['cells']:
						# find lookup value match 
						if cell['columnId'] == mappingSource['lookupMapping']['sheetColumnId']:

							if 'value' in cell:
								logger.info('Searching source for value: {}'.format(cell['value']))
								# sourceMatch is the source record with the matching lookup value
								sourceMatch = currentSource['sourceObject'].findSourceMatch(cell['value'], mappingSource['lookupMapping']['sourceKey'])
								
								if len(sourceMatch):
									logger.info('Match Found')

									for outputMap in mappingSource['outputMappings']:
										# build put call
										# - columnId
										# - value
										try:
											payload.append({'columnId': outputMap['sheetColumnId'], 'value': sourceMatch[outputMap['sourceKey']], 'strict':currentSource['isStrict']})
										except KeyError, error_message:
											
											if str(error_message) == '\'sheetColumnId\'':
												logger.warning('The {} was not set for the sheetColumn: {} in source: {}. Verify the sheetColumn value matches the column title in sheet: {}'.format(error_message,outputMap['sheetColumn'],mappingSource['sourceId'],theSheet['name']))
											else:
												logger.warning('The sourceKey of {} could not be found in the source {} for {}. {}'.format(outputMap['sourceKey'],mappingSource['sourceId'],cell['value'],error_message))
								else:
									logger.info('No Match')
				if len(payload):
					# send update to smartsheet for each row
					updateResponse = requests.put(updateRowUrl, data=json.dumps(payload), headers=headers)
					
					# output api response
					if updateResponse.status_code == 200:
						logger.info('Sheet {} Updated'.format(theSheet['name']))
					else:
						logger.warning(updateResponse)

		logger.info('===Smartsheet Data Tracker Utility Completed: {}'.format(str(datetime.datetime.now()).split('.')[0]))
	else:
		logger.error('There are no mappings configured. Please add a properly formatted mapping node to the mapping.json file.')

if __name__ == '__main__':
	main()	