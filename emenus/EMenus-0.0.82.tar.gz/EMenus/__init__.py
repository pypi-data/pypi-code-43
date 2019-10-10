#Test module for easier menus and input

#Required libraries
import random
import time
import hashlib

#version
ver = "0.0.81"

#Example
#class GameWord:
#  def __init__(self,words,length,word):
#    self.words = words
#    self.length = length
#    self.word = word
#  
#  def attempt(self,inpu,word,w,r):
#    print("*"*len(word))
#    print("Wrong: ", w)
#    print("Correct: ", r)
#    print("Current: ", inpu)

class UserInput:
  def uinput(x,type):
    if type == "str":
        while True:
            try:
                x = input("=> ")
                x = str(x)
                break
            except ValueError:
                print("Not string, please try again!")
    if type == "int":
      while True:
          try:
              x = input("=> ")
              x = int(x)
              break
          except ValueError:
              print("Not integer, please try again!") 

    if type == "float":
      while True:
          try:
              x = input("=> ")
              x = float(x)
              break
          except ValueError:
              print("Not float, please try again!") 
    return x

class NewMenu:
  def __init__(self,q,c):
    self.q = q
    self.c = []
  #Choices have to be an array of 3 strings
  #This function will return a value from 1 to 3 depending onwhat the user chose


def mcreate(n,q,c):
  while True:
    #proccesing
    c1, c2, c3 = c
    #
    print("###################",n,"###################")
    print(q)
    print("###########################################")
    print("Choices: ",c)
    choice = input("=> ")
    if choice == c1:
      return 1
      break
    elif choice == c2:
      return 2
      break
    elif choice == c3:
      return 3
      break
    else:
      print("No such option!")

class encryption:
  def sha256_encrypt(x):
    print("Using sha 256 to encrypt "+x)
    x = hashlib.sha256(x.encode()).hexdigest()
    return x

#Example
#choices = ["1","2","3"]
#print(NewMenu.create("Inventory","Equip?",choices))


#user = UserInput(0)

#user.cache(user.uinput(user.x))

def version():
  print("##################################################")
  print("#Menus "+ver+" has been installed and loaded!")
  print("##################################################")
