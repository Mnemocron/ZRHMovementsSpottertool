#!/bin/bash

cd /home/pi/workspace/zrh

rm timetable.arrival.spotter.json
rm timetable.arrival.standard.json
rm timetable.departure.spotter.json
rm timetable.departure.standard.json
rm timetable.arrival.tom.spotter.json
rm timetable.arrival.tom.standard.json
rm timetable.departure.tom.spotter.json
rm timetable.departure.tom.standard.json

./zrh-fix-working-beta.py
./zrh-fix-2day.py

./spotter-sort.py timetable.arrival.standard.json timetable.arrival.spotter.json | awk '!x[$0]++' > temparrtod.txt
./spotter-sort-tom.py timetable.arrival.tom.standard.json timetable.arrival.tom.spotter.json | awk '!x[$0]++' > temparrtom.txt

cat temparrtod.txt temparrtom.txt > temparr.txt

./spotter-sort.py timetable.departure.standard.json timetable.departure.spotter.json | awk '!x[$0]++' > tempdeptod.txt
./spotter-sort-tom.py timetable.departure.tom.standard.json timetable.departure.tom.spotter.json | awk '!x[$0]++' > tempdeptom.txt

cat tempdeptod.txt tempdeptom.txt > tempdep.txt
