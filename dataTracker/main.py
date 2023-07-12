#!/usr/bin/env python

"""
 ----------------------------------------------------------------------
   Copyright 2016 Smartsheet, Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions ipabuse@wirelessdataspco.org",
  limitations under the License.
 ----------------------------------------------------------------------f


 written and tested with Python 2.7.5
 depencies to install:
 requests ( http://docs.python-requests.org/en/latest/ )
 mysql-python ( http://mysql-python.sourceforge.net/ )
 python-ldap ( http://python-ldap.org/ )
"""

from utils import config
from utils import match

import requests
import json
import os
import sys
import logging
import datetime
import time
import string

# debugging
import pdb

def main():
	theConfig = config.Config()
	theMatch = match.Match()
	# file names for the json config files in settings directory
	APP_CONFIG_FILE = 'app.json'
	SOURCES_FILE = 'sources.json'
	MAPPINGS_FILE = 'mapping.json'


	# read app config
	appConfig = theConfig.getConfigFromFile(APP_CONFIG_FILE)
	logger = theConfig.getLogger(appConfig)

	logger.info('***Smartsheet Data Tracker Utility Started: {}'.format(str(datetime.datetime.now()).split('.')[0]))
	API_URL = appConfig['apiURL']
	ACCESS_TOKEN = 'Bearer ' + appConfig['accessToken']
	headers = {'Authorization': ACCESS_TOKEN}

	"""
	 read sources config
	 array of sources
	 	sourceId
		connectorClassName
		sourceObject
	 	...other custom attributes
	"""
	sourceConfigs = theConfig.getConfigFromFile(SOURCES_FILE)

	# loop source configs and initialize sourceConfig objects
	if len(sourceConfigs):
		for sourceConf in sourceConfigs:
			try:
				module = __import__('connectors.' + sourceConf['connectorClassName'], fromlist=[sourceConf['connectorClassName']])
				sourceClass = getattr(module, sourceConf['connectorClassName'])
				sourceConf['sourceObject'] = sourceClass(sourceConf)
			except KeyError, error_message:
				logger.error('Source with id {} needs a connectorClassName attribute'.format(sourceConf['sourceId']))
				theConfig.endBadly()
	else:
		logger.error('There are no sources configured. Please add a properly formatted source node to the sources.json file.')
		theConfig.endBadly()

	"""
	 loop those mappings
	 read mapping config
	 	sheetId
	 	sources
	 	lookupMapping {sourceKey, sheetColumn}
	 	outputMappings {sourceKey, sheetColumn}
	"""
	mappings = theConfig.getConfigFromFile(MAPPINGS_FILE)

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
			getSheetUrl = API_URL + "/sheets/" + str(mapping['sheetId'])
			getSheetResponse = requests.get(getSheetUrl, headers=headers)
			logger.info('get sheet response for {}: {}'.format(str(mapping['sheetId']), getSheetResponse.status_code))
            		if getSheetResponse.status_code == 200:
				theSheet = getSheetResponse.json()
			else:
				logger.error('There was a problem getting sheet {}. '.format(mapping['sheetId']))
				logger.error('API Response Status Code: {}'.format(getSheetResponse.status_code))

				if getSheetResponse.status_code == 403:
					logger.error('Access forbidden. Probably forgot to add your API Access Token to main.py')
				elif getSheetResponse.status_code == 404:
					logger.error('Sheet not found. Make sure the sheetId value in mapping.json is correct.')
				break

			logger.info('Updating sheet: {}'.format(theSheet['name']))

			# mapping columnIds with column names to make mapping.json more readable
			for mappingSource in mapping['sources']:
				# loop over all columns in sheet
				for col in theSheet['columns']:


					# check if column is lookup column
					if 'sheetColumn' in mappingSource['lookupMapping'] and mappingSource['lookupMapping']['sheetColumn'] == col['title'] :
						mappingSource['lookupMapping']['sheetColumnId'] = col['id']
					else:
						# check if column is output column
						for outMap in mappingSource['outputMappings']:
							if outMap['sheetColumn'] == col['title']:
								outMap['sheetColumnId'] = col['id']

				if 'sheetColumnId' not in mappingSource['lookupMapping'] and 'sheetColumn' in mappingSource['lookupMapping']:
					logger.error('Lookup column {} not found in sheet {}'.format(mappingSource['lookupMapping']['sheetColumn'], theSheet['name']))
					theConfig.endBadly()

				for outM in mappingSource['outputMappings']:

					if 'sheetColumnId' not in outM:
						logger.warning('Output column {} not found in sheet {}'.format(outM['sheetColumn'], theSheet['name']))
			for sheetRow in theSheet['rows']:
				sourceMatch = [] # init sourceMatch
				cellsPayload = [] # init payload
				updateRowUrl = getSheetUrl + '/rows/' + str(sheetRow['id'])

				for mappingSource in mapping['sources']:
					logger.info('Source: {}'.format(mappingSource['sourceId']))

					for source in sourceConfigs:
						if source['sourceId'] == mappingSource['sourceId']:
							currentSource = source
							break
					if 'lookupByRowId' in mappingSource['lookupMapping'] and mappingSource['lookupMapping']['lookupByRowId'] == True:
						# lookup by rowId
						cellsPayload.extend(theMatch.findMatch(sheetRow['id'], theSheet['name'], currentSource, mappingSource, mappingSource['lookupMapping']['sourceKey'], logger))
					else:
						for cell in sheetRow['cells']:
							# find lookup value match
							if cell['columnId'] == mappingSource['lookupMapping']['sheetColumnId']:

								if 'displayValue' in cell:
									cellsPayload.extend(theMatch.findMatch(cell['displayValue'], theSheet['name'], currentSource, mappingSource, mappingSource['lookupMapping']['sourceKey'], logger))
				
				if len(cellsPayload):
					payload = { 'cells': cellsPayload }
					attempt = 0
					updateResponse = sendUpdate(updateRowUrl, data=json.dumps(payload), headers=headers, attempt=attempt)
					# output api response
					try:
						if updateResponse.status_code == 200:
							logger.info('Sheet {} Updated'.format(theSheet['name']))
						else:
							logger.warning('updateResponse: {}'.format(updateResponse.text))
					except AttributeError:
						logger.error(updateResponse)
		logger.info('===Smartsheet Data Tracker Utility Completed: {}'.format(str(datetime.datetime.now()).split('.')[0]))
	else:
		logger.error('There are no mappings configured. Please add a properly formatted mapping node to the mapping.json file.')

def sendUpdate(updateUrl, data, headers, attempt):
	try:
		# send update to smartsheet for each row
		updateResponse = requests.put(updateUrl, data=data, headers=headers)
	except requests.exceptions.ConnectionError, error_message:
		time.sleep(3)
		# send update to smartsheet for each row
		updateResponse = sendUpdateRetry(updateUrl, data, headers, attempt, error_message)
	return updateResponse

def sendUpdateRetry(updateUrl, payload, headers, attempt, exception):
	maxAttempts = 3
	response = {}

	print 'updateRetry'
	if attempt < maxAttempts:
		attempt = attempt + 1
		response = sendUpdate(updateUrl, payload, headers, attempt)
	else:
		response = exception
	return response


if __name__ == '__main__':
	main()
