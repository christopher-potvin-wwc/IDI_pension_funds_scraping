'''Scrapes Pensioenfonds Vervoer, a nonprofit pension fund in transport, based in the Netherlands. Scraper finds link to pdf, downloads, and extracts text. Extracted text contains two entries per seperation, so regex accounts for this. Two lists are created to formated before being combined. Exports to TSV. No manual steps needed unless the website or format changes.'''
#Python Modules
import re

#External Modules
from playwright.sync_api import sync_playwright
import pandas as pd
import pdfplumber
import requests

#If run from main, imports from scripts folder. Else, imports locally.
if __name__ != "__main__":
    import scripts.functions as functions
else:
    import functions




'''Main Function'''
def scrape_vervoer():
    #/------------------Setup-------------------------/#

    #Create directory for PDFs and CSVs (create_path returns path object used later)
    path = functions.create_path("vervoer")

    #Columns for final dataframe (constants)
    shareholder = "Pensioenfonds Vervoer"
    URL = "https://www.pfvervoer.nl/over-ons/beleggen/spreiden-van-beleggingen"
    currency = "EUR"
    multiplier = "x1"



    #Playwright Start
    playwright = sync_playwright().start()

    #Establish page and browser
    browser = playwright.chromium.launch(headless=True, slow_mo=1, channel="chromium")
    page = browser.new_page()

    #Go to page that leads to PDF
    page.goto(URL)

    #Save button that leads to pdf preview
    link_button = page.get_by_role('link', name="overzicht van onze beleggingen (pdf)") #likely to break here on future updates of website
    link_button = "https://www.pfvervoer.nl/" + link_button.get_attribute("href")

    #Get PDF data and download
    r = requests.get(link_button)
    pdf_path = functions.download_file(r, "raw_vervoer.pdf", path)

    #Open PDF
    pdf = pdfplumber.open(pdf_path)

    #Stop playwright
    browser.close()
    playwright.stop()





    #--------------------/Format PDF data/-----------------#

    #Extract all text to one string
    text = ""
    for p in pdf.pages:
        text = text + p.extract_text()


    #Regex for date
    date_pattern = re.compile("(?P<day>\d+)-(?P<month>\d+)-(?P<year>\d{4})")
    
    #Find first instance of report date
    report_date  = re.search(date_pattern, text)

    #Split match into 3 vars to format
    day, month, year = report_date.groups()

    #If either month or day only has one digit, add zero to format
    if len(day) < 2:
        day = "0" + day
    if len(month) < 2:
        month = "0" + month

    #Stitch together
    report_date = year + "-" + month + "-" + day


    #Regex for Entries. Searching for standard things.
    #Edge cases: Entries come in groups of 2, but some (like government bonds) are not needed. Luckily, those ones include commas as opposed to periods. Selected for now, and filtered out later.
    entry_pattern = re.compile("\n(?P<l_issuer>[A-Za-z\- /'&,]+) (?P<l_value>[\d\.\-]+) (?P<r_issuer>[A-Za-z\- /'&,]+) (?P<r_value>[\d\.\-,]+)")

    #Find all matches
    split_text = re.findall(entry_pattern, text)

    #2 seperate entry lists to maintain intended order
    entries_left = []
    entries_right = []

    #For each group in matches
    for line in split_text:

        #Split list item into individual vars
        l_issuer, l_value, r_issuer, r_value = line


        #Check to see if matched issuer is the page footer
        l_check = re.search("Overzicht|Pagina", l_issuer)
        if not l_check:
            #Check to see if the matched value in not desired (gov bonds)
            l_check = re.search(",|-", l_value)
            if not l_check:
                #If both checks passed, append an entry
                entries_left.append([shareholder, l_issuer, report_date, l_value, multiplier, currency, URL])


        #Repeat process for group 2
        r_check = re.search("Overzicht|Pagina", r_issuer)
        if not r_check:
            r_check = re.search(",|-", r_value)
            if not r_check:
                entries_right.append([shareholder, r_issuer, report_date, r_value, multiplier, currency, URL])
        
    #Add into 1 list
    entries = entries_left + entries_right




    #--------------------/Export/------------------------#

    #Create dataframe
    df=pd.DataFrame(entries, columns=["Shareholder - Name", "Issuer - Name", "Security - Report Date", "Security - Market Value - Amount", "Security - Market Value - Multiplier", "Security - Market Value - Currency Code", "Data Source URL"])
    #Export
    functions.export_df(df, "vervoer", path)




#Run function locally
if __name__ == "__main__":
    scrape_vervoer()
