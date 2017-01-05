from bs4 import BeautifulSoup
import urllib
import pdftables_api
from secrets import pdftables_key
import csv

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
short_years = dashes[2].split("p")[1]
year = "20"+short_years[0:2]+"-20"+short_years[2:]
period = dashes[3]
#print ("period", period)
#print ("year", year) 


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

# do a database write here


