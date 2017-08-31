# ZRH Movements Spottertool

This Python script can fetch the full arrival / departure list of the Zürich airport (ZRH).
The output format is 'json'.
There multiple lists available. Both the arrivals and depatrures of regular civil flights,
as well as both the arrivals and departures of all available flights (including private and freight flights).
Typically a regular list contains ~400 flights per day, while a spotter list contains ~450 flights.

## Usage

### Download Timetables

Get the arrival list (today / regular):

`$ get-zrh.py -a`

Get the departure list (toady / regular):
`$ get-zrh.py -d`

Get all four available lists of today:
`$ get-zrh.py -dau`

Get all four available lists of tomorrow:
`$ get-zrh.py -daut`

### Filter Timetables

Filter out the special flights:

`$ spotter-sort.py -r [regular] -s [spotter] [-o][dir] [-v]`

Example:

`$ spotter-sort.py -r timetable.arrival.regular.json -s timetable.arrival.spotter.json -o ./flighttables`

The option `-o [dir]` is used to set the output directory (not filename) of the filtered timetable.json - 
if there is already a timetable.[x].special.json, this file will be overwritten

The option `-v` enables verbos output for further use. You can pipe this output to a Telegram chat for example.

## Output Format

The output format is a json file. The structure is taken from the old ZRH website API.

### Example:

```json
{
	"timetable":[{
		"airportinformation": {
			"airport_city": "DUBLIN"
		},
		"flightcode": "EI349",
		"masterflight": {
			"registration": "EIDEN"
		}, 
		"scheduled": "20:05", 
		"expected" : "20:20"
	},{
		"airportinformation": {
			"airport_city": ""
		},
		"flightcode": "",
		"masterflight": {
			"registration": ""
		}, 
		"scheduled": "", 
		"expected" : "0"
	}
}

```

## One more example

Online at <a href="http://dxmek.ch/zrharr/"></a>

## Dependencies

Python 2.7

Packages used:

- optparse
- sys
- os
- datetime
- httplib
- urllib 
- requests
- bs4 / BeautifulSoup 
- json 				
