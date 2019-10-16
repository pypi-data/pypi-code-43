##########################################################################
# $Id: turbine_psuade_script.py 6275 2014-09-12 16:47:57Z leek2 $
# Joshua R. Boverhof, LBNL
# See LICENSE.md for copyright notice!
#
#   $Author: leek2 $
#   $Date: 2014-09-12 09:47:57 -0700 (Fri, 12 Sep 2014) $
#   $Rev: 6275 $
#
###########################################################################
import sys
import os
import json
import optparse
from configparser import ConfigParser
from turbine.commands import states
from turbine.commands.turbine_job_script import parseExtraArgs

#states = set(['submit', 'create', 'setup', 'running', 'success', 'warning', 'error', 'expired', 'cancel'])


def fuzzyEquals(a, b, epsilon):
    return abs(a-b) < epsilon


def certifyConfig(configFile):
    outputs = configFile.items("Outputs")
    outputsOrder = configFile.items("OutputsOrder")

    for k, v in outputsOrder:
        assert(configFile.get('Outputs', v))
        assert(int(k) > -1)

    for ii in range(0, outputsOrder.__len__()):
        assert(configFile.get('OutputsOrder', str(ii)))

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


def getInputsFromPSUADE_IO(configFile, infilename):

    infile = open(infilename, "r+")

    numinputs = 0
    numoutputs = 0
    numsamples = 0

    samples = []

    inIO = False

    while(not inIO):
        line = infile.readline()
        linesplit = line.split()
        if(linesplit[0] == "PSUADE_IO"):
            inIO = True

#  print "We're in PSUADE_IO now"

    metaline = infile.readline()
    metasplit = metaline.split()
    numinputs = int(metasplit[0])
    numoutputs = int(metasplit[1])
    numsamples = int(metasplit[2])

    # print "%d %d %d" % (numinputs, numoutputs, numsamples)
    # make sure the psuade file and config file agree about the number of outputs
    # print configFile.items("OutputsOrder"), numoutputs
    assert(configFile.items("OutputsOrder").__len__() == numoutputs)

    for sampleNum in range(1, numsamples+1):
        line = infile.readline()
        linesplit = line.split()
        assert(sampleNum == int(linesplit[0]))
        # If the sample has run, this number is 1, 0 otherwise
        hasRun = int(linesplit[1])
        thisInput = []
        for inputnum in range(1, numinputs+1):
            thisInput.append(float(infile.readline()))
        for outputnum in range(1, numoutputs+1):
            infile.readline()

        if(hasRun == 0):  # Skip any samples that have already been run.
            samples.append(thisInput)
            # print "Sending", sampleNum, hasRun

    line = infile.readline().strip()
    while(line == ""):
        line = infile.readline().strip()

    assert(line.split()[0] == "PSUADE_IO")

    infile.close()
    return samples

# Converts to array of samples to be easily converted to a JSON
# String.


def writeInputsToGatewayFormat(configFile, samples):

    sessionArray = []
    for args in samples:
        inputs = {}
        for (node, argnum) in configFile.items('Input'):
            inputs[node] = args[int(argnum)]

        simname = configFile.get('Simulation', 'name')
        createDict = {"Simulation": simname, "Input": inputs}
        createDict.update(parseExtraArgs(configFile))

        sessionArray.append(createDict)

    return sessionArray

#  outfile.write(sessionJson)


# Write the outputs for 1 sample, in order, one-per-line, to the provided outputfile
def writeOutputs(configFile, status, allOutputs, outputfile):

    # Get the outputs and make them a dict, because that's actually useful
    outputsList = configFile.items("Outputs")
    outputsOrderList = configFile.items("OutputsOrder")

#  print "OutputsList: " , outputsList
#  print allOutputs

    outputsDict = {}
    for item in outputsList:
        if item[0] == "status":
            outputsDict[item[0]] = {"units": "", "value": status}
        elif allOutputs == None:
            outputsDict[item[0]] = {"units": "", "value": 0.0}
        else:
            outputsDict[item[0]] = item[1]

    if(allOutputs != None):
        # for each output that comes directly from sinter, get the real values in outOutputs
        for k, v in outputsDict.items():
            # print "outputsDict", k, " ", v
            if(type(v) is str and v[0] != '"'):
                if(allOutputs != None):
                    outputsDict[k] = allOutputs[v]
                else:
                    outputsDict[k] = 0

        # print "Status: ", status
        # Now go back through an evaluate any that are calculations
        for k, v in outputsDict.items():
            # print "Pre: ", k, v
            if(type(v) is str and v[0] == '"'):
                try:
                    outputsDict[k] = eval(eval(v, outputsDict), outputsDict)
                except:
                    outputsDict[k] = 0
                # print "Post: ", k, outputsDict[k]

    for ii in range(0, outputsOrderList.__len__()):
        var = configFile.get('OutputsOrder', str(ii))
        outputfile.write("  %g\n" % float(outputsDict[var]["value"]))

# ---- end output


# If the json->PSUADE conversion goes wrong, this should try to recover
# by outputing dummy outputs
def writeErrorOutputs(configFile, outputfile, status):

    # Get the outputs and make them a dict, because that's actually useful
    outputsList = configFile.items("Outputs")
    outputsOrderList = configFile.items("OutputsOrder")

    outputsDict = {}
    for item in outputsList:
        if item[0] == "status":
            print("status: %d" % status)
            outputsDict[item[0]] = {"units": "", "value": status}
        else:
            outputsDict[item[0]] = {"units": "", "value": 0.0}

    for ii in range(0, outputsOrderList.__len__()):
        var = configFile.get('OutputsOrder', str(ii))
        outputfile.write("  %g\n" % float(outputsDict[var]["value"]))


# This function needs to take two psuadeFiles.  I didn't want to overwrite
# the original file (as PSUADE does) so you take the PSUADE file with the
# inputs and no outputs, and output and idetical file with the outputs
# filled in.
def writeJson2Psuade(configFile, inputJson, psuadeInFilename, psuadeOutFilename):

    psuadeInFile = open(psuadeInFilename, "r+")
    psuadeOutFile = open(psuadeOutFilename, "w+")

    numinputs = 0
    numoutputs = 0
    numsamples = 0

    samples = []

    inIO = False

    while(not inIO):
        line = psuadeInFile.readline()
        linesplit = line.split()
        if(linesplit[0] == "PSUADE_IO"):
            inIO = True
        psuadeOutFile.write(line)

    # print "We're in PSUADE_IO now"

    metaline = psuadeInFile.readline()
    psuadeOutFile.write(metaline)
    metasplit = metaline.split()
    numinputs = int(metasplit[0])
    numoutputs = int(metasplit[1])
    numsamples = int(metasplit[2])

    # print "%d %d %d" % (numinputs, numoutputs, numsamples)

    # make sure the psuade file and config file agree about the number of outputs
    #assert(configFile.items("OutputsOrder").__len__() == numoutputs)

    sampleNum = 0

    for sample in inputJson:
        sampleNum = sampleNum+1
        # print sampleNum
        # Now advance the PSUADE File
        line = psuadeInFile.readline()
        linesplit = line.split()
        assert(sampleNum == int(linesplit[0]))

        while(int(linesplit[1]) == 1):  # If this sample has already been run
            # skip it by outputting everything to the
            psuadeOutFile.write(line)
            for ii in range(0, numinputs + numoutputs):  # output file.
                line = psuadeInFile.readline()
                psuadeOutFile.write(line)

            line = psuadeInFile.readline()  # Then load up the next sample start line
            linesplit = line.split()  # to prime the top of the loop.
            sampleNum = sampleNum+1
            assert(sampleNum == int(linesplit[0]))

        complete = 0
        if(sample["State"] == 'success' or sample["State"] == 'error'):
            complete = 1
        # set it to has been run
        psuadeOutFile.write("%d %d\n" % (sampleNum, complete))

        # Put the psuade inputs into an array so we can check them against the json.
        psuadeInputs = []
        for ii in range(0, numinputs):
            line = psuadeInFile.readline()
            psuadeOutFile.write(line)
            psuadeInputs.append(float(line))

        # Check that inputs match in psuade file and server results
        jsonInputs = [None] * psuadeInputs.__len__()
        for (argname, argnum) in configFile.items('Input'):
            sampleInputs = loadJsonObjFromJsonObj("Input", sample)
            jsonInputs[int(argnum)] = sampleInputs[argname]

        # print sampleInputs
        # print jsonInputs
        for idx in range(0, psuadeInputs.__len__()):
            if(not fuzzyEquals(psuadeInputs[idx], jsonInputs[idx], 1e-6)):
                print(
                    "Error: inputs from sample %d do not match those returned by server." % sampleNum)
                print("Has the psuade input file changed since this job was submitted?")
                print("psuade input \t server expectation")
                for idx in range(0, psuadeInputs.__len__()):
                    print(psuadeInputs[idx], jsonInputs[idx])
        # End Check that inputs match in psuade file and server results

        # advance the inpsuade past the outputs, If the job isn't complete or is in error state
        # write whatever outputs were in the in file to the out file (junk)
        # If run did complete, outside look will write real outputs
        for ii in range(0, numoutputs):
            line = psuadeInFile.readline()
#        if(not complete or sample["Status"] != 0):
#          psuadeOutFile.write(line)

        # Bug workaround.  If the state is error, status should be non-zero
        status = sample["Status"]
        if(status == 0 and sample["State"] == "error"):
            status = 1

        # If the run DID complete, write the real outputs out to the outfile.
        if(complete and status == 0):
            try:
                if(sample["Output"] != ""):
                    writeOutputs(configFile, status, loadJsonObjFromJsonObj(
                        "Output", sample), psuadeOutFile)
                else:
                    writeOutputs(configFile, status, None, psuadeOutFile)
            except Exception as e:
                print(
                    "WARNING: converting Sample %d from json to PSUADE had the following error:" % sampleNum)
                print(e.message)
                print(
                    "Attempting to recover, but Sample %d may be invalid and need to be fixed by hand." % sampleNum)
                writeErrorOutputs(configFile,  psuadeOutFile)
        else:
            writeErrorOutputs(configFile, psuadeOutFile, status)

    # Ensure that we have run through all the PSUADE_IO section by looking for closing keyword
    # doesn't work if doing a rerun and the last run passed.
    line = psuadeInFile.readline()

    while(line):
        psuadeOutFile.write(line)
        line = psuadeInFile.readline()

    psuadeInFile.close()
    psuadeOutFile.close()

# ------ end writeJson2Psuade --------------
