#What all needs to go in main:

#Input to determine wether to call functions with download
'''
Current idea:
Input 1 for download, 2 for no download

If 1: use that as input in functions
try: run function
try: switch variable, run it without download
except: switch variable back, log error message, move on

If 2:
try: run function without download
excepct: log and pass

'''

#recurring functions need to be written on outside docs



'''Python Modules'''
import datetime
import re
from pathlib import Path
import io

'''External Modules'''
from playwright.sync_api import sync_playwright
import pdfplumber
import pandas as pd
import requests

import scripts.functions as functions
#import importlib
#import sys
#sys.path.append("data")

import_list = {
    "scripts.vervoer":"scrape_vervoer"
    }




#download = bool(input("Download pdf? (True or False)"))
download = True


if download == True:
    for x in import_list:
        
        

        y=__import__(x)
        #print(y) #<module 'scripts' (namespace) from ['c:\\Users\\Jackie\\Documents\\myprojects\\WW Schoolwork and docs\\ghub\\IDI_pensions_funds_scraping\\scripts']>
        #z.import_list[x](download)
        z=getattr(y, import_list[x])
        #z
        z(download)

        
        #try:
            #download = True
            #run scrape_i
        #scripts_list[i](download)
        
        #try:
            #donwload = False

        #except:
            #pass






#download = input("Download pdf? (True or False)")

#import scripts.vervoer as vervoer
#vervoer.scrape_vervoer(download)