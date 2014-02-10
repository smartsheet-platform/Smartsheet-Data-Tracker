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

class Match:
	def __init__(self):
		return None

	def findMatch(self, lookupVal, sheetName, source, mappingSource, lookupKey, logger):
		payload = []

		logger.info('Searching source for value: {}'.format(lookupVal))

		# sourceMatch is the source record with the matching lookup value
		sourceMatch = source['sourceObject'].findSourceMatch(lookupVal, lookupKey)
		
		if len(sourceMatch):
			logger.info('Match Found')

			for outputMap in mappingSource['outputMappings']:
				# build put call
				# - columnId
				# - value
				logger.info('outputMap: {}'.format(outputMap))
				try:
					payload.append({'columnId': outputMap['sheetColumnId'], 'value': sourceMatch[outputMap['sourceKey']], 'strict':source['isStrict']})
				except KeyError, error_message:
					
					if str(error_message) == '\'sheetColumnId\'':
						logger.warning('The {} was not set for the sheetColumn: {} in source: {}. Verify the sheetColumn value matches the column title in sheet: {}'.format(error_message,outputMap['sheetColumn'],mappingSource['sourceId'],sheetName))
					else:
						logger.warning('The sourceKey of {} could not be found in the source {} for {}. {}'.format(outputMap['sourceKey'],mappingSource['sourceId'],lookupVal,error_message))
				except error_message:
						logger.warning(error_message)
		else:
			logger.info('No Match')	
		
		return payload