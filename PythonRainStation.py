import requests
import urllib.parse
import json
import sys
import time
from datetime import datetime
from datetime import date
from collections import Counter
from geopy.geocoders import Nominatim
from geopy.distance import great_circle



##################Start of Python Methods for the script
 

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}	


def get_state_from_coordinates(coordinates, geolocator):
	rawLocationDataFromAddress = geolocator.reverse(coordinates, exactly_one=True)
	rawAddress = rawLocationDataFromAddress.raw['address']
	USstate = rawAddress.get('state', '')
	return USstate




def calculate_number_of_days_between_two_string_dates(earlyDate, lateDate):
		
	dateFormat = '%m-%d-%Y'
	earlyDateTimeObject = datetime.strptime(earlyDate, dateFormat)
	lateDateTimeObject = datetime.strptime(lateDate, dateFormat)
	
	earlyDayInteger = int(earlyDateTimeObject.strftime("%d"))
	lateDayInteger = int(lateDateTimeObject.strftime("%d"))
	
	earlyMonthInteger = int(earlyDateTimeObject.strftime("%m"))
	lateMonthInteger = int(lateDateTimeObject.strftime("%m"))
	
	earlyYearInteger = int(earlyDateTimeObject.strftime("%Y"))
	lateYearInteger = int(lateDateTimeObject.strftime("%Y"))
	
	earlyDateObject = date(earlyYearInteger, earlyMonthInteger, earlyDayInteger)
	lateDateObject = date(lateYearInteger, lateMonthInteger, lateDayInteger)
	
	dateDifference = lateDateObject - earlyDateObject
	
	if dateDifference.days < 0 :
		exit("Early date MUST be earlier than late date.  Try again.")
	
	return dateDifference.days
	
def get_lat_lng_from_user_chosen_address (geolocator,userChosenAddress):
	geoLocatedUserChosenAddress = geolocator.geocode(userChosenAddress)
	latLngFromUserChosenAddress = (geoLocatedUserChosenAddress.latitude, geoLocatedUserChosenAddress.longitude)
	return latLngFromUserChosenAddress 
	

def get_JSON_dict_from_URL_string(stateFromUserChosenAddress,userChosenEarlyDate,userChosenLateDate):
	urlRainfallRequestString = 'http://data.cocorahs.org/export/exportreports.aspx?ReportType=Daily&Format=JSON&State=' + stateFromUserChosenAddress +'&ReportDateType=reportdate&StartDate=' + userChosenEarlyDate + '&EndDate=' + userChosenLateDate
	responseObjectFromURLRainfallRequest = requests.get(urlRainfallRequestString)
	JSONStringFromRainfallResponseObject = responseObjectFromURLRainfallRequest.text	
	JSONRainfallDict = json.loads(JSONStringFromRainfallResponseObject)
	return JSONRainfallDict

	
	
def clean_list_of_rainfall_report_dictionaries_of_invalid_rainfall_amounts(listOfRainfallReportDictionaries): 
	for rainfallReportDictionary in listOfRainfallReportDictionaries:
		if rainfallReportDictionary['totalpcpn'] == -1.0:
			rainfallReportDictionary['totalpcpn'] = 0
	for rainfallReportDictionary in listOfRainfallReportDictionaries:
		if rainfallReportDictionary['totalpcpn'] == -2.0:
			listOfRainfallReportDictionaries.remove(rainfallReportDictionary)
	
	

##################### End of Methods for the Script

userChosenAddress = "1 Providence Pl, Providence, RI 02903"
userChosenEarlyDate = "10-13-2020"
userChosenLateDate = "10-14-2020"

geolocator = Nominatim(user_agent="rainfallApp")
latLngFromUserChosenAddress = get_lat_lng_from_user_chosen_address(geolocator,userChosenAddress)
stateFromUserChosenAddress = us_state_abbrev[get_state_from_coordinates(latLngFromUserChosenAddress,geolocator)]

JSONRainfallDict = get_JSON_dict_from_URL_string(stateFromUserChosenAddress,userChosenEarlyDate,userChosenLateDate)

listOfRainfallReportDictionaries = JSONRainfallDict['data']['reports']

clean_list_of_rainfall_report_dictionaries_of_invalid_rainfall_amounts(listOfRainfallReportDictionaries)


listOfRainfallReportDictionariesSortedByStationName = sorted(listOfRainfallReportDictionaries, key=lambda key: key['st_name']) 

		
totalPrecipForEachStationDictionary = {}
numberOfDaysStationInRainfallReportDictionary = {}
listOfStationPrecipTotalObjects = []


class stationPrecipTotal:
	def __init__(self, stationName, stationNumber,totalPrecip, lat, lng, distanceFromHomeStation):
		self.stationName = stationName
		self.stationNumber = stationNumber
		self.totalPrecip = totalPrecip
		self.lat = lat
		self.lng = lng
		self.distanceFromHomeStation = distanceFromHomeStation
	 
	 
numberDaysRequiredDaysForNoMissingDays = calculate_number_of_days_between_two_string_dates(userChosenEarlyDate,userChosenLateDate) + 1

for rainfallReportDictionary in listOfRainfallReportDictionariesSortedByStationName :
			numberOfDaysStationInRainfallReportDictionary[rainfallReportDictionary['st_num']] = numberOfDaysStationInRainfallReportDictionary.get(rainfallReportDictionary['st_num'],0) + 1
			totalPrecipForEachStationDictionary[rainfallReportDictionary['st_num']] = totalPrecipForEachStationDictionary.get(rainfallReportDictionary['st_num'],0) + rainfallReportDictionary['totalpcpn']
			if numberOfDaysStationInRainfallReportDictionary[rainfallReportDictionary['st_num']] == numberDaysRequiredDaysForNoMissingDays:
				stationLocation = (rainfallReportDictionary['lat'], rainfallReportDictionary['lng'])
				stationPrecipTotalObject = stationPrecipTotal(rainfallReportDictionary['st_name'],rainfallReportDictionary['st_num'],totalPrecipForEachStationDictionary[rainfallReportDictionary['st_num']],rainfallReportDictionary['lat'],rainfallReportDictionary['lng'],great_circle(stationLocation, latLngFromUserChosenAddress).miles)
				listOfStationPrecipTotalObjects.append(stationPrecipTotalObject)
print("")	



sortedlistOfStationPrecipTotalObjects = sorted(listOfStationPrecipTotalObjects, key=lambda stationPrecipTotal: stationPrecipTotal.distanceFromHomeStation) 

print("5 closest rainfall reports")
print(userChosenEarlyDate + " to " + userChosenLateDate )
print (userChosenAddress)
print("") 
for stationPrecipTotalObject in sortedlistOfStationPrecipTotalObjects[0:5]:
	print(stationPrecipTotalObject.stationNumber.ljust(12) +  stationPrecipTotalObject.stationName.ljust(30) + "    Precip Total: " + str(format(stationPrecipTotalObject.totalPrecip,'.2f')).ljust(7) + "  Distance Away: " + str(format(stationPrecipTotalObject.distanceFromHomeStation,'.2f')))
	
	


	
	
	

	
	

	

