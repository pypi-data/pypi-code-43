#Test module for easier menus and input

#Required libraries
import random
import time

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
  def __init__(self,x):
    self.x = x
  def cache(self,x):
    print("Cached Input as x:",x)
  def uinput(self,x):
    x = input("=> ")
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
#Example
#choices = ["1","2","3"]
#print(NewMenu.create("Inventory","Equip?",choices))


#user = UserInput(0)

#user.cache(user.uinput(user.x))

#game = GameWord()