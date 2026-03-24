'''Scrapes Pensioen Funds Detailhandel, a company based in the Netherlands that manages the investments of non-food retail employees and those retired from the field. This scraper naviagtes to the website, finds the link to the pdf, saves it, and uses it to download the pdf (Note: get_pdf function was not used here, as window was not a popup.) Then, the pdf was split into two sections per page to account for edge cases, and desired attributes for each were saved into a list (Note: memory became an issue on this one, so only the desired attributes were saved, and all others were deleted). Then, regex is used to filter entries, the data is formatted, then exported as a tsv. No manual steps needed unless the website or format changes.'''
#Python module
import re

#External Modules
import pdfplumber
import pandas as pd
from playwright.sync_api import sync_playwright
import requests

#Correctly import functions, regardless of script executed
if __name__ != "__main__":
    import scripts.functions as functions
else:
    import functions



'''Main function'''
def scrape_detailhandel():

    #----------------/Get PDF/---------------------#

    url = "https://pensioenfondsdetailhandel.nl/onze-organisatie/pensioenzaken/de-beleggingsportefeuille" #Website download page
    path = functions.create_path("detailhandel") #Path to file


    #Start playwright
    playwright = sync_playwright().start()

    #Establish page and browser
    browser = playwright.chromium.launch(headless=True, slow_mo=1, channel="chromium")
    page = browser.new_page()

    #Go to page that leads to PDF
    page.goto(url)

    #Reject Cookies
    page.get_by_role('button', name="alles weigeren").click()

    #Get URL of pdf page (Not a popup, therefore get_pdf function doesn't work here)
    url = page.get_by_role('link', name="Beleggingen per", exact=False).get_attribute('href')

    #Close browser and stop playwright
    browser.close()
    playwright.stop()




    #-------------/Download PDF/--------------#

    #Return response object
    r = requests.get(url)
    

    #Path to PDF
    pdf_path = path/"raw_detailhandel.pdf"

    #Write pdf data to directory
    with open(pdf_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    #Open PDF
    pdf = pdfplumber.open(pdf_path)





    #--------------/Sort through entries/---------------#

    #Both edge cases and memory are issues on this one, so this loop splits pages into 2, gets their metadata, and appends only what we need.
    text = []
    for p in pdf.pages:
        #Left and right columns
        left = p.crop((0, 0, 416, p.height))
        right = p.crop((416, 0, p.width, p.height))

        #Extract left side, then right side (order of entries is maintained)
        temp = left.extract_text_lines(return_chars=True) + right.extract_text_lines(return_chars=True)
        
        #For each line, get only what we need (The text and the font name)
        for line in temp:
            text.append([line['text'], line['chars'][0]['fontname']])
    #Delete temp for memory
    del temp


    #Establish constants
    shareholder = "Pensioenfonds Detailhandel"
    currency = "EUR"
    report_date = functions.get_pdf_date(pdf)
    sectype = ""

    #Establish Pattern. Edge cases: Some entries don't have numbers.
    pattern = re.compile("(?P<issuer>[A-Za-z\d\- '/&]+) (?P<value>[\d\.]*)")


    #For each line, apply regex, check for edge cases, and append entries.
    entries = []
    for line in text:

        #Split list from earlier into two variables
        info, font = line

        #Check for correct entry font
        if font == "AAAAAG+CenturyGothic":

            #Apply pattern to one line
            match = re.search(pattern, info)
            #Split groups into 2 vars
            issuer, value = match.groups()
            #Strip excess spaces on issuer name
            issuer = issuer.strip()

            #Some entries have numbers, and some don't (hence why we split the pages earlier.) Only sanctionized entries don't have them, and vice versa.
            if not value:
                sectype = "Sanctionized"
            else:
                sectype = "Equity"

            #Create 1 entry according to IDI schema 
            entries.append([shareholder, issuer, sectype, report_date, value, currency, url])




    #----------/Export data/-----------#

    #Create df with columns according to IDI schema
    df = pd.DataFrame(entries, columns = ["Shareholder - Name", "Issuer - Name", "Security - Type", "Security - Report Date", "Security - Market Value - Amount", "Security - Market Value - Currency Code", "Data Source URL"])
    #Export as tsv
    functions.export_df(df, "detailhandel", path)




#---------------/Scrape Locally/-----------------#
if __name__ == "__main__":
    scrape_detailhandel()