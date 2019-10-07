import pygame


print("AnnouncementLink v1.0")
    

def Test():
    print("AnnouncementLink is imported")

def init (directory, filetype):
    pygame.mixer.init()
    global filedirectory
    filedirectory = directory
    global fileextention
    fileextention = filetype
def getfilename (name):
    return(filedirectory+ name+ fileextention)
    
def announce (sound, text):
    #splits the text
    sounds = text.split("#")
    #Loads makes a list to store the loaded sounds in.
    LoadedSounds = list()
    if sound != "":
        LoadedSounds.append(pygame.mixer.Sound(getfilename(sound)))
    #Load Sounds
    for text in sounds:
        
        if text[:1] == "^":
            timestring = text.split("^")
            timestring.pop(0)
            time = timestring[0].split(":")
            for timenumbers in time:
                timenumber = list(timenumbers)
                if timenumber[0] == "1":
                    if timenumber[1] >= "4":
                        LoadedSounds.append(pygame.mixer.Sound(getfilename(timenumber[1])))
                        LoadedSounds.append(pygame.mixer.Sound(getfilename("teen")))
                    else:
                        LoadedSounds.append(pygame.mixer.Sound(getfilename(timenumber[0]+ timenumber[1])))
                else:
                    if timenumber[0] != "0":
                        LoadedSounds.append(pygame.mixer.Sound(getfilename(timenumber[0]+ "0")))
                    if timenumber[1] != "0":
                        LoadedSounds.append(pygame.mixer.Sound(getfilename(timenumber[1])))
                    
                

                   
        else:
            LoadedSounds.append(pygame.mixer.Sound(getfilename(text)))
        
    
    
    for a in LoadedSounds:
        print(a)
        a.play()
        while pygame.mixer.get_busy():
            pygame.time.delay(100)
