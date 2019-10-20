from gtts import gTTS
from playsound import playsound

filename = 'temp.mp3'

def speak(text):
    tts = gTTS(text)
    tts.save(filename)
    playsound(filename)



    

   
