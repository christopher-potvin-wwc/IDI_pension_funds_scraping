'''Imports'''
#python module
import warnings


'''Setup'''
#Supress warnings. (For debug purposes, comment this line.)
warnings.filterwarnings('ignore')

#Dictionary of module:function (Note that the scripts.___ is important for python to find directory)
import_list = {
    "scripts.vervoer":"scrape_vervoer"
    }

#Input used for download
download = bool(input("Download pdf? (True or False)"))
#message used to track progress/debug (Ideally will be replaced with log system in future)
message = ""



'''Run Scripts'''
if download:
    for x in import_list:
        #Import the module
        module_x=__import__(x, fromlist=[None])
        #Get function object
        function_x=getattr(module_x, import_list[x])

        try:
            #Run function
            function_x(download)

            message = f"Succesfully ran {import_list[x]} with download."
        except Exception as e:
            try:
                #Run function without download
                download = False
                function_x(download)

                #Reset download to True
                download = True
                message = f"Ran {import_list[x]} without download. {e}."
            except Exception as e:
                #Error message.
                message = f"Unable to run {import_list[x]}. {e}"
                pass

        #print message
        print(message)

elif not download:
    for x in import_list:
        #Import the module
        module_x=__import__(x, fromlist=[None])
        #Get function object
        function_x=getattr(module_x, import_list[x])

        try:
            #Run function
            function_x(download)
            message = f"Succesfully ran {import_list[x]} without download."
        except Exception as e:
            #Error message.
            message = f"Unable to run {import_list[x]}. {e}"
            pass

        #print message
        print(message)