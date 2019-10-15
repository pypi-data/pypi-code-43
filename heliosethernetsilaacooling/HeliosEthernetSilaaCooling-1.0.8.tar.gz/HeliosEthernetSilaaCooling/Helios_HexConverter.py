"""
@ Stefanie Fiedler 2019
@ Alexander Teubert 2019
Version vom 15.10.2019

for Hochschule Anhalt, University of Applied Sciences
in coorperation with axxeo GmbH

This module converts either a string of characters to a list of hexadecimal-coded
values or a list of hex-values to a string
"""

def str2duohex(string):
    """
    if the string consists of an even number of characters, add 0x0000 as the last
    hex-value

    or, if the string consists of an even number of characters, add 0x00 to the last
    hex-value
    """

    if len(string)%2 == 0:
        myList = [ord(character) for character in (string+"\0"*2)]
        data = []

        for count in range(len(myList)//2):
            data.append((myList[count*2]<<8)|myList[count*2+1])

    else:
        myList = [ord(character) for character in (string+"\0")]
        data = []

        for count in range(len(myList)//2):
            data.append((myList[count*2]<<8)|myList[count*2+1])

    return data

def duohex2str(hexlist):
    """
    converts the hexadecimal coded values to strings of ascii-characters
    cuts of any unwanted ascii-NULL
    """

    string = ""
    #chr() converts hexadecimal coded values to their corresponding ascii val
    for duohex in hexlist:
        if (duohex & 0xff) | (duohex & 0xff00) != 0:
            string += chr((duohex&0xff00)>>8) + chr(duohex&0xff)

    return string
