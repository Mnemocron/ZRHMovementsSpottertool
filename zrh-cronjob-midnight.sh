#!/bin/bash

cd /home/pi/workspace/zrh

rm timetable.arrival.spotter.json
rm timetable.arrival.standard.json
rm timetable.departure.spotter.json
rm timetable.departure.standard.json

./zrh-fix-midnight.py

./spotter-sort.py timetable.arrival.standard.json timetable.arrival.spotter.json | awk '!x[$0]++' > temparrtod.txt

./spotter-sort.py timetable.departure.standard.json timetable.departure.spotter.json | awk '!x[$0]++' > tempdeptod.txt
