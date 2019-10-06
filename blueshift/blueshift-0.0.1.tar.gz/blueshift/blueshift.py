#!/usr/bin/env python3

import os
from random import shuffle
from string import *

def generate(numberOfSerials, lengthOfSerial, useNumber="y", useUppercase="y", useLowercase="y", useSymbols="y"):
    if useNumber == False:
        useNumber = ""
    if useUppercase == False:
        useUppercase = ""
    if useLowercase == False:
        useLowercase = ""
    if useSymbols == False:
        useSymbols = ""

    listOfCharacterLists = createListOfCharacterLists(lengthOfSerial, useNumber, useUppercase,
                                                      useLowercase, useSymbols)
    totalPossibleSerialNumbers = len(listOfCharacterLists[0]) ** lengthOfSerial

    if (totalPossibleSerialNumbers < numberOfSerials):
        printErrorMessage(numberOfSerials, totalPossibleSerialNumbers)
        return

    generateSerialNumbers(numberOfSerials, lengthOfSerial, listOfCharacterLists, totalPossibleSerialNumbers)

def createListOfCharacterLists(lengthOfSerial, useNumber, useUppercase, useLowercase, useSymbols):
    characterList = createCharacterList(useNumber, useUppercase, useLowercase, useSymbols)
    listOfCharacterLists = []

    for i in range(lengthOfSerial):
        shuffle(characterList)
        listOfCharacterLists.append(characterList.copy())

    return listOfCharacterLists

def createCharacterList(useNumber, useUppercase, useLowercase, useSymbols):
    characterList = []

    if useNumber:
        characterList += digits

    if useUppercase:
        characterList += ascii_uppercase

    if useLowercase:
        characterList += ascii_lowercase

    if useSymbols:
        characterList += punctuation

    return characterList

def generateSerialNumbers(numberOfSerials, lengthOfSerial, listOfCharacterLists, totalPossibleSerialNumbers):
    fileName = str(numberOfSerials) + "_unique_serials.txt"
    addSerialsToArray(numberOfSerials, lengthOfSerial,
                             listOfCharacterLists, totalPossibleSerialNumbers)

def addSerialsToArray(numberOfSerials, lengthOfSerial, listOfCharacterLists, totalPossibleSerialNumbers):
    global serial_array
    serial_array = []

    singleSerialNumberString = ""
    indexList = [0] * lengthOfSerial
    distanceBetweenSerialNumbers = int(totalPossibleSerialNumbers / numberOfSerials)

    for _ in range(numberOfSerials):
        for y in range(lengthOfSerial):
            singleSerialNumberString += listOfCharacterLists[y][indexList[y]]

        serial_array.append(singleSerialNumberString)
        singleSerialNumberString = ""

        # printIndexList(indexList)

        increaseIndexVectorBy(indexList, len(listOfCharacterLists[0]), distanceBetweenSerialNumbers)


def printIndexList(indexList):
    for index in indexList:
        print(str(index).rjust(3), end = '')

    print()

def increaseIndexVectorBy(indexVctor, rolloverNumber, distanceBetweenSerialNumbers):
    increaseValueAtIndexXBy = 0

    for x in reversed(range(len(indexVctor))):
        increaseValueAtIndexXBy = distanceBetweenSerialNumbers % rolloverNumber
        indexVctor[x] += increaseValueAtIndexXBy

        if (indexVctor[x] >= rolloverNumber):
            indexVctor[x] -= rolloverNumber

            if (x > 0):
                indexVctor[x - 1] += 1

        distanceBetweenSerialNumbers = int(distanceBetweenSerialNumbers / rolloverNumber)
def get_serials():
    return serial_array