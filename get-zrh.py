#!/usr/bin/python
#_*_ coding: utf-8 _*_

'''
@file 			get-zrh.py
@brief 			download arrivals and departures from ZRH (Airport Zurich)
@author 		Simon Burkhardt - simonmartin.ch - github.com/mnemocron
@author 					    - dxmek.ch - github.com/dxmek
@date 			2017-08-01
@description 	made for use with Python 2.7.9

@bug 			It seems like the last few flights appear twice in all the files.
				The problem is most likely at the determination of lastFlightFetched = True


@details		The ZRH website changed it's API from GET-requesting JSON-formated data
				to POST-requesting html data. To keep other scripts, which depend on the json format working,
				the JSON format is kept as an output format.
				Example:

				{
					'timetable':[{
					    'airportinformation': {
					        'airport_city': 'DUBLIN'
					    },
					    'flightcode': 'EI349',
					    'masterflight': {
					        'registration': 'EIDEN'
					    }, 
					    'scheduled': '20:05', 
					    'expected' : '20:20'
					},{
						[...]
					}
				}

'''

# ===== COLORS =====
# https://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
class bcolors:
	HEADER = '\033[95m'		# purple
	OKBLUE = '\033[94m'		# blue
	OKGREEN = '\033[92m'	# green
	WARNING = '\033[93m'	# yellow
	FAIL = '\033[91m'		# red
	ENDC = '\033[0m'		# white / reset
	BOLD = '\033[1m'		# bold
	UNDERLINE = '\033[4m'	# underline

# ===== MODULES =====
try:
	import optparse					# argument parser
	import sys 						# args
	import os 						# files, directories
	import datetime 				# time formats
#	import datetime as dt
	import httplib
	import urllib 					# urlencode strings
	import requests					# requesting webpages
	from bs4 import BeautifulSoup 	# parsing html
	import json 					# generating / reading json
except Exception, ex:
	print('[' + bcolors.FAIL + '-' + bcolors.ENDC + '] Error: ' + str(ex))
	exit(-1)

# ===== ARGUMENTS =====
parser = optparse.OptionParser('get-zrh')
parser.add_option('-a', '--arr', '--arrivals',   	action='store_true',	dest='arr', 	help='get the arrival table')
parser.add_option('-d', '--dep', '--departures', 	action='store_true',	dest='dep', 	help='get the departure table')
parser.add_option('-s', '--spot', '--spotter', 		action='store_true',	dest='spt',		help='[optional] get the full list including spotter flights')
parser.add_option('-u', '--all', 					action='store_true',	dest='all',		help='[optional] get both lists including regular flights and spotter flights')
parser.add_option('-t', '--tomorrow',				action='store_true', 	dest='tom', 	help='[optional] get the timetable of tomorrow')
(opts, args) = parser.parse_args()

if ( opts.arr is None and opts.dep is None ):
	parser.print_help()
	exit(0)

if ( opts.spt is True and opts.all is True ):
	print('[' + bcolors.FAIL + '-' + bcolors.ENDC + '] Error: both arguments -s and -u are set.' )
	exit(-2)

json_regular = {}
json_regular['timetable'] = []
json_spotter = {}
json_spotter ['timetable'] = []

# CSV string arrays
# Could be used to sort out the interesting flights within this script.
# Currently used to determine wether the last flight has been fetched or not.
flights_regular = []
flights_spotter  = []

# ToDo: Tested: headers seem to be not required
# Edit: Seems to be required sometimes
headers = { 'Host': 'www.zurich-airport.com',
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
		'Accept': '*/*',
		'Accept-Language': 'en-US,en;q=0.5',
		'Accept-Encoding': 'gzip, deflate, br',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'X-Requested-With': 'XMLHttpRequest',
		'Referer': 'https://www.zurich-airport.com/passengers-and-visitors/arrivals-and-departures/',
		'Content-Length': '85',
		'Cookie': 'sc_expview=0; website#lang=en; ASP.NET_SessionId=tewblvuqsehbozbq5yakat2n; __RequestVerificationToken=vIUKElZhB4SVQfWDXu2DyJAYluqyOAecVSwB5sDOniFyFMTvSZJnrZNudEVMbrRzvtLS1v2GurbyFTCScCMOME-ybd81; TS01cd1ab8=018735b6f7dff7a3e09286a67ae052f4e2011617ee8846a666a6630182514b91ee5552f129831d7f6267e740d9595f99ca9149393dae9ac848ae68b61d427320fffd9b5eb9890ba550276dd5bd9c357f6c979b7a89d7ebac45ad4fe23564114c99cdab08f117858652ebe1195e659af262baa071e0bbd6fc395fb0b81a1ebd6bfe2799de00bde795de96bab4b0a8b52993ab0995a2',
		'DNT': '1',
		'Connection': 'keep-alive' }

def getZRH(ftyp, fdat, get_spotters=False):
	if ftyp is 'Arrival':
		fname = 'timetable.arrival'
	elif ftyp is 'Departure':
		fname = 'timetable.departure'
	else:
		return

	# info message
	if ( get_spotters is True ) :
		print ( '[' + bcolors.OKGREEN + '+' + bcolors.ENDC + '] Fetching: ' + fname + '.spotter on ' + fdat)
	else :
		print ( '[' + bcolors.OKGREEN + '+' + bcolors.ENDC + '] Fetching: ' + fname + '.regular on ' + fdat)
	

	# The new API uses POST requests including the parameters !!!!!
	# https://stackoverflow.com/questions/3238925/python-urllib-urllib2-post

	# requesting the full flighttable could be done two ways:
	# - seting a time, and scroling the page until the next higher time is reached, then set the next time and continue
		# r_date   ---   yyyy-mm-dd
		# date_today = datetime.datetime.now().strftime('%Y-%m-%d') 
		# r_time   ---   time 06:00:00 to 22:00:00
		# for i in xrange(6, 23, 2): 				# from 6 to 23 in 2-steps
		#	print (str(i).zfill(2) +':00:00') 		# leading zero if hour is < 10 + 00:00
	# - seting the time to 04:00:00 UTC and just scroll the page all the way to the end (~20:00:00 UTC)

	r_tstart = '04:00:00'
	# r_now  = str( dt.datetime.now().hour )
	# r_time = (r_now + ':00:00')	# set time - 'HH:MM:SS'   ---   GMT/UTC format ! -> Swiss time 06:00:00 would be 04:00:00
	r_time = r_tstart
	r_page = str(0)					# set page number
	r_type = ftyp 	 				# Arrival / Departure
	r_sear = '' 					# search query - 'spotter' for spotter flights
	
	# clear / reinitialize arrays
	json_regular = {}
	json_regular['timetable'] = []
	json_spotter = {}
	json_spotter ['timetable'] = []
	flights_regular = []
	flights_spotter  = []
	
	if get_spotters is True :
		r_sear = 'spotter'
	lastFlightFetched = False
	page = 0
	while not lastFlightFetched :	# fetch every flight by scrolling through pages
		r_page = str(page)
		# body = 'startDateTime=2017-07-11T14%3A00%3A00.000Z&search=&page=0&__RequestVerificationToken='
		body = urllib.urlencode({'startDateTime' : fdat + 'T' + r_time + '.000Z', 'search' : r_sear, 'page' : r_page, '__RequestVerificationToken' : ''})
		# print (body) 				# debug
		
		requrl = 'https://www.zurich-airport.com/api/sitecore/FlightScheduleDetail/' + r_type + 'DetailData'
		
		try:
			response = requests.post(requrl, data=body, headers=headers)
		except requests.exceptions.ConnectionError :
			print('[' + bcolors.FAIL + '-' + bcolors.ENDC + '] Error: Could not connect. Check your internet settings.' )
			# exit(-3)
			return
		except Exception, ex:
			print('[' + bcolors.FAIL + '-' + bcolors.ENDC + '] Unknow Error: ' + str(ex) )
			exit(-4)

		parsed_html = BeautifulSoup(response.text, 'lxml') 				# parse html object with 'lxml'
		flighttable = parsed_html.find('div', attrs={'class', 'desktop-only'})

		if (page > 0):
			# check if the last flight of previous requests is inside the new request
			if   (get_spotters is True) and (flights_spotter[ len(flights_spotter)-1].split(';')[0] in flighttable) :
				lastFlightFetched = True
			elif (get_spotters is False) and (flights_regular[len(flights_spotter)-1].split(';')[0] in flighttable) :
				lastFlightFetched = True
		if not lastFlightFetched:
			for flight in flighttable.tbody.findAll('tr') :
				try:
					f_code = '' 	# clear
					f_code =      flight.find('a', attrs={'class', 'main-code'}).text 				# flight code
					f_reg  = '' 	# clear
					f_reg  = str( flight.find('a', attrs={'class', 'main-code'}).get('title') ) 	# registration number nested in 'title'
					f_reg  = f_reg.split('number:')[1].split('<br')[0].strip()
					f_loc  = flight.find('div', attrs={'class', 'airport'}).contents[0].strip() 	# location airport
					f_time = flight.find('td', attrs={'class', 'plan'}).text.replace('\n', '') 		# scheduled time
					f_texp = flight.find('td', attrs={'class', 'plan ext'}).text.replace('\n', '') 	# expected time
					f_airc = str( flight.find('a', attrs={'class', 'main-code'}).get('title') )
					f_airc = f_airc.split('Typ')[1].strip().replace(':', '').replace('e ', '')
					# print (f_code + '  \t' + f_reg + ' \t' + f_loc + ' \t' + f_time + '/' + f_texp)
					if (get_spotters is True) :
						flights_spotter.append (f_code +';'+ f_reg +';'+ f_loc +';'+ f_time +';'+ f_texp +';'+ f_airc) 	# append to CSV string
						json_spotter['timetable'].append({})
						siz = len(json_spotter['timetable'])-1
						json_spotter['timetable'][siz]['airportinformation'] = {}
						json_spotter['timetable'][siz]['airportinformation']['airport_city'] = f_loc
						json_spotter['timetable'][siz]['flightcode'] = f_code
						json_spotter['timetable'][siz]['masterflight'] = {}
						json_spotter['timetable'][siz]['masterflight']['registration'] = f_reg
						json_spotter['timetable'][siz]['masterflight']['aircrafttype'] = f_airc
						json_spotter['timetable'][siz]['scheduled'] = f_time
						json_spotter['timetable'][siz]['expected'] = f_texp
					else :
						flights_regular.append(f_code +';'+ f_reg +';'+ f_loc +';'+ f_time +';'+ f_texp +';'+ f_airc) 	# append to CSV string
						json_regular['timetable'].append({})
						siz = len(json_regular['timetable'])-1
						json_regular['timetable'][siz]['airportinformation'] = {}
						json_regular['timetable'][siz]['airportinformation']['airport_city'] = f_loc
						json_regular['timetable'][siz]['flightcode'] = f_code
						json_regular['timetable'][siz]['masterflight'] = {}
						json_regular['timetable'][siz]['masterflight']['registration'] = f_reg
						json_regular['timetable'][siz]['masterflight']['aircrafttype'] = f_airc
						json_regular['timetable'][siz]['scheduled'] = f_time
						json_regular['timetable'][siz]['expected'] = f_texp
				except Exception:
					# two possible error cases, 
					# 'No Result' when the there are no further pages
					# 'No flights' when there was something wrong with the search query
					if ('No Result' in flight.text or 'No flights' in flight.text):
						lastFlightFetched = True
					else:
						print (flight) 			# debug
						print (body)
		page += 1
		
	if ( get_spotters is True ) :
		with open(fname + '.spotter.json', 'w') as outfile:
			json.dump(json_spotter, outfile)
	else :
		with open(fname + '.regular.json', 'w') as outfile:
			json.dump(json_regular, outfile)

	'''
	# optional - print flight table from CSV string
	for i in range( len(flights_spotter) ):
		if ( flights_spotter[i] not in flights_regular ):
			print flights_spotter[i].replace(';', ' - ') 
	'''

# ===== MAIN =====
def main():
	try:
		if ( opts.tom is True ) :
			date_to_get = ( datetime.date.today() + datetime.timedelta(days=1) ).strftime('%Y-%m-%d')
		else :
			date_to_get = ( datetime.date.today() ).strftime('%Y-%m-%d')
		if ( opts.all is True ) :
			if ( opts.arr is True ) :
				getZRH('Arrival', date_to_get)
				getZRH('Arrival', date_to_get, True)
			if ( opts.dep is True ) :
				getZRH('Departure', date_to_get)
				getZRH('Departure', date_to_get, True)
		elif ( opts.spt is True ):
			if ( opts.arr is True ) :
				getZRH('Arrival', date_to_get, True)
			if ( opts.dep is True ) :
				getZRH('Departure', date_to_get, True)
		else :
			if ( opts.arr is True ) :
				getZRH('Arrival', date_to_get)
			if ( opts.dep is True ) :
				getZRH('Departure', date_to_get)

		exit(0)
	# enables abortion of the program through CTRL + C
	except KeyboardInterrupt:
		print('')
		exit(0)

if __name__ == '__main__':
	main()
