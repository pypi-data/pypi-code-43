"""
Multiline string formatting

Author: Pit

Acknowledgements: Thanks to Will for highlighting the importance
of automated boxes! You are my inspiration.
"""

#BOX: (generates a box around a string)
#takes string to add box around, and parameters for width, justification, border, and padding
#returns formatted string
def box(toFormat, boxChar = '|',width = 0, justify = "c", isPadded = True):
    width = _Check_Width(width, toFormat, isPadded)

    #Format the box
    #Add the top border (with padding if applicable)
    formattedStr = boxChar * width
    if isPadded:
        formattedStr += "\n" + boxChar + " ".center(width - 2) + boxChar

    #Format each line individually
    for line in toFormat.splitlines():
        formattedStr += "\n" + boxChar

        funcDict = {
            "c" : line.center,
            "l" : line.ljust,
            "r" : line.rjust
        }
        if isPadded:
            formattedStr += " " + funcDict[justify](width - 4) + " "
        else:
            formattedStr += funcDict[justify](width - 2)
        
        formattedStr += boxChar

    #Add bottom border (with padding if applicable)
    if isPadded:
        formattedStr += "\n" + boxChar + " ".center(width - 2) + boxChar
    formattedStr += "\n" + boxChar * width

    return formattedStr

#COLUMN: Formats mutliline string into columns.
def col(toFormat, colChar = "|", colWidth = "auto", just = "c", delimiter = " "):
    
    #Check for widest cell to set column width
    try:
        maxWidth = int(colWidth)
    except:
        maxWidth = 0
        
    if colWidth == "auto":
        
        #Check length of each cell againt maxWidth
        for cell in toFormat.split(delimiter):
            if len(cell) > maxWidth:
                maxWidth = len(cell)

    #Format the columns
    formattedStr = ""
    for line in toFormat.splitlines():
        
        for cell in line.split(delimiter):
            funcDict = {
                "c" : cell.center,
                "l" : cell.ljust,
                "r" : cell.rjust
            }

            #Determine whether cell contains integer value
            isInt = False
            try:
                cell = int(cell)
                isInt = True
            except:
                pass
            cell = str(cell)

            #Justify the current cell
            if not isInt:    
                formattedStr += colChar + funcDict[just](maxWidth)
            else:
                formattedStr += colChar + cell.rjust(maxWidth)
                
        formattedStr += colChar
        formattedStr += "\n"

    return(formattedStr)

#FLAIR: Bring some life
def flair(toFormat, flairChar = "~", width = "auto", just = "c"):
    #Determine the length of the longest line
    maxLineWidth = _Check_Width(0, toFormat, False)
    #If no total width provided, allocate 5 spaces outside longest line
    try:
        width = int(width)
    except:
        width = maxLineWidth + 10
        

    formattedStr = ""
    for line in toFormat.splitlines():
        
        funcDict = {
            "c" : line.center,
            "l" : line.ljust,
            "r" : line.rjust
        }
        formattedStr+= funcDict[just](width, flairChar) 

        formattedStr+="\n"

    return formattedStr

    
#Check each line to see if it has a greater width than the user defined width
#If it does, update the width    
def _Check_Width(testWidth, toTest, isPadded):
    for line in toTest.splitlines():
        if isPadded:
            if len(line) + 4 > testWidth:
                testWidth = len(line) + 4
        elif len(line) + 2 > testWidth:
            testWidth = len(line) + 2
            
    return testWidth
    
