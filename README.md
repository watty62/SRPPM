# SRPPM
Tracking Scottish Rail Performance

## Introduction

This project is my first [100 Days of Code](http://github.com/watty/100-days-of-code) project. 

It is designed to:
* spot the publication of 4-weekly PDF performance reports, 
* download new ones, 
* use the PDFTables API to convert to CSV, 
* extract headline data, and 4 detailed measures for each Scottish Railway station, 
* write all data to a SQLite database
* make that publicly available - perhaps via an API

* Requirements

1. You'll need [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-2. soup) installed 
3. You'll need an API Key from [PdfTables](https://pdftables.com/pdf-to-excel-api)
4. Rather than write your own wrapper for the API, install [this package](https://github.com/pdftables/python-pdftables-api)
5. Create a secrets.py file to put your API key in, and have a line in it as follows:
pdftables_key = "xxxxxxxx"

##Progress so far

* Given the starting URL, the scraper finds the link to the current performance report in PDF.
* The programme notes the file name (as it contains info on the year and period which we use later) and downloads a copy. 
* The programme invokes the PDFTables API, sending the PDF and gets returned a CSV file which is given the same file name but with the correct CSV suffix. 
* We then parse the CSV, locating the necessary bits of data, writes these to nested lists, which it the sorts alphabetically by station before (for now) writing these to a plain text file as CSV.

#To be done

1. The main objective is to get the code writing the data to a SQLite database.
2. I also need to normalise the data structure - rather than copy how it works so far 

## Optional extras

I might also

* set up a twitter feed to draw attention to significant changes month on month, 
* set up a website to make the data more widely avaialable
* create visualisations
* set up an API to grab the data
