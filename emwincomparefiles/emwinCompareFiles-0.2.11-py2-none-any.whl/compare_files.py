#!/usr/bin/python/
#
# This script will compare the arrival time of data to the ESB between
# the legacy system and the enterprise/new system using the NWS WMO
# Header in the following format: 
#     TTAAii CCCC YYGGgg [BBB] NNNxxx (NNNxxx is the AWIPS ID)
#
import csv, psycopg2, re
from datetime import datetime

print("Running compare_files.py\n")

# Define empty lists to store data
date1 = []
date2 = []
wmoHeader1 = [] 
wmoHeader2 = [] 
AWDSList = []
validNNN = []

##Ask user for input
userInput = raw_input("Enter legacy filename: ")
if userInput[-4:] in ('.csv'): 
    filename = userInput     
    print("Using: " + filename)
else:
    print("Invalid file. Must be CSV.\nExiting...")
    quit ()

# Open list of products missing from Enterprise, to be excluded from comparison
with open('AWDS_190501_1600_BL.csv', 'r')as csvfile12:
    filereader = csv.reader(csvfile12, delimiter=',')
    next(filereader, None)
    for column in filereader: 
        AWDS = column[0]
        AWDSList.append(AWDS)

# Open the legacy CSV file 
#with open('EMleg-Listing-190610-r1.csv', 'r')as csvfile:
with open(filename, 'r')as csvfile:
    print "\nExtracting data from legacy file..."
    filereader = csv.reader(csvfile, delimiter=',')
    next(filereader, None) 
    for column in filereader:
        # Extract the datetime data as datetime objects to use in timedelta
        legacyDateString = datetime.strptime(column[6], '%m/%d/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S') #reformat string to use dashes
        #legacyDateString = datetime.strptime(column[6], '%m/%d/%Y %H:%M %p').strftime('%Y-%m-%d %H:%M:%S') #use this line if legacy file includes AM/PM in timestamp
        legacyDateObject = datetime.strptime(legacyDateString, '%Y-%m-%d %H:%M:%S') #returns datetime object
        date1.append(legacyDateObject)
        # Extract WMO header info
        wmoHeaderLegacy = column[1] # TTAAii CCCC YYGGgg
        wmoHeaderNoSpace = wmoHeaderLegacy.replace(" ", "") #Replace whitespace
        awipsId = column[2]
        awipsIdNoSpace = awipsId.strip() #remove trailing whitespace if present
        # Remove dashes if present (A dash represents a byte in a 4 or 5 characters AWIPS ID, the database does not use dashes)
        awipsIdNoDash = awipsIdNoSpace.replace("-", "") 
        header = wmoHeaderNoSpace + awipsIdNoDash
        wmoHeader1.append(header)

#If product is in AWDS, exlcude it from wmoHeader1 list
newWmoHeader1 = [x for x in wmoHeader1 if not any(substr in x for substr in AWDSList)]

# Open the database query results file and write to a new file, after merging columns
# containing WMO header information 
with open('Database_Query.csv', 'r')as csvfile:
    filereader2 = csv.reader(csvfile, delimiter=',')
    next(filereader2, None)
    # Open new file to write to
    with open('Database_Query_merged.csv', 'w+') as mergedcsvfile:
        writer = csv.writer(mergedcsvfile)
        for row in filereader2:
            # Merge columns in database results file to form WMO header 
            wmoHeader = ''.join([row[1], row[2], row[4]])
            writer.writerow((row[0], wmoHeader, row[5], row[6], row[3])) #NNN on end

# Define module to parse dates queried from the database, having two formats 
# - with and without milliseconds, takes a datetime object as an argument
def parse_dates(datetimeObject):
    for formats in ('%Y-%m-%d %H:%M:%S.%f','%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(datetimeObject, formats)
        except ValueError:
            pass
    raise ValueError('No valid date format found.') # If format does not match those defined above

# Open merged file for reading to append WMO header info to empty list defined earlier
with open('Database_Query_merged.csv', 'r')as csvfile:
    filereader3 = csv.reader(csvfile, delimiter=',')
    print "Extracting data from database file..."
    for column in filereader3: 
        #matches = re.findall(r"((?:\d{6}\ ?)([A-Z\d]{3})?(?:[\r\n\ ]+)(([A-Z\d]{6}|[A-Z\d]{5} |[A-Z\d]{4}  ))?)", column[3])
        matches = re.findall(r"((?:\d{6}\ ?)([A-Z\d]{3})?(?:[\r\n\ ]+)(([A-Z\d]{6}|[A-Z\d]{5} |[A-Z\d]{4}  ))?)(?:[\r\n]+)", column[3])
        BBB = matches[0][1]
        awipsId = matches[0][2]
        wmoHeader = column[1]
        header = (wmoHeader + BBB + awipsId).strip()
        wmoHeader2.append(header) 
        # Extract datetime info
        parsedString = parse_dates(column[0]).replace(microsecond=0)
        timeString = datetime.strftime(parsedString, '%Y-%m-%d %H:%M') # string
        timeObject = datetime.strptime(timeString, '%Y-%m-%d %H:%M') # convert to datetime object
        date2.append(timeObject)

# Create dictionary from header and timestamps
# Dictionaries overwrite duplicate keys
headerDates1 = dict(zip(newWmoHeader1,date1)) # Legacy
headerDates2 = dict(zip(wmoHeader2,date2)) # Enterprise

# Perform time comparison and save results to a file
with open('Latency.csv', 'wb') as csvfile:
    latencywriter = csv.writer(csvfile, delimiter=',')
    latencywriter.writerow(['Product ID'] + ['Legacy Time'] + ['Enterprise Time'] + ['Latency'])
    for k in headerDates1:
        if k in headerDates2:
            latencywriter.writerow([k, headerDates1[k], headerDates2[k], abs(headerDates1[k]-headerDates2[k])])

#print("Total number of Legacy products (includes duplicates): " + str(len(newWmoHeader1))) # total number of Legacy products in the file
print("Number of Legacy products (excludes duplicates): " + str(len(headerDates1)))
#print("Total number of Enterprise products (includes duplicates): " + str(len(wmoHeader2))) # total number of Enterprise products in the file
print("Number of Enterprise products (excludes duplicate): " + str(len(headerDates2)))

# Save ouput as CSV
# Products in Legacy, missing from Enterprise
with open('LegacyProductsNotInEnterprise.csv', 'wb') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',')
    filewriter.writerow(['Product ID'])
    for key in headerDates1.keys(): #keys in dict1 not in dict2
        if not key in headerDates2:
            filewriter.writerow([key]) 

count = len(open("LegacyProductsNotInEnterprise.csv").readlines(  ))
print("Number of missing products: " + str(count))

# Products in Enterprise, missing from Legacy
#file5 = open('EnterpriseProductsNotInLegacy.txt', 'w')
#for key in headerDates2.keys(): #keys in dict2 not in dict1
#    if not key in headerDates1:
#        print >> file5, key

# End of script 
