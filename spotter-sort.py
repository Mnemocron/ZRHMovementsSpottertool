#!/usr/bin/python

'''
@file 			zrh-filter.py
@brief 			download arrivals and departures from ZRH (Airport Zurich)
@author 		Simon Burkhardt - simonmartin.ch - github.com/mnemocron
@author 					    - dxmek.ch - github.com/dxmek
@date 			2017-08-01
@description 	made for use with Python 2.7.9
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
		json_regular = json.load(stdFile)
	with open(opts.spt) as sptFile:
		json_spotter = json.load(sptFile)
except :
	print('[' + bcolors.FAIL + '-' + bcolors.ENDC + '] Error: Cannot parse json file')
	exit(-1)

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

# JSON object
json_special = {}
json_special['timetable'] = []

if ( opts.out is not None ) :
	if ( os.path.exists(opts.out) and os.path.isdir(opts.out) ):
		outname = (opts.out + '/').replace('//', '/') + outname
		try :
			if ( os.path.exists(outname) ) :
				os.remove(outname)
			outfile = open(outname, "w")
		except Exception, ex :
			print('[' + bcolors.FAIL + '-' + bcolors.ENDC + '] Error creating an outfile: ' + str(ex))
			exit(-3)

# compare the flights from the two files
for i in range( len(json_spotter["timetable"])-1 ) :	# compare every spotter flight...
	is_special = 1	# default true until proven otherwise
	for k in range( len(json_regular["timetable"])-1 ) :		# ...against every regular flight
		if ( json_spotter["timetable"][i]["flightcode"].lower() == json_regular["timetable"][k]["flightcode"].lower() ) :
			# print (str(i) + " " + json_spotter["timetable"][i]["flightcode"] + " " + json_spotter["timetable"][i]["scheduled"] + " " + json_spotter["timetable"][i]["masterflight"]["registration"] + " " + json_spotter["timetable"][i]["airportinformation"]["airport_city"] + " - EQUALS - " + str(k) + " " + json_regular["timetable"][k]["flightcode"] + " " + json_regular["timetable"][k]["scheduled"] + " " + json_regular["timetable"][k]["masterflight"]["registration"] + " " + json_regular["timetable"][k]["airportinformation"]["airport_city"])
			is_special = 0
			k = len(json_regular["timetable"])		# abort second loop
	if (is_special == 1) :
		try :
			if ( opts.verb is True ) :
				print (json_spotter["timetable"][i]["flightcode"] + " - " + json_spotter["timetable"][i]["scheduled"] + " - " + json_spotter["timetable"][i]["masterflight"]["registration"] + " - " + json_spotter["timetable"][i]["airportinformation"]["airport_city"])
		except:	# if the "registration" element is missing, print a N/A
			try :
				print (json_spotter["timetable"][i]["scheduled"] + "\t" + "\t" + "N/A" + "\t" + "\t")
			except :
				print ("unhandled error with this flight")
		json_special['timetable'].append({})
		siz = len(json_special['timetable'])-1
		json_special['timetable'][siz] = json_spotter['timetable'][i]

# write JSON data to file
outfile.write( json.dumps(json_special) )

