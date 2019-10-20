from collections import Counter
import os
from termcolor import colored

def green(word):
    word = str(colored(word, 'green'))
    return word
def red(word):
    word = str(colored(word, 'red'))
    return word
def yellow(word):
    word = str(colored(word, 'yellow'))
    return word
def cyan(word):
    word = str(colored(word, 'cyan'))
    return word
def magenta(word):
    word = str(colored(word, 'magenta'))
    return word
def diflet(string, start=''):
    if start == '':
        start = 0
    string = str(string)
    for char in str(Counter(string)):
        if char == "'":
            start += 0.5
    return int(start)
def help():
    print(colored('''Type 'afro.help()' for help
Type 'afro.' followed by one of the folloing colors [green, red, yellow, cyan, magenta] then ("the text to add color to here") without spaces for eg. print(afro.red("This Text Is Red"))
Type 'afro.' followed by 'diflet()' which will find the amount of different letters in a string.            (string, starting_value) so afro.diflet("hellllllllllo", 1) would return 5 because 4 different letters are in that string and the second parameter would be the added value

'''))

def vsco(worrrrrrd):
    worrrrrrd += 'sksksksksksksksksksksksksks'
    return worrrrrrd