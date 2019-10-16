##########################################################################
# $Id: turbine_csv_script.py 4480 2013-12-20 23:20:21Z boverhof $
# Joshua R. Boverhof, LBNL
# See LICENSE.md for copyright notice!
#
#   $Author: boverhof $
#   $Date: 2013-12-20 15:20:21 -0800 (Fri, 20 Dec 2013) $
#   $Rev: 4480 $
#
###########################################################################
import sys
import os
import csv
import json
import optparse
from configparser import ConfigParser
from turbine.commands import states
from turbine.commands.turbine_job_script import parseExtraArgs

#states = set(['submit', 'create', 'setup', 'running', 'success', 'warning', 'error', 'expired', 'cancel'])


def fuzzyEquals(a, b, epsilon):
    return abs(a-b) < epsilon

# MS7 and earlier had weird issues with JSON objects.
# This is used when we know what should come out is an object,
# but it may be held in a single length array, string, or both


def loadJsonObjFromJsonObj(keyVal, jsonObj):
    entryVal = jsonObj[keyVal]
    if(isinstance(entryVal, list)):
        entryVal = entryVal[0]
    if(isinstance(entryVal, basestring)):
        entryVal = json.loads(entryVal)

    return entryVal

# Take a list of string objects and return the same list
# stripped of extra whitespace.


def striplist(l):
    return([x.strip() for x in l])

# Converts every array value that can be converted to a float to a float


def floatify(arry):
    for ii in range(0, len(arry)):
        try:
            arry[ii] = float(arry[ii])
        except:
            None


def getInputsFromCSV(configFile, infilename):

    infile = open(infilename, "r+")

    csvReader = csv.reader(infile)

    # The first row gives the sinter names of variables
    inputVarNames = striplist(csvReader.next())

    numinputs = len(inputVarNames)

    samples = []

    for row in csvReader:
        thisSample = {}
        floatify(row)
        for ii in range(0, len(row)):
            thisSample[inputVarNames[ii]] = row[ii]

        samples.append(thisSample)

    infile.close()
    return samples

# Converts to array of samples to be easily converted to a JSON
# String.


def writeInputsToGatewayFormat(configFile, samples):

    sessionArray = []
    for sample in samples:

        simname = configFile.get('Simulation', 'name')
        createDict = {"Simulation": simname, "Input": sample}
        createDict.update(parseExtraArgs(configFile))

        sessionArray.append(createDict)

    return sessionArray

#  outfile.write(sessionJson)


# Write the outputs for 1 sample, in order, one-per-line, to the provided outputfile
def writeCSVOutputs(configFile, outVarNames, status, allOutputs, csvWriter):

    outargs = []

    for name in outVarNames:
        if(name == "status"):
            outargs.append(status)
        elif(allOutputs == None):
            outargs.append(0.0)
        else:
            outargs.append(allOutputs[name]["value"])

    csvWriter.writerow(outargs)

# ---- end output

# This function needs to take two psuadeFiles.  I didn't want to overwrite
# the original file (as PSUADE does) so you take the PSUADE file with the
# inputs and no outputs, and output and idetical file with the outputs
# filled in.


def writeJson2CSV(configFile, inputJson, csvInFilename, csvOutFilename):

    csvInFile = open(csvInFilename, "rb")
    csvOutFile = open(csvOutFilename, "rb")

    # Read the output names first
    csvOutReader = csv.reader(csvOutFile)
    outputVarNames = striplist(csvOutReader.next())
    csvOutFile.close
    # Prep for writing outputs (to the same file)
    csvOutFile = open(csvOutFilename, "wb")
    csvWriter = csv.writer(csvOutFile)
    csvWriter.writerow(outputVarNames)  # Re-write that first line

    # Read the input names
    csvReader = csv.reader(csvInFile)
    # The first row gives the sinter names of variables
    inputVarNames = striplist(csvReader.next())

    numOutputs = len(outputVarNames)
    numInputs = len(inputVarNames)
    numsamples = 0

    samples = []
    sampleNum = 0

    for sample in inputJson:
        sampleNum = sampleNum+1
        # print sampleNum
        inargs = csvReader.next()
        floatify(inargs)
        assert(len(inargs) == numInputs)

        # Check that input values from this job in our input file match the values the gateway returned
        jsonInputs = [None] * len(inargs)
        for ii in range(0, numInputs):
            argname = inputVarNames[ii]
            jsonInputs = loadJsonObjFromJsonObj("Input", sample)
            if(not fuzzyEquals(inargs[ii], float(jsonInputs[argname]), 1e-6)):
                print(
                    "Error: inputs from sample %d do not match those returned by server." % sampleNum)
                print("Has the csv input file changed since this job was submitted?")
                print("csv input \t server expectation")
                for idx in range(0, len(inargs)):
                    print(inargs[idx], jsonInputs[argname])
        # End Check that inputs match in psuade file and server results

        # If the run DID complete, write the real outputs out to the outfile.
        if(sample["Output"] != ""):
            writeCSVOutputs(configFile, outputVarNames, sample["Status"], loadJsonObjFromJsonObj(
                "Output", sample), csvWriter)
        else:
            writeCSVOutputs(configFile, outputVarNames,
                            sample["Status"], None, csvWriter)

    csvInFile.close()
    csvOutFile.close()

# ------ end writeJson2Psuade --------------
