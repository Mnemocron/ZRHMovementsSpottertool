#!/usr/bin/python

'''
@file 			zrh-filter.py
@brief 			download arrivals and departures from ZRH (Airport Zurich)
@author 		Simon Burkhardt - simonmartin.ch - github.com/mnemocron
@author 					    - dxmek.ch - github.com/dxmek
@date 			2017-08-01
@description 	made for use with Python 2.7.9
@todo 			use json library and dumps to generate the outfile
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
try :
	import optparse
	import json
	import sys
	import os
except Exception, ex :
	print('[' + bcolors.FAIL + '-' + bcolors.ENDC + '] Error: ' + str(ex))
	exit(-1)

# ===== ARGUMENTS =====
parser = optparse.OptionParser('spotter-sort')
parser.add_option('-r', '--regular',	dest='reg', 	help='-r [timetable.x.regular.json]')
parser.add_option('-s', '--spotter',	dest='spt', 	help='-s [timetable.x.spotter.json]')
parser.add_option('-v', '--verbose', 	dest='verb', action='store_true', help='print all the special flights for further use')
parser.add_option('-o', '--out-file', 	dest='out', help='[file] where to store the output file')
(opts, args) = parser.parse_args()

if ( opts.reg is None or opts.spt is None ) :
	parser.print_help()
	exit(0)

try :
	with open(opts.reg) as stdFile:
		jsonstd = json.load(stdFile)
	with open(opts.spt) as sptFile:
		jsonspot = json.load(sptFile)
except :
	print('[' + bcolors.FAIL + '-' + bcolors.ENDC + '] Error: Cannot parse json file')
	exit(-1)

'''
# find out if it is arrival or departure
if ( "arr" in sys.argv[1] ):
	print ("Zurich Airport ZRH - Arrivals")			# start output
	if os.path.exists("timetable.arrival.special.json"):
		os.remove("timetable.arrival.special.json")		# delete the outdated file
	webfile = open("timetable.arrival.special.json", "w")
elif ( "dep" in sys.argv[1] ):
	print ("Zurich Airport ZRH - Departures")
	if os.path.exists("timetable.departure.special.json"):
		os.remove("timetable.departure.special.json")
	webfile = open("timetable.departure.special.json", "w")

webfile.write("{\"timetable\":[")	# begin the json file
'''

# open the outfile for write
outname = 'timetable'
if   ( "arr" in opts.reg.lower() and "arr" in opts.spt.lower() ) :
	if (opts.verb is True ):
		 print ("Zurich Airport ZRH - Arrivals (Special)")
	outname = outname + '.arrival.special.json'
elif ( "dep" in opts.reg.lower() and "dep" in opts.spt.lower() ) :
	if ( opts.verb is True ) :
		print ("Zurich Airport ZRH - Departures (Special)")
	outname = outname + '.departure.special.json'
else :
	print('[' + bcolors.FAIL + '-' + bcolors.ENDC + '] Error: Could not determine the file status (arrival / departure)')
	exit(-2)

if ( opts.out is not None ) :
	if ( os.path.exists(opts.out) and os.path.isdir(opts.out) ):
		outname = (opts.out + '/').replace('//', '/') + outname
		try :
			if ( os.path.exists(outname) ) :
				os.remove(outname)
			webfile = open(outname, "w")
		except Exception, ex :
			print('[' + bcolors.FAIL + '-' + bcolors.ENDC + '] Error creating an outfile: ' + str(ex))
			exit(-3)


# compare the flights from the two files
for i in range( len(jsonspot["timetable"])-1 ) :	# compare every spotter flight...
	send = 1	# default: true until proven otherwise
	for k in range( len(jsonstd["timetable"])-1 ) :		# ...against every standard flight
		if ( jsonspot["timetable"][i]["flightcode"].lower() == jsonstd["timetable"][k]["flightcode"].lower() ) :
			# print (str(i) + " " + jsonspot["timetable"][i]["flightcode"] + " " + jsonspot["timetable"][i]["scheduled"] + " " + jsonspot["timetable"][i]["masterflight"]["registration"] + " " + jsonspot["timetable"][i]["airportinformation"]["airport_city"] + " - EQUALS - " + str(k) + " " + jsonstd["timetable"][k]["flightcode"] + " " + jsonstd["timetable"][k]["scheduled"] + " " + jsonstd["timetable"][k]["masterflight"]["registration"] + " " + jsonstd["timetable"][k]["airportinformation"]["airport_city"])
			send = 0
			k = len(jsonstd["timetable"])		# abort second for loop
	if (send == 1) :
		try :
			if ( opts.verb is True ) :
				print (jsonspot["timetable"][i]["flightcode"] + " - " + jsonspot["timetable"][i]["scheduled"] + " - " + jsonspot["timetable"][i]["masterflight"]["registration"] + " - " + jsonspot["timetable"][i]["airportinformation"]["airport_city"])
		except:	# if the "registration" element is missing, print a N/A
			try :
				print (jsonspot["timetable"][i]["scheduled"] + "\t" + "\t" + "N/A" + "\t" + "\t")
			except :
				print ("unhandled error with this flight")
		# dumps encodes the json string
		webfile.write( json.dumps(jsonspot["timetable"][i], indent=4, sort_keys=True) + ",")
# ugly way to terminate the json file
webfile.write("{\"null\":\"null\"}]}")

