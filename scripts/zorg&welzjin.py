'''Scrapes Pensionefonds Zorg & Welzjin, a Dutch pension fund for "health, mental, and social inerests." Scraper contains 3 functions, 2 for formatting data and 1 main scraping function. The main function uses a combination of while loops and requests to find the proper JSON files to download from the dynamic HTML website. When found, the files are downloaded, loaded in as dataframes, entries are formatted, and then columns are reordered in new DFs according to IDI schema. Each JSON and dataframe (.tsv) is saved as seperate files (10 files created if scraper ran to full extent). Right now, only tested for December quarter. Depending on future report dates, the dictionary "quarters" may need to be adjusted. Other than that, no manual steps needed unless format of JSON request links or format of data within JSONs change.'''
#Python Modules
import re
import datetime
import logging
from pathlib import Path

#External Modules
import requests
import pandas as pd

#If run from main, imports from scripts folder. Else, imports locally.
if __name__ != "__main__":
    import scripts.functions as functions
    log_mode = "a" #Add to log
else:
    import functions
    log_mode = "w" #Create log



'''Formats data by removing ranges and html tags.'''
def fix_entries(name):
    #Read entry as string
    name = str(name)

    #Drop tags
    name = re.sub("<.+>+", "", name)

    #Fix first possible market value
    match = re.search("\d+ - (\d+) M", name)
    if match:
        name = match.group(1)
    
    #Fix second possible market value
    match = re.search("([.\d]+)M", name)
    if match:
        name = match.group(1)

    return name



'''Drop range in percent and convert to decimal.'''
def fix_percent(percent):
    try:
        #See if entry matches their percent schema
        match = re.search("\d+ - (\d+) %", percent)
        #Save max number
        percent = match.group(1)

        #Convert number to decimal
        percent = float(percent)
        percent = percent/100
    except:
        pass
    return str(percent)




'''Main funtion'''
def scrape_zw():

    #---------------/Setup and Find Correct Report Date/-------------#

    #Find directory of repository
    parent_dir = Path(__file__).parent.parent
    #Setup logging
    logging.basicConfig(filename=parent_dir/'log.log', level=logging.INFO, filemode=log_mode, format="%(asctime)s - %(message)s")
    

    #Link to dynamic HTML
    data_url = "https://www.pfzw.nl/over-pfzw/beleggen-voor-een-goed-pensioen/soorten-beleggingen.html"
    #Create a path and save as var
    path = functions.create_path("zorg&welzjin")

    
    #Get current year, with offset of 1 for loop to function
    year = int(datetime.datetime.now().year) + 1


    try_url = "" #URL to try
    report_quarter = "" #The last report quarter (what we want)
    label = f"Private_Equity_{year}" #A label to test (Could be any, not just private equity)

    #Loop through years until correct report quarter found 
    while not report_quarter:

        #Subtract a year (beginning value offset to make this work)
        year -= 1

        #Redefine label with new year
        label = f"Private_Equity_{year}"

        #Quarters to check NOTE:Currently only dec is tested, but the other 3 are standard fiscal quarters.
        quarters = {
        "4":f"31-december-{year}",
        "3":f"30-september-{year}",
        "2":f"30-june-{year}",
        "1":f"31-march-{year}"
        }

        #Loop through each quarter in a year, trying to find a request URL that works
        for quart in quarters:

            #Stitch together a URL that matches the request URL format of Z&W
            try_url = "https://www.pfzw.nl/content/dam/pfzw/web/transparantielijsten/transparantielijsten-" + quarters[quart] + "/" + label + "Q" + quart + ".json"
            
            #Request info
            req = requests.get(try_url)
            if req.status_code == 200:
                #If request succesful, save quarter and date, and break for loop
                report_quarter = [quart, quarters[quart]]
                break



    
    #------------------/Download JSON Files/--------------------#

    #Split report date info into 2 vars
    quarter, date = report_quarter
    #Labels to look for
    labels = ["Private_Equity", "Listed_Real_Estate", "Equities_corporate", "Credit_Risk_Sharing", "Externe_vermogensbeheerders"]
    #Labels found
    export_labels = []
    #Paths to JSONs
    json_paths = []


    #Loop through all labels, attempting to download
    for label in labels:

        #Stitch together URL according to a label and found report date
        json_url = "https://www.pfzw.nl/content/dam/pfzw/web/transparantielijsten/transparantielijsten-" + date + "/" + label + f"_{year}" + "Q" + quarter + ".json"
        
        #Request
        req = requests.get(json_url)

        #If the request is good to go, download the json
        if req.status_code == 200:

            #Add label to exports
            export_labels.append(label.lower())

            #Download file and append to json paths
            filename = "raw_zorg&welzjin_" + label.lower() + ".json"
            json_paths.append(functions.download_file(req,filename, path))

            #Log success
            logging.info(f"Z&W - Downloaded {label}")
        #If not
        else:
            #Log failure, and continue
            logging.info(f"Z&W - Failed to download {label}")
            pass



    #Load json files as dataframes and use custom functions to format columns (Would've included in for loop directly, but pandas quirk made it easier for them to be functions)
    unfiltered_dfs = []
    for file in json_paths:

        #Read and save as df
        df = pd.read_json(file)
        
        #Iterate through columns
        for col in df:
            #Fix tags and ranges
            df[col] = df[col].apply(fix_entries)
            #If column has shares, fix percentages
            if col == "Aandeel":
                df[col] = df[col].apply(fix_percent)
        
        #Append to list
        unfiltered_dfs.append(df)





    #--------------------/Format DFs and Export/------------------#

    #Set constants
    multiplier = "x1_000_000"
    currency = "EUR"

    #Set report date constant using quarter found earlier
    #Get year with basic string slicing (last 4 chars)
    year = date[-4:]
    #Get day with basic string slicing (first 2 chars)
    day = date[:2]

    #Get month as word by subbing out dashes and digits
    month = re.sub("[\d\-]+", "", date)
    #Convert month to digits
    month = functions.convert_month(month)

    #Assemble report date
    report_date = year + "-" + month + "-" + day



    #Loop through dataframes, using if statements to assemble new dfs the way we want. Index used to name each df from export labels (should match up with number of dfs).
    for i, df in enumerate(unfiltered_dfs):

        #Find lengths of dataframe
        num_entries = len(df.index)

        #Create dictionary for new dataframe, with first entry being shareholder as many times as there are entries
        df_dict = {
            "Shareholder":["Pensioenfonds Zorg & Welzjin"]*num_entries
        }



        #Create list of col names
        cols = []
        for col in df:
            cols.append(col)

        #Check to see if specific keywords are in the dataframe's columns. By checking in a specific order with if statements, we may assemble dfs accoridng to IDI schema no matter what order they appear in the JSON files.

        if "Investeerder" in cols: #Investor
            df_dict.update({"Issuer - Name":df["Investeerder"]})
        elif "CreditRiskSharingBank" in cols: #Credit Risk Sharing Bank
            df_dict.update({"Issuer - Name":df["CreditRiskSharingBank"]})

        if "Land" in cols: #Country
            df_dict.update({"Issuer - Country Name":df["Land"]})

        if "Sector" in cols: #Sector
            df_dict.update({"Issuer - Sector":df["Sector"]})

        if "Categorie" in cols: #Category
            df_dict.update({"Security - Type":df["Categorie"]})
        elif "TypeInvestering" in cols: #Type of Investment
            df_dict.update({"Security - Type":df["TypeInvestering"]})
        
        #Add report date. Needed in all DFs
        df_dict.update({"Security - Report Date":[report_date]*num_entries})

        #Several different keywords for market value, but if found, they all need the multiplier and currency constants as well.
        if "Marktwaarde" in cols: #Market value
            df_dict.update({"Security - Market Value - Amount":df["Marktwaarde"]})
            df_dict.update({"Security - Market Value - Multiplier":[multiplier]*num_entries})
            df_dict.update({"Security - Market Value - Currency Code":[currency]*num_entries})
        elif "IndicatieMarktwaarde" in cols: #Market Value Indication
            df_dict.update({"Security - Market Value - Amount":df["IndicatieMarktwaarde"]})
            df_dict.update({"Security - Market Value - Multiplier":[multiplier]*num_entries})
            df_dict.update({"Security - Market Value - Currency Code":[currency]*num_entries})
        elif "IndicatieMarktwaardeEur" in cols: #Market Value Indication Eur
            df_dict.update({"Security - Market Value - Amount":df["IndicatieMarktwaardeEur"]})
            df_dict.update({"Security - Market Value - Multiplier":[multiplier]*num_entries})
            df_dict.update({"Security - Market Value - Currency Code":[currency]*num_entries})

        if "Aandeel" in cols: #Share
            df_dict.update({"Stock - Percent Ownership":df["Aandeel"]})

        #All DFs need data source (the dynamic HTML, established at beginning)
        df_dict.update({"Data Source URL":[data_url]*num_entries})



        #Create dataframe from dictionary
        export_df = pd.DataFrame(df_dict)
        
        #Asseble filename using export labels and current DF's index
        filename = "zorg&welzjin_" + export_labels[i]
        #Export a dataframe
        functions.export_df(export_df, filename, path)




#---------/Run function locally/---------------#
if __name__ == "__main__":
    scrape_zw()

