from bs4 import BeautifulSoup
import urllib
import pdftables_api
from secrets import pdftables_key
import csv
import xml.etree.ElementTree as ET
import sqlite3

r = urllib.urlopen('https://www.scotrail.co.uk/performance-and-reliability').read()
soup = BeautifulSoup(r, "html.parser")

links = soup.findAll('a')
file_name = ""
downfile = ""
target = ""
no_suffix = ""

for link in links:
	title = link.get('title')
	if title == "Download our monthly performance results":
		target = str(link.get('href'))

		url_chunks = target.split("/")
		atpos = len(url_chunks)
		file_name = url_chunks[atpos - 1:][0]
		no_suffix = file_name.split(".")[0]

#uncomment the following line to download the file
urllib.urlretrieve (target, file_name)

#uncomment the next two lines to send the file for conversion
c = pdftables_api.Client(pdftables_key)
c.csv(file_name, no_suffix + ".csv") # Note: change each 'csv' to 'xslx' or 'xml' as wanted

written_name = no_suffix+".csv"

#work out the year and period from the file name
no_suffix = file_name.split(".")
dashes = no_suffix[0].split("-")
year = dashes[2].split("p")[1]
period = dashes[3]

# open the downloaded CSV version of the file 
# run through it extracting the data we need
# create a nested lists, the inner list with performance data
# for each individual station 

f = open(written_name)
csv_f = csv.reader(f)

start_date = ""
end_date = ""

count_line = -1

all_stations = []
one_station = []

for line in csv_f:
	count_line += 1
	if count_line == 0:
		# code for 1st line

		for cell in line:

			if cell [:18] == "Performance Update":
				bits = cell.split()
				start_date =  bits [2]
				end_date = bits [4]

	elif count_line == 1:
		#code for second line   <== to be done !!!!!!
		pass
	else:
		if count_line > 18 and count_line < 55:
			
			for x in [0, 3,4, 5, 6]:
				if x in [3,5,6]:
					one_station.append(float(line[x][0:len(line[x])-1]))
				elif x == 0:
					one_station.append(line[x])
				else:
					one_station.append(int(line[x]))

			all_stations.append(one_station)
			one_station = []
			
			for x in [7, 8,9, 10, 11]:
				if x in [8,10,11]:
					one_station.append(float(line[x][0:len(line[x])-1]))
				elif x == 7:
					one_station.append(line[x])
				else:
					one_station.append(int(line[x]))
			
			all_stations.append(one_station)
			one_station = []
			

		if count_line == 55:
			
			for x in [0, 3,4, 5, 6]:
				if x in [3,5,6]:
					one_station.append(float(line[x][0:len(line[x])-1]))
				elif x == 0:
					one_station.append(line[x])
				else:
					one_station.append(int(line[x]))

			all_stations.append(one_station)
			one_station = []

all_stations.sort()			


#Keep the following code for now - write out to a CSV. 
#Maybe keep this operation to act as a failsafe copy

file_out_name = 'y'+year + '_p'+period+'_output.csv'
f2 = open(file_out_name, 'w')

f2.write ('Year, Period, start, end, Location,On_Time_T(%),Booked_T,On_Time_A(%),PPM(%) \n')
for outer in all_stations:
	rec_count = 0
	f2.write (year +", " + period +", "+ start_date+', '+ end_date+', ')
	for inner in outer:
		f2.write (str(inner))
		if rec_count < 4:
			f2.write (',')
		rec_count += 1
	f2.write (' \n')	
	

f2.close()

# New - in v1.1 - writes the main data out to a SQLite Database


conn = sqlite3.connect('train_perf.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
# delete or comment out if you have existing data
# otherwise existing data will be discarded

cur.executescript ('''
DROP TABLE IF EXISTS Period;
DROP TABLE IF EXISTS Performance;


CREATE TABLE Period (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    year INTEGER,
    per_iod INTEGER,
    start_date TEXT,
    end_date TEXT
);

CREATE TABLE Performance (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    year INTEGER,
    period_id  INTEGER,
    station TEXT  UNIQUE,
    on_time_t FLOAT, 
    booked_t INTEGER, 
    on_time_a FLOAT, 
    ppm FLOAT
);
''')
# end sections to drop and delete tables

for outer in all_stations:
    rec_count = 0
    stn_name = outer[0]
    ott = outer[1]
    bt = outer[2]
    ota = outer [3]
    ppm = outer [4]

    
    cur.execute('''INSERT OR REPLACE INTO Performance
    (year, period_id, station, on_time_t, booked_t, on_time_a, ppm) 
    VALUES ( ?, ?, ?, ?, ?, ?, ? )''', 
    ( year, period, stn_name, ott, bt, ota, ppm ) )

conn.commit()