#Smartsheet Data Tracker
A command line application that updates an existing sheet with data from external sources.

##Purpose

The Smartsheet Data Tracker is an application that uses one or more external data sources to update existing rows in a Smartsheet with values determined by a lookup column in the sheet.

###Revision History

2.3 - Feb 12, 2014. Added to Jira connector to support searching of custom fields, allowing search by sheet row ID. Restructured connector classes to give each connector its own file. 

2.2 - Jan 24, 2014. Added GET REST connector for Jira Issues.

2.1 - Jan 22, 2014. Added GET REST connector for Desk.com Cases.

2.0 - Jan 2, 2014. Added connectors for MySQL, OpenLDAP, and REST GET. Refactored  config files for better readability.

1.0 - Dec 5, 2013. Baseline application that works with CSV files. 

###Use Case

Let’s assume your goal is to keep a sheet updated based on changes in two external CSV files - one from an employee directory and another from an issue tracking system. The Data Tracker uses values from the sheet to search for matches in the given employees.csv and issues.csv files, and then maps the results with the columns in the sheet. 

A simple example of this scenario is illustrated in the diagram below. The yellow indicates the lookup values (such as unique user or record IDs) which are expected by the Data Tracker to be in your sheet, and are used to find matching records in the external system. The red indicates where the values from the matching records will be placed on the sheet.

![Data Tracker Mappings Illustration](https://googledrive.com/host/0Bx6R6UA4-C6zc2NrcVZVQVNRR28/mappings4.png)

###Smartsheet API

The Smartsheet Data Tracker utilizes the Smartsheet API, which provides a REST interface to Smartsheet features and data. The API enables Smartsheet customers to programmatically access and manage their data, and empowers application developers to build solutions on top of Smartsheet.

For more information about the Smartsheet API, please visit [the Smartsheet Developer Portal](http://www.smartsheet.com/developers) for full[ API Documentation](http://www.smartsheet.com/developers/api-documentation) and[ sample applications](https://www.smartsheet.com/developers/apps).


###Dependencies

The Data Tracker application was built and tested using Python 2.7.5, and depends on the libraries listed in the next section.

**Requests** -- In addition to the standard Python libraries this application requires the "requests" library that is available at [http://docs.python-requests.org/en/latest/](http://docs.python-requests.org/en/latest/)

**MySQL-Python** -- To use the MySQL connector, the MySQL-Python library is required. 

In order for the library to compile it will need access to an instance of MySQL, as well as the MySQL developer libraries. If using apt-get on any Debian-based distribution, such as Ubuntu, you would run the following three commands:

	sudo apt-get install mysql-server
	sudo apt-get install libmysqlclient-dev
	sudo pip install mysql-python

If you don’t plan on using the MySQL connector, simply don't reference the MySQLSource class in the `sources.json` file.
More information on MySQL-Python can be found at the project web site: [http://mysql-python.sourceforge.net/](http://mysql-python.sourceforge.net/)

**python-ldap** -- Connecting to OpenLDAP requires the python-ldap library. In order to compile the module you’ll need to have the development files for OpenLDAP. On Ubuntu you can get these files with the following:

	sudo apt-get install python-dev libldap2-dev
	sudo pip install python-ldap

If you don’t plan on using the OpenLDAP connector, simply don't reference the OpenLDAPSource class in the `sources.json` file. More information on python-ldap can be found at the project web site:  [http://python-ldap.org/](http://python-ldap.org/)

##Installation

The application runs locally on any system that can access the Smartsheet API. On a Unix/Linux based system a good place to install the dataTracker folder is in the ‘/opt/’ directory. If that directory doesn’t already exist, create it with the following command in the command line: 

	sudo mkdir /opt

Now place the dataTracker directory in the ‘opt’ directory. 

The dataTracker directory includes:

* **main.py** -- primary application script. This is the main file that runs the application.
* **settings directory**
	* **app.json** -- configuration settings for the whole application
	* **mapping.json** -- configuration file that maps values in the external source to the sheet
	* **sources.json** -- configuration file that holds information about each source that the application queries. 
* **connectors directory**
	* **CSVCon.py** -- Python class file that houses CSV external connector
	* **MySQLCon.py** -- Python class file that houses MySQL external connector
	* **OpenLDAPCon.py** -- Python class file that houses OpenLDAP external connector
	* **RestGETCon.py** -- Python class file that houses generic REST GET external connector
	* **RestGETDeskCon.py** -- Python class file that houses Desk.com REST GET external connector
	* **RestGETJiraCon.py** -- Python class file that houses Jira REST GET external connector
* **utils directory**
	* **config.py** -- a utility class that deals with app configurations
	* **match.py** -- a utility class that processes matches and prepares them to send to Smartsheet API 
* **sampleData directory**
	* **employees.csv** -- example CSV source file
	* **issues.csv** -- example CSV source file

##Configuration

###Generate API Access Token

For the Data Tracker application to access Smartsheet, an API Access Token will need to be generated via your Smartsheet account. Please review the Smartsheet API documentation section on how to [generate a Smartsheet Access Token](http://www.google.com/url?q=http%3A%2F%2Fwww.smartsheet.com%2Fdevelopers%2Fapi-documentation%23h.5osh0dl59e5m&sa=D&sntz=1&usg=AFQjCNFv3Ithnb6Ghc_ynWko0jASYkGq3A).

When the token is generated, copy and paste it into the `app.json` file as value for accessToken:

	"accessToken" = “your_token_here”,

###Set App Level Configs

General settings for the whole application are kept in the `app.json` file, and look like:

	{
		"accessToken": "your_token_here",
		"apiURL": "https://api.smartsheet.com/1.1",
		"logLevel": "logging.WARNING",
		"logFileName": "dougFir.log",
		"logFileMaxBytes": 10000,
		"logFileBackupCount": 10
	}

Brief description of the attributes:

* **accessToken** -- Smartsheet API access token. See the next section called ‘Generate API Access Token’ for instructions on how to create your token
* **apiURL** -- url of the Smartsheet API
* **logLevel** -- level of logging output
* **logFileName** -- name of the file for the log. Leave blank if you want to see the logging output in command line
* **logFileMaxBytes** -- the max size of a single log file. Once the file reaches this size the logger will create a new file.
* **logFileBackupCount** -- max number of log files to keep. Once the logger creates this many files the oldest will be deleted, and this number of files will remain


Next, you’ll need to configure the application to use your sources and map the values from those sources to the appropriate columns in a sheet.

###Pick a Connector
Now you'll need to pick a connector create a source that will update your sheet. Currently, the Smartsheet Data Tracker contains the following connectors to create a source:
 
* [REST GET](#restGetSourceRef)
* [REST GET Desk.com](#restGetDeskSourceRef)
* [REST GET JIRA](#restGetJiraIssueSourceRef)
* [MySQL](#mysqlSourceRef)
* [OpenLDAP](#openLdapSourceRef)
* [CSV](#csvSourceRef)

You can also [create your own](#createOwnCon) connector.
 

###Configure Source
Each source is configured in the `sources.json` file. The following are a couple of examples of typical source configurations using the [MySQL](#mysqlConRef) and the [REST GET Desk.com](#restGetDeskConRef) connectors:

**MySQL**

	{
		"sourceId": "productDB",
		"connectorClassName": "MySQLCon",
		"dbServer": "localhost",
		"dbUser": "root",
		"dbPassword": "root",
		"dbName": "dvDB",
		"lookupQuery": "SELECT sku,name,description,price,quantity FROM product WHERE sku = %s",
		"isStrict": false
	}

**REST GET Desk.com**

	{
		"sourceId": "deskAPI",
		"connectorClassName": "RestGETDeskCon",
		"apiUrl": "https://yourOrg.desk.com/api/v2/cases/{}",
		"username": "yourUsername",
		"password": "yourPassword",
		"isArray": false,
		"isStrict": false
	}

Refer to the [Source Reference](#sourceRef) section for a detailed description of each source and its available fields.
 
###Mappings
Now you'll need to map the data that is returned from the sources to columns in the sheet. The `mappings.json` file contains mappings for each of the sheets updated by the Smartsheet Data Tracker. In this file the columns from the external system, or source, are mapped to corresponding columns in the sheet. 

The following are examples of different types of mapping nodes found in the `mappings.json` file, covering the most common mapping cases. 

This first mapping example shows the most common use of `sourceKey`, assigning it to a key name. This method is used when a source - such as an API or OpenLDAP - return an array of key-value pairs, and the key names can be assigned to `sourceKey` as follows:

	{
		"sourceId": "jiraIssueAPI",
		"lookupMapping": {
			"sourceKey": "key",
			"sheetColumn": "Issue ID"
		},
		"outputMappings": [
			{
				"sourceKey": "statusName",
				"sheetColumn": "Status"
			},
			{
				"sourceKey": "summary",
				"sheetColumn": "Subject"
			}
		]
	}
	
In situations where the source returns an indexed array of values, such as with a CSV source, the `sourceKey` uses the index position of the value it's mapping to, like so:

	{
		"sheetId": 1234567890123456,
		"sources": [
			{
				"sourceId": "employees",
				"lookupMapping": {
					"sourceKey": 0, 
					"sheetColumn": "UserId"
				},

				"outputMappings": [
					{
						"sourceKey": 2,
						"sheetColumn": "Department"
					},
					{
						"sourceColumnIndex": 1,
						"sheetColumn": "Email"
					}
				]
			}
		]
	}

Each mapping configuration is made up of the following attributes:

* **sheetId** -- The id of the sheet to be updated. There are two ways to find a sheet’s ID.

    * To find the Sheet ID through the Smartsheet UI click on the dropdown arrow on the sheet tab, and go to Properties:

    * ![Sheet Properties](https://googledrive.com/host/0Bx6R6UA4-C6zc2NrcVZVQVNRR28/sheetProperties.png) 

    * The sheet ID can also be found by [using the GET SHEET method](http://www.smartsheet.com/developers/api-documentation#h.4930jur8qsvs) through the [Smartsheet API.](http://www.smartsheet.com/developers/api-documentation)

* **sources**
    * **name** -- name of the source set in the sources.json file
    * **lookupMapping** -- maps the value in the source file with the lookup value in the sheet
        * **sourceKey** -- the name or index position of the lookup value in the source record:
        * ![sourceKey Illustration](https://googledrive.com/host/0Bx6R6UA4-C6zc2NrcVZVQVNRR28/sourceKey.png)
        * **sheetColumn** -- the name of the sheet column that contains the lookup value 
    * **outputMappings** -- maps which values in the source update which cells in the sheet. 
        * **sourceKey** -- the name or position in the source record of the value to send to sheet
        * **sheetColumn** -- the name of the sheet column that will be updated with the `sourceKey` value

##Run
Now with everything configured, you can run the application with the following command:

	python main.py


##Additional Features
###Search by Row (JIRA)
In addition to the REST GET JIRA Issue source, the JIRA connector can also support a source that searches by the row ID of a sheet. This comes in handy if a unique column value - such as the JIRA Issue key - is not available. For instance, in combination with a [Zapier](http://zapier.com) work flow that creates new JIRA Issues from new rows in a sheet - putting the row ID into a custom field for the JIRA Issue - using the row ID for the lookup value would allow for the Data Tracker to find the correct JIRA Issue.

An exmaple of the REST GET JIRA Search by Row source:

**REST GET JIRA Search Custom Field**

	{
		"sourceId": "jiraSearchAPI",
		"connectorClassName": "RestGETJiraCon",
		"apiUrl": "https://ourOrg.atlassian.net/rest/api/latest/search?jql={}~\"{}\"",
		"username": "yourUsername",
		"password": "yourPassword",
		"isArray": true,
		"isStrict": false
	}
	
To create a source that searches JIRA by row ID the following differences from the JIRA Get Issue source are required. For a full explanation on each of the fields please see the entry for [REST GET JIRA Issue](#restGetJiraIssueSourceRef):

* **connectorClassName** -- the Python class used to parse the source connector. Same class as [REST GET JIRA Issue](#restGetJiraIssueSourceRef) source connector.
* **apiUrl** -- URL of the JIRA Search API. The {} are placeholders for the sourceKey - which is the name of the JIRA custom field holding the sheet row ID - and the lookup value - which is the sheet row ID.
* **isArray** -- flag indicating whether the API response is an array. This should be set to true, as the response from the JIRA API will be an array.

To create a `lookupMapping` that will utilize this Search by Row source we add a boolean flag to lookupMapping for `lookupByRowId` in place of `sheetColumn`. The `sourceKey` value is the name of the custom field in JIRA that holds the `sheetRowID`, like so:
	
	"lookupMapping": {
		"lookupByRowId": true,
		"sourceKey": "Sheet_Row_ID"
	},


###Adding Columns

Each `outputMapping` represents a column in the sheet. To add additional columns to the update process, find the `sourceKey` in the source, the corresponding column name in the sheet, and simply create another `outputMappings` node with those values. 


###Setup to Run on Schedule

The Data Tracker application can be configured to automatically run on a schedule,.  Please refer to your system documentation for details on how to setup a scheduled job.  Here is how to add Data Tracker as a scheduled cron job on a UNIX/Linux system:

	sudo crontab -u root -e

This opens a [VI style](http://www.cs.colostate.edu/helpdocs/vi.html) editor. In the editor, press ‘i’ to insert the new job. A common cron job that would run the application every day at 1am would look like this:

	* 1 * * * python /opt/dataTracker/main.py

Each of the asterisks represents a unit of time.  Starting with the most left position

* minute ( 0-59 ) -- the minute the job runs every hour
* hour ( 0-23 ) -- the hour the job runs every day
* day of the month ( 1-31 ) -- the day of the month the job runs every month
* month ( 0-12) -- the month the job runs every year
* day of week ( 0-6 ) ( 0 to 6 are Sunday to Saturday, or use names ) -- day the job runs each week

To have the cron job send an email of the application output each time it runs add the following line to the top of the crontab file:

	MAILTO="your.email@yourdomain.com"
		
When you’re done editing hit the ‘esc’ key and then type :wq to save and close the crontab file.


<a href name="sourceRef"></a>
##Source Reference
<a href name="csvSourceRef"></a>
###CSV

This CSV source uses the CSVCon connector to search the rows of a specified CSV file for the lookup value.  An example of a source node for a CSV source called "employees" looks like this:

	{
		"sourceId": "employees",
		"connectorClassName": "CSVCon",
		"fileName":"employees.csv",
		"isStrict": false
	}

Brief description of each of the configuration settings: 

* **sourceId** -- a descriptive name that will help you identify the source 
* **connectorClassName** -- the connector class used to parse the source
* **fileName** -- name of the CSV file
* **isStrict** -- setting that tells the Smartsheet API to be strict or lenient with cell validation. This setting is optional for each source, and is set to false by default if not specified in the source configuration settings. 

<a href name="mysqlSourceRef"></a>
###MySQL

This MySQL source uses the MySQLCon connector to query the given database with the value of the lookupQuery setting, and then maps the results of the first record returned with the output mapping columns in the sheet. The configuration for the MySQL looks like this:

	{
		"sourceId": "productDB",
		"connectorClassName": "MySQLCon",
		"dbServer": "localhost",
		"dbUser": "root",
		"dbPassword": "root",
		"dbName": "dvDB",
		"lookupQuery": "SELECT sku,name,description,price,quantity FROM product WHERE sku = %s",
		"isStrict": false
	}

Brief description of each of the configuration settings: 

* **sourceId** -- a descriptive name that will help you identify the source 
* **connectorClassName** -- the connector class used to parse the source
* **dbServer** -- location of MySQL database server
* **dbUser** -- username for MySQL user
* **dbPassword** -- password for MySQL user
* **dbName** -- database name 
* **lookupQuery** --  SQL query for getting the output values based on the lookup value. The `%s` denotes where the lookup value will be placed into the query.
* **isStrict** -- setting that tells the Smartsheet API to be strict or lenient with cell validation. This setting is optional for each source, and is set to false by default if not specified in the source configuration settings.

<a href name="openLdapSourceRef"></a>
###OpenLDAP

The OpenLDAP source uses the OpenLDAPCon connector to search a specified LDAP organizational unit for a given user, or cn. The configuration of the OpenLDAP source looks like this:

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

Brief description of each of the configuration settings: 

* **sourceId** -- a descriptive name that will help you identify the source 
* **connectorClassName** -- the class used to parse the source
* **ldapServer** -- location of LDAP server
* **baseDN** -- base distinguished name on which the search is performed
* **orgUnit** -- organizational unit in the baseDN where the search is performed
* **adminUser** -- cn of the user that is performing the search
* **adminPass**-- password of the user performing the search
* **searchFilter** -- LDAP search filter. The {} denotes where the lookup value will go.
* **retrieveAttributes** -- an array of the attributes to return in LDAP search. Leave array blank to return all attributes
* **ldapTimeout** -- number of seconds before LDAP search times out. If set to a negative number, the search will never time out.
* **isStrict** -- setting that tells the Smartsheet API to be strict or lenient with cell validation. This setting is optional for each source, and is set to false by default if not specified in the source configuration settings.

<a href name="restGetSourceRef"></a>
###REST GET

The REST GET source uses the RestGetCon connector to call the given API and maps the returning JSON object’s top level attributes (or attributes of the first object in the array if isArray = true) to the appropriate columns in the sheet being updated. The configuration for this source looks like this:

	{
		"sourceId": "markitOnDemandAPI",
		"connectorClassName": "RestGETCon",
		"apiUrl":"http://dev.markitondemand.com/Api/v2/Quote/json?symbol={}",
		"isArray": false,
		"isStrict": false
	}

Brief description of each of the configuration settings: 

* **sourceId** -- a descriptive name that will help you identify the source
* **connectorClassName** -- the connector class used to parse the source
* **apiUrl** -- URL of API. The {} denotes where the lookup value will go inside of the URL.
* **isArray** -- flag indicating whether the API response is an array
* **isStrict** -- setting that tells the Smartsheet API to be strict or lenient with cell validation. This setting is optional for each source, and is set to false by default if not specified in the source configuration settings.

<a href name="restGetDeskSourceRef"></a>
###REST GET Desk.com Cases

	{
		"sourceId": "deskAPI",
		"connectorClassName": "RestGETDeskCon",
		"apiUrl": "https://yourOrg.desk.com/api/v2/cases/{}",
		"username": "yourUsername",
		"password": "yourPassword",
		"isArray": false,
		"isStrict": false
	}
Brief description of each of the configuration settings: 

* **sourceId** -- a descriptive name that will help you identify the source
* **connectorClassName** -- the connector class used to parse the source
* **apiUrl** -- URL of API. The {} denotes where the lookup value will go inside of the URL.
* **username** -- username for Desk.com
* **password** -- password for Desk.com
* **isArray** -- flag indicating whether the API response is an array
* **isStrict** -- setting that tells the Smartsheet API to be strict or lenient with cell validation. This setting is optional for each source, and is set to false by default if not specified in the source configuration settings.

<a href name="restGetJiraIssueSourceRef"></a>
###REST GET JIRA Issue
	
	{
		"sourceId": "jiraIssueAPI",
		"connectorClassName": "RestGETJiraCon",
		"apiUrl": "https://yourOrg.atlassian.net/rest/api/latest/issue/{}",
		"username": "yourUsername",
		"password": "yourPassword",
		"isArray": false,
		"isStrict": false
	}
Brief description of each of the configuration settings: 

* **sourceId** -- a descriptive name that will help you identify the source
* **connectorClassName** -- the class used to parse the source
* **apiUrl** -- URL of API. The {} denotes where the lookup value will go inside of the URL.
* **username** -- username for JIRA
* **password** -- password for JIRA
* **isArray** -- flag indicating whether the API response is an array
* **isStrict** -- setting that tells the Smartsheet API to be strict or lenient with cell validation. This setting is optional for each source, and is set to false by default if not specified in the source configuration settings.

For ease of use, the RestGETJiraCon connector flattens the multi-layered JSON response returned by the JIRA API. For example, the `issue` endpoint returns an `assignee` object that looks like this:

	"assignee": {
		"displayName": "Zachary Taylor"
	}

After the response passes through the RestGETJiraCon connector in the Data Tracker, the flattened value will look like this:
	
	"assigneeDisplayname": "Zachary Taylor"
	
The following is a list of commonly used fields returned from JIRA, including some examples of flattened fields.

**Example of Fields Returned from JIRA**
 
assigneeDisplayname, assigneeEmailaddress, created, creatorName, creatorEmail, description, dueDate, issuetypeName, issuetypeDescription, key, lastViewed, priority, projectName, projectKey, progress, progressTotal, reporterDisplayname, reporterEmailaddress, resolution, self, status, summary, timeoriginalestimate, timeSpent, updated, votesVotes (not a typo. this is the format the API returns the key for the number of votes cast for the issue)

For a [full list of fields](https://docs.atlassian.com/jira/REST/latest/#d2e2892) available from the JIRA API, please refer to the [JIRA API documentation](https://docs.atlassian.com/jira/REST/latest/#d2e2892).

<a href name="createOwnCon"></a>
###Create Your Own
Additional connectors can be created to support any data source, public or private. To create a new connector create a connector Python module in the `connectors` directory.  The connector class should follow the same structure as the other connector classes. Namely, the new class should include the following function signatures:

	def __init__(self, sourceConfig):
		# validates the sourceConfig
	
	def findSourceMatch(self, lookupVal, lookupKey):
		# queries source and returns matchingRecord`

To use a new source in the Data Tracker application, a sourceConfig entry in the `sources.json` file will need to be created for the class. Each sourceConfig node must have a sourceId attribute set to a unique value, as well as a connectorClassName attribute that is set to the name of the new connector class.


##Help and Contact

If you have any questions or suggestions about this document, the application, or about the Smartsheet API in general please contact us at api@smartsheet.com. Development questions can also be posted to[ Stackoverflow](http://stackoverflow.com/) with the tag[ smartsheet-api](http://stackoverflow.com/questions/tagged/smartsheet-api).

***The Smartsheet Platform team***

##License

	Copyright 2014 Smartsheet, Inc.

	Licensed under the Apache License, Version 2.0 (the
	"License"); you may not use this file except in compliance
	with the License. You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing,
	software distributed under the License is distributed on an
	"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
	either express or implied. See the License for the specific
	language governing permissions and limitations under the
	License.             

[![githalytics.com alpha](https://cruel-carlota.pagodabox.com/3927b6507d54b58d0025f56d53b752fd "githalytics.com")](http://githalytics.com/smartsheet-platform/Smartsheet-Data-Tracker)
