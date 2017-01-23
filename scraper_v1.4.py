#!/usr/bin/python
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
monthly_pc = 0.0
annual_pc = 0.0

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
#no_suffix = file_name.split(".")
#code below changes in v1.4 as Scotrail changes the file naming from dashes to underscores
if "-" in no_suffix:
	dashes = no_suffix.split("-")
elif "_" in no_suffix:
	dashes = no_suffix.split("_")
else:
	 print "File name mismatch"

year = dashes[2].split("p")[1]

period = dashes[3]

# open the downloaded CSV version of the file 
# run through it extracting the data we need
# create a nested lists, the inner list with performance data
# for each individual station 

start_date = ""
end_date = ""

# this code checks to see if the station performance data is offset by one column or not
# In P8 of 2016-17 (pattern 1 below) there is an extra blank column to the right of Aberdeen / Airdrie etc
# but in P9 of 2016-17 there is no blank column (pattern 0)
f = open(written_name)
csv_f = csv.reader(f)

pattern = 0
line_count = -1
for line in csv_f:
	line_count +=1
	if line_count == 19:
		if '%' in line[2]: continue
			
		elif '%' in line[3]:
			pattern = 1
		else: 
			print "There is a problem in the format of the station data"
f.close()

# end of routine to check for offset ########################################
f = open(written_name)
csv_f = csv.reader(f)

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
		for cell in line:
			if "%" in cell:
				percents = cell.split("%")
				monthly_pc = percents[0]
				annual_pc = percents[1]
		
		
	else:
		# no pattern offset
		if pattern == 0:
			if count_line > 18 and count_line < 55:
				for x in [0, 2, 3, 4, 5]:
					
					if x in [2,4,5]:
						
						one_station.append(float(line[x][0:len(line[x])-1]))
					elif x == 0:

						one_station.append(line[x])
					else:
						one_station.append(int(line[x]))

				all_stations.append(one_station)
				one_station = []
				
				for x in [6, 7, 8,9, 10]:
					if x in [7,9,10]:
						one_station.append(float(line[x][0:len(line[x])-1]))
					elif x == 6:
						one_station.append(line[x])
					else:
						one_station.append(int(line[x]))
				
				all_stations.append(one_station)
				one_station = []
		
			if count_line == 55:
				#pattern offset
				for x in [0, 2, 3,4, 5]:
					if x in [2,4,5]:
						one_station.append(float(line[x][0:len(line[x])-1]))
					elif x == 0:
						one_station.append(line[x])
					else:
						one_station.append(int(line[x]))

				all_stations.append(one_station)
				one_station = []

		if pattern == 1:
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

# begin function (refresh_db) to make some fresh tables using executescript()
# USE WITH CAUTION!!  
# if you have existing data IT WILL BE DESTROYED

def refresh_db():

	cur.executescript ('''
	DROP TABLE IF EXISTS Period;
	DROP TABLE IF EXISTS Performance;
	DROP TABLE IF EXISTS Percentages;


	CREATE TABLE Period (
	    id  INTEGER NOT NULL PRIMARY KEY UNIQUE,
	    year INTEGER,
	    per_iod INTEGER,
	    start_date TEXT,
	    end_date TEXT
	);

	CREATE TABLE Percentages (
		id  INTEGER NOT NULL PRIMARY KEY 
	        AUTOINCREMENT UNIQUE,
	        period_id INTEGER UNIQUE, 
	        monthly_pc FLOAT, 
	        annual_pc FLOAT 
	);

	CREATE TABLE Performance (
	    id  INTEGER NOT NULL PRIMARY KEY 
	        AUTOINCREMENT UNIQUE,
	    period_id  INTEGER,
	    station TEXT,
	    on_time_t FLOAT, 
	    booked_t INTEGER, 
	    on_time_a FLOAT, 
	    ppm FLOAT
	);
	''')
	# end function to drop and delete tables
	###########################################

#refresh_db() # <<== commented out to stop funtion being called. See not at the start of the function

for outer in all_stations:
    rec_count = 0
    stn_name = outer[0]
    ott = outer[1]
    bt = outer[2]
    ota = outer [3]
    ppm = outer [4]
    per_iod = int(year + period)

    cur.execute('''INSERT OR IGNORE INTO Period (id, year, per_iod, start_date, end_date) 
        VALUES ( ?, ?, ?, ?,? )''', ( per_iod, year, period, start_date, end_date ) )
    cur.execute('SELECT id FROM Period WHERE id = ? ', (per_iod, ))
    id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Performance
    (period_id, station, on_time_t, booked_t, on_time_a, ppm) 
    VALUES ( ?, ?, ?, ?, ?, ? )''',  
    ( id, stn_name, ott, bt, ota, ppm ) )

cur.execute(''' INSERT OR IGNORE INTO Percentages (period_id, monthly_pc, annual_pc)
    	VALUES (?,?,?)''', (id, monthly_pc, annual_pc))
conn.commit()