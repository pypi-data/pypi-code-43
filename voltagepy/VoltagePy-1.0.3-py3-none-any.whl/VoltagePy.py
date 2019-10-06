#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver

browser = None #webdriver
driver_folder = None #location of the browser drive
arguments = ["--headless","--disable-gpu"] #arguments

#init webdriver, defining options and capabilities
#by default the methods will autoload browser if None
#and return the browser


def setup(drive = "",arguments = ["--headless","--disable-gpu"]):
    #add the arguments to the browser options
    options = webdriver.ChromeOptions()
    for op in arguments:
        options.add_argument(op)    

    #turn these options into browser capabilities
    capabilities = options.to_capabilities()

    #setup drive path
    if(drive is not ""): 
        global driver_folder
        driver_folder = drive
    else:
        print("Please setup a drive path ex. setup('path/to/drive')")

    #init webdrive
    global browser
    browser = webdriver.Chrome(executable_path=driver_folder,desired_capabilities=capabilities)
    return browser

#open the page ex. browser.get("https://www.duckduckgo.com"), if in headless, there's no window.
#and return the browser
def open(url):
    if(browser is None): setup()
    browser.get(url)
    return browser

#copy the contet of a "opened page" and return it
def pageHtml(url = ""):
    html = "PAGE NOT LOADED"
    
    #open a page if a url is provided
    if(url != "") : open(url)
    
    #check if the page is loaded 
    if(browser.title != ""):
        #if the url is not null, open and copy     
        html = browser.page_source
    return html

#close the browser
def quit():
    browser.close()
    browser.quit()

#--exemple of commands and response--
#import VoltagePy

#VoltagePy.setup('webdrivers/Chrome/76/linux_76')
#VoltagePy.open("https://www.duckduckgo.com")
#print(VoltagePy.pageHtml())
#VoltagePy.quit()