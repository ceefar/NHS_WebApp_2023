# -- author : ceefar --
# -- project : nhs 2023 --

# -- imports --
import asyncio
from cls_db import Database
import bs4 
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import json
import requests
import time
import urllib.error
import datetime

# -- some handy objects --
JSON = int | str | float | bool | None | dict [str, "JSON"] | list["JSON"]
JSONobject = dict[str, JSON]
JSONList = list[JSON]

# -- initialise global db instance --
db = Database()

# -- header info --
header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}

# mids # south west # london # north east & yorkshire
hospitals_regions = {'UNIVERSITY HOSPITALS BIRMINGHAM NHS FOUNDATION TRUST':"mids", 'CHESTERFIELD ROYAL HOSPITAL NHS FOUNDATION TRUST':"mids", 
                        'KETTERING GENERAL HOSPITAL NHS FOUNDATION TRUST':"mids", 'NOTTINGHAM UNIVERSITY HOSPITALS NHS TRUST':"mids", 
                        'SHERWOOD FOREST HOSPITALS NHS FOUNDATION TRUST':"mids", 'THE DUDLEY GROUP NHS FOUNDATION TRUST':"mids", 
                        'THE ROYAL ORTHOPAEDIC HOSPITAL NHS FOUNDATION TRUST':"mids", 'THE SHREWSBURY AND TELFORD HOSPITAL NHS TRUST':"mids", 
                        'UNIVERSITY HOSPITALS OF DERBY AND BURTON NHS FOUNDATION TRUST':"mids", 'UNIVERSITY HOSPITALS OF NORTH MIDLANDS NHS TRUST':"mids", 
                        'WORCESTERSHIRE ACUTE HOSPITALS NHS TRUST':"mids", 'WYE VALLEY NHS TRUST':"mids", 'WALSALL HEALTHCARE NHS TRUST':"mids", 
                        "BIRMINGHAM WOMEN'S AND CHILDREN'S NHS FOUNDATION TRUST":"mids", 'GEORGE ELIOT HOSPITAL NHS TRUST':"mids", 
                        'NORTHAMPTON GENERAL HOSPITAL NHS TRUST':"mids", 'SANDWELL AND WEST BIRMINGHAM HOSPITALS NHS TRUST':"mids", 
                        'SOUTH WARWICKSHIRE NHS FOUNDATION TRUST':"mids", 'THE ROBERT JONES AND AGNES HUNT ORTHOPAEDIC HOSPITAL NHS FOUNDATION TRUST':"mids", 
                        'THE ROYAL WOLVERHAMPTON NHS TRUST':"mids", 'UNITED LINCOLNSHIRE HOSPITALS NHS TRUST':"mids", 
                        'UNIVERSITY HOSPITALS COVENTRY AND WARWICKSHIRE NHS TRUST':"mids", 'UNIVERSITY HOSPITALS OF LEICESTER NHS TRUST':"mids",
                        'DORSET COUNTY HOSPITAL NHS FOUNDATION TRUST':"swest", 'GREAT WESTERN HOSPITALS NHS FOUNDATION TRUST':"swest", 
                        'ROYAL CORNWALL HOSPITALS NHS TRUST':"swest", 'ROYAL UNITED HOSPITALS BATH NHS FOUNDATION TRUST':"swest", 'SOMERSET NHS FOUNDATION TRUST':"swest",
                        'UNIVERSITY HOSPITALS BRISTOL AND WESTON NHS FOUNDATION TRUST':"swest", 'UNIVERSITY HOSPITALS PLYMOUTH NHS TRUST':"swest", 
                        'GLOUCESTERSHIRE HOSPITALS NHS FOUNDATION TRUST':"swest", 'NORTH BRISTOL NHS TRUST':"swest", 
                        'ROYAL DEVON UNIVERSITY HEALTHCARE NHS FOUNDATION TRUST':"swest", 'SALISBURY NHS FOUNDATION TRUST':"swest", 
                        'TORBAY AND SOUTH DEVON NHS FOUNDATION TRUST':"swest", 'UNIVERSITY HOSPITALS DORSET NHS FOUNDATION TRUST':"swest", 
                        'YEOVIL DISTRICT HOSPITAL NHS FOUNDATION TRUST':"swest",
                        'BARTS HEALTH NHS TRUST':"london", 'CROYDON HEALTH SERVICES NHS TRUST':"london", 'GREAT ORMOND STREET HOSPITAL FOR CHILDREN NHS FOUNDATION TRUST':"london",
                        'HOMERTON HEALTHCARE NHS FOUNDATION TRUST':"london", "KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST":"london", 'LEWISHAM AND GREENWICH NHS TRUST':"london",
                        'MOORFIELDS EYE HOSPITAL NHS FOUNDATION TRUST':"london", 'ROYAL FREE LONDON NHS FOUNDATION TRUST':"london", 
                        "ST GEORGE'S UNIVERSITY HOSPITALS NHS FOUNDATION TRUST":"london", 'UNIVERSITY COLLEGE LONDON HOSPITALS NHS FOUNDATION TRUST':"london",
                        'BARKING, HAVERING AND REDBRIDGE UNIVERSITY HOSPITALS NHS TRUST':"london", 'CHELSEA AND WESTMINSTER HOSPITAL NHS FOUNDATION TRUST':"london", 
                        'EPSOM AND ST HELIER UNIVERSITY HOSPITALS NHS TRUST':"london", "GUY'S AND ST THOMAS' NHS FOUNDATION TRUST":"london", 
                        'IMPERIAL COLLEGE HEALTHCARE NHS TRUST':"london", 'KINGSTON HOSPITAL NHS FOUNDATION TRUST':"london", 
                        'LONDON NORTH WEST UNIVERSITY HEALTHCARE NHS TRUST':"london", 'NORTH MIDDLESEX UNIVERSITY HOSPITAL NHS TRUST':"london", 
                        'ROYAL NATIONAL ORTHOPAEDIC HOSPITAL NHS TRUST':"london", 'THE HILLINGDON HOSPITALS NHS FOUNDATION TRUST':"london", 
                        'WHITTINGTON HEALTH NHS TRUST':"london",
                        'BARNSLEY HOSPITAL NHS FOUNDATION TRUST':"ney", 'CALDERDALE AND HUDDERSFIELD NHS FOUNDATION TRUST':"ney", 
                        'DONCASTER AND BASSETLAW TEACHING HOSPITALS NHS FOUNDATION TRUST':"ney", 'HARROGATE AND DISTRICT NHS FOUNDATION TRUST':"ney", 
                        'LEEDS TEACHING HOSPITALS NHS TRUST':"ney", 'THE NEWCASTLE UPON TYNE HOSPITALS NHS FOUNDATION TRUST':"ney", 
                        'NORTH TEES AND HARTLEPOOL NHS FOUNDATION TRUST':"ney", 'NORTHUMBRIA HEALTHCARE NHS FOUNDATION TRUST':"ney", 
                        'SHEFFIELD TEACHING HOSPITALS NHS FOUNDATION TRUST':"ney", 'SOUTH TYNESIDE AND SUNDERLAND NHS FOUNDATION TRUST':"ney", 
                        'YORK AND SCARBOROUGH TEACHING HOSPITALS NHS FOUNDATION TRUST':"ney", 'AIREDALE NHS FOUNDATION TRUST':"ney", 
                        'BRADFORD TEACHING HOSPITALS NHS FOUNDATION TRUST':"ney", 'COUNTY DURHAM AND DARLINGTON NHS FOUNDATION TRUST':"ney", 
                        'GATESHEAD HEALTH NHS FOUNDATION TRUST':"ney", 'HULL UNIVERSITY TEACHING HOSPITALS NHS TRUST':"ney", 'MID YORKSHIRE HOSPITALS NHS TRUST':"ney", 
                        'NORTH CUMBRIA INTEGRATED CARE NHS FOUNDATION TRUST':"ney", 'NORTHERN LINCOLNSHIRE AND GOOLE NHS FOUNDATION TRUST':"ney", 
                        'SOUTH TEES HOSPITALS NHS FOUNDATION TRUST':"ney", 'THE ROTHERHAM NHS FOUNDATION TRUST':"ney",
                        'BUCKINGHAMSHIRE HEALTHCARE NHS TRUST':"seast", 
                        'EAST KENT HOSPITALS UNIVERSITY NHS FOUNDATION TRUST':"seast", 
                        'FRIMLEY HEALTH NHS FOUNDATION TRUST':"seast",
                        'ISLE OF WIGHT NHS TRUST':"seast",
                        'MEDWAY NHS FOUNDATION TRUST':"seast", 
                        'PORTSMOUTH HOSPITALS UNIVERSITY NATIONAL HEALTH SERVICE TRUST':"seast",
                        'ROYAL BERKSHIRE NHS FOUNDATION TRUST':"seast", 
                        'SURREY AND SUSSEX HEALTHCARE NHS TRUST':"seast", 
                        'UNIVERSITY HOSPITALS SUSSEX NHS FOUNDATION TRUST':"seast",
                        "ASHFORD AND ST PETER'S HOSPITALS NHS FOUNDATION TRUST":"seast",
                        'DARTFORD AND GRAVESHAM NHS TRUST':"seast",
                        'EAST SUSSEX HEALTHCARE NHS TRUST':"seast",
                        'HAMPSHIRE HOSPITALS NHS FOUNDATION TRUST':"seast", 
                        'MAIDSTONE AND TUNBRIDGE WELLS NHS TRUST':"seast",
                        'OXFORD UNIVERSITY HOSPITALS NHS FOUNDATION TRUST':"seast",
                        'QUEEN VICTORIA HOSPITAL NHS FOUNDATION TRUST':"seast", 
                        'ROYAL SURREY COUNTY HOSPITAL NHS FOUNDATION TRUST':"seast", 
                        'UNIVERSITY HOSPITAL SOUTHAMPTON NHS FOUNDATION TRUST':"seast",                                                
                        "ALDER HEY CHILDREN'S NHS FOUNDATION TRUST":"nwest", 
                        'BOLTON NHS FOUNDATION TRUST':"nwest", 
                        'EAST CHESHIRE NHS TRUST':"nwest", 
                        'LANCASHIRE TEACHING HOSPITALS NHS FOUNDATION TRUST':"nwest",
                        'LIVERPOOL UNIVERSITY HOSPITALS NHS FOUNDATION TRUST':"nwest", 
                        'MANCHESTER UNIVERSITY NHS FOUNDATION TRUST':"nwest",
                        'NORTHERN CARE ALLIANCE NHS FOUNDATION TRUST':"nwest", 
                        'ST HELENS AND KNOWSLEY TEACHING HOSPITALS NHS TRUST':"nwest", 
                        'TAMESIDE AND GLOSSOP INTEGRATED CARE NHS FOUNDATION TRUST':"nwest", 
                        'UNIVERSITY HOSPITALS OF MORECAMBE BAY NHS FOUNDATION TRUST':"nwest", 
                        'WIRRAL UNIVERSITY TEACHING HOSPITAL NHS FOUNDATION TRUST':"nwest", 
                        'BLACKPOOL TEACHING HOSPITALS NHS FOUNDATION TRUST':"nwest",
                        'COUNTESS OF CHESTER HOSPITAL NHS FOUNDATION TRUST':"nwest",
                        'EAST LANCASHIRE HOSPITALS NHS TRUST':"nwest", 
                        'LIVERPOOL HEART AND CHEST HOSPITAL NHS FOUNDATION TRUST':"nwest", 
                        "LIVERPOOL WOMEN'S NHS FOUNDATION TRUST":"nwest",
                        'MID CHESHIRE HOSPITALS NHS FOUNDATION TRUST':"nwest", 
                        'SOUTHPORT AND ORMSKIRK HOSPITAL NHS TRUST':"nwest", 
                        'STOCKPORT NHS FOUNDATION TRUST':"nwest",
                        'THE WALTON CENTRE NHS FOUNDATION TRUST':"nwest", 
                        'WARRINGTON AND HALTON TEACHING HOSPITALS NHS FOUNDATION TRUST':"nwest",
                        'WRIGHTINGTON, WIGAN AND LEIGH NHS FOUNDATION TRUST':"nwest",                                 
                        'BEDFORDSHIRE HOSPITALS NHS FOUNDATION TRUST':"east", 
                        'EAST AND NORTH HERTFORDSHIRE NHS TRUST':"east", 
                        'JAMES PAGET UNIVERSITY HOSPITALS NHS FOUNDATION TRUST':"east", 
                        'MILTON KEYNES UNIVERSITY HOSPITAL NHS FOUNDATION TRUST':"east",
                        'NORTH WEST ANGLIA NHS FOUNDATION TRUST':"east", 
                        'THE PRINCESS ALEXANDRA HOSPITAL NHS TRUST':"east",
                        'WEST HERTFORDSHIRE TEACHING HOSPITALS NHS TRUST':"east", 
                        'CAMBRIDGE UNIVERSITY HOSPITALS NHS FOUNDATION TRUST':"east", 
                        'EAST SUFFOLK AND NORTH ESSEX NHS FOUNDATION TRUST':"east", 
                        'MID AND SOUTH ESSEX NHS FOUNDATION TRUST':"east", 
                        'NORFOLK AND NORWICH UNIVERSITY HOSPITALS NHS FOUNDATION TRUST':"east", 
                        'ROYAL PAPWORTH HOSPITAL NHS FOUNDATION TRUST':"east",
                        "THE QUEEN ELIZABETH HOSPITAL, KING'S LYNN, NHS FOUNDATION TRUST":"east",
                        'WEST SUFFOLK NHS FOUNDATION TRUST':"east"}

# -- funcs --
def make_new_hospital_data_dict_sync(data_dict) -> tuple[str, dict]:
    """ """
    new_hospital_data_dict = {}
    hospital_name = data_dict["Provider_Name"]
    hospital_wait_times_list = (data_dict["TFC"])
    for department_dict in hospital_wait_times_list:
        department_name = department_dict["TFC_Description"]
        # Average waiting time for first outpatient appointment at this hospital for this specialty
        department_first_wait = department_dict["First_Av_Wait"]
        # Average waiting time for treatment at this hospital for this specialty
        department_avg_wait = department_dict["Av_Wait"]
        # make the key the deparment name (tfc desc) and the value a tuple of the two wait times
        new_hospital_data_dict[department_name] = (department_first_wait, department_avg_wait)
    return((hospital_name, new_hospital_data_dict))

async def make_new_hospital_data_dict(data_dict):
    """ make our dictionary creator function asyncronous """
    # tbf the make new dict function is fast enough to not require async but thats only on my machine,
    # speed up probably noticable on cloud provision machine
    return await(asyncio.to_thread(make_new_hospital_data_dict_sync, data_dict))

def http_get_sync(url:str) -> JSONobject:
    """
    note : catches potential error that only happens on web app (not locally - weird af)
    if too many error just wait it out for a bit then make the request again, seems fine for now anyways (famous last words)
    """
    req = Request(url, headers=header)
    try:
        webpage = urlopen(req).read()
        return(webpage)
    except urllib.error.HTTPError as e:
        print('HTTPError: {}'.format(e.code))
        time.sleep(5)
        webpage = urlopen(req).read()
        return(webpage)
        
async def http_get(url:str) -> JSONobject:
    """ make our http get function asyncronous """
    return await(asyncio.to_thread(http_get_sync, url))

async def get_code_data(given_url) -> str:
    """ """
    url = given_url
    page_data = await http_get(url)
    hospital_code = await get_hospital_code(page_data)
    return(str(hospital_code))

def convert_to_soup_sync(page_data) -> bs4.BeautifulSoup:
    """ """
    page_soup = soup(page_data, "html.parser")
    return(page_soup)

async def convert_to_soup(page_data):
    """ make our convert to soup function asyncronous """
    return await(asyncio.to_thread(convert_to_soup_sync, page_data))

async def get_hospital_code(page_data):
    """ """
    page_soup = await convert_to_soup(page_data)
    hospital_code = page_soup.find("div", {"class": "320"}).get("id")
    return(hospital_code)

async def get_hospital_data(page_data) -> dict:
    """ """
    page_soup = await convert_to_soup(page_data)
    for hospital_json in page_soup: 
        hospital_data_dict = json.loads(hospital_json)[0]
        return(hospital_data_dict)

async def get_page_data(given_url:str) -> dict:
    """ """
    url = given_url
    page_data = await http_get(url)
    hospital_data = await get_hospital_data(page_data)
    return(hospital_data)

def get_region_from_name(hospital_name:str) -> str:
    """ """
    # should be using dictionaries as its quicker to check keys than to loop a list duh!
    region = hospitals_regions[hospital_name]
    return(region)

def add_first_wait_times_to_db_sync(hospital_data):
    """ for one hospital """
    # preset our variables to false, which we will turn on if the valid departments data is found
    want_breast, want_cardiology, want_cardiothoracic = False, False, False
    want_clinical_haemotology, want_colorectal, want_dermatology, want_ear = False, False, False, False
    want_gastroenterology, want_general, want_general_surgery, want_gynaecology = False, False, False, False
    want_maxillofacial, want_neurology, want_neurosurgical = False, False, False
    want_ophthalmology, want_oral, want_paediatric = False, False, False
    want_paediatric_surgery, want_pain, want_plastic = False, False, False    
    want_respiratory, want_rheumatology, want_spinal  = False, False, False 
    want_trauma, want_upper, want_urology, want_vascular  = False, False, False, False
    # --
    dep_dict = {"Breast Surgery": want_breast, "Cardiology": want_cardiology, "Cardiothoracic Surgery":want_cardiothoracic,
                    "Clinical Haematology": want_clinical_haemotology, "Colorectal Surgery": want_colorectal , "Dermatology": want_dermatology,
                    "Ear Nose and Throat": want_ear, "Gastroenterology": want_gastroenterology, 
                    "General Internal Medicine": want_general, "General Surgery": want_general_surgery, "Gynaecology":want_gynaecology, 
                    "Maxillofacial Surgery": want_maxillofacial, "Neurology": want_neurology , "Neurosurgical": want_neurosurgical,
                    "Ophthalmology": want_ophthalmology , "Oral Surgery": want_oral,
                    "Paediatric": want_paediatric, "Paediatric Surgery": want_paediatric_surgery,
                    "Pain Management": want_pain, "Plastic Surgery": want_plastic,
                    "Respiratory Medicine": want_respiratory, "Rheumatology": want_rheumatology,
                    "Spinal Surgery": want_spinal, "Trauma and Orthopaedic": want_trauma,
                    "Upper Gastrointestinal Surgery": want_upper, "Urology": want_urology, "Vascular Surgery":want_vascular}

    # sort it alphabetically so it matches the flags
    data_dict=dict(sorted(hospital_data[1].items(), key=lambda item: item[0]))
    # loop the data, and prepare to be inserted for the hospital (only one hospital)
    params_list = []
    params_list.append(hospital_data[0])
    params_list.append(get_region_from_name(hospital_data[0]))
    for department, wait_times in data_dict.items():
        if department in dep_dict.keys():
            dep_dict[department] = True
            params_list.append(wait_times[0])
    # --
    params_list = tuple(params_list)
    # --
    # always 1, then minus 1 as it has the hopsital name
    insert_db_data([params_list], (len(params_list) - 1), dep_dict["Breast Surgery"], dep_dict["Cardiology"], dep_dict["Cardiothoracic Surgery"],
                        dep_dict["Clinical Haematology"], dep_dict["Colorectal Surgery"], dep_dict["Dermatology"],
                        dep_dict["Ear Nose and Throat"], dep_dict["Gastroenterology"], dep_dict["General Internal Medicine"],
                        dep_dict["General Surgery"], dep_dict["Gynaecology"], dep_dict["Maxillofacial Surgery"],
                        dep_dict["Neurology"], dep_dict["Neurosurgical"], dep_dict["Ophthalmology"],
                        dep_dict["Oral Surgery"], dep_dict["Paediatric"], dep_dict["Paediatric Surgery"],
                        dep_dict["Pain Management"], dep_dict["Plastic Surgery"], dep_dict["Respiratory Medicine"],
                        dep_dict["Rheumatology"], dep_dict["Spinal Surgery"], dep_dict["Trauma and Orthopaedic"],
                        dep_dict["Upper Gastrointestinal Surgery"], dep_dict["Urology"], dep_dict["Vascular Surgery"])

# naming convension is just the first word except for clinical haemotology, general surgery, and paediatric surgery which are both words (full string)
def insert_db_data(entries:list[tuple], amount_of_departments:int, want_breast:bool = False, want_cardiology:bool = False,
                    want_cardiothoracic:bool = False,
                    want_clinical_haemotology:bool = False, want_colorectal:bool = False, want_dermatology:bool = False, want_ear:bool = False, 
                    want_gastroenterology:bool = False, want_general:bool = False, want_general_surgery:bool = False, want_gynaecology:bool = False,
                    want_maxillofacial:bool = False, want_neurology:bool = False, want_neurosurgical:bool = False, 
                    want_ophthalmology:bool = False, want_oral:bool = False, want_paediatric:bool = False, 
                    want_paediatric_surgery:bool = False, want_pain:bool = False, want_plastic:bool = False,
                    want_respiratory:bool = False, want_rheumatology:bool = False, want_spinal:bool = False,
                    want_trauma:bool = False, want_upper:bool = False, want_urology:bool = False, want_vascular:bool = False, table_name:str = "first_apt"):             
    """
    //desc : uses extended insert to drastically reduce insert speed, takes a list of tuples which are unpacked and extended then sent as one long ass tuple
    //params : entries (as list of tuples), amount_of_entries (as int) creates the values part of the query
    // returns : None
    """
    for entry in entries:
        # Extract hospital_name and date from entry
        # Assuming the hospital_name is the first item and the date is the last item in each entry
        hospital_name = entry[0]
        current_date = datetime.date.today()
        date = str(current_date)
        # Only insert data if no matching entry is found in the database
        if not db.check_existing_entry(hospital_name, date, table_name):
            print("Found Existing Data For Today - Skipping Entry")
        else:
            print("No Existing Entry For Today - Saving Data")

            param_list, param_tuple = [], ()
            # extend the given data set into one long list with all the data
            [param_list.extend(entry) for entry in entries]
            # then convert it to a tuple to be used as the parameter variable
            param_tuple = tuple(param_list)
            # amount of departments should be dynamic from the amount of booleans that are true duh    
            placeholder = "%s, "
            temp_string = placeholder * (amount_of_departments) # minus one for the end (nope now thats the hospital name)
            values_string = "(" + temp_string + "%s),"
            # the end slice removes the final trailing comma
            final_values = values_string[:-1]
            # create prepared query with given parameters for 5 entries
            sql_1 = f"INSERT INTO {table_name} (hospital_name, hospital_region, {'`Breast Surgery`,' if want_breast else ''} {'Cardiology,' if want_cardiology else ''} \
                    {'`Cardiothoracic Surgery`,' if want_cardiothoracic else ''} {'`Clinical Haematology`,' if want_clinical_haemotology else ''} \
                    {'`Colorectal Surgery`,' if want_colorectal else ''} {'Dermatology,' if want_dermatology else ''} \
                    {'`Ear Nose and Throat`,' if want_ear else ''} {'Gastroenterology,' if want_gastroenterology else ''} \
                    {'`General Surgery`,' if want_general_surgery else ''} {'Gynaecology,' if want_gynaecology else ''} \
                    {'`General Internal Medicine`,' if want_general else ''} {'`Maxillofacial Surgery`,' if want_maxillofacial else ''} \
                    {'Neurosurgical,' if want_neurosurgical else ''} {'Neurology,' if want_neurology else ''} {'Urology,' if want_urology else ''} \
                    {'`Trauma and Orthopaedic`,' if want_trauma else ''} {'Ophthalmology,' if want_ophthalmology else ''} \
                    {'`Oral Surgery`,' if want_oral else ''} {'Paediatric,' if want_paediatric else ''} \
                    {'`Plastic Surgery`,' if want_plastic else ''} {'`Paediatric Surgery`,' if want_paediatric_surgery else ''} \
                    {'`Pain Management`,' if want_pain else ''} {'`Respiratory Medicine`,' if want_respiratory else ''} \
                    {'Rheumatology,' if want_rheumatology else ''} {'`Spinal Surgery`,' if want_spinal else ''} \
                    {'`Upper Gastrointestinal Surgery`,' if want_upper else ''} {'`Vascular Surgery`,' if want_vascular else ''}"
            # create the sql string ensuring that the insert columns are formatted properly within brackets plus with correct use of spacing and commas
            sql_2 = f"VALUES {final_values}" 
            last_comma = sql_1.rfind(",")
            sql_1 = sql_1[:last_comma]
            sql = sql_1 + ") " + sql_2
            # send off the query
            db.secure_add_to_db(sql, param_tuple)


def create_base_first_apt_table():
    """
    //desc : create wait to first appointment table, 27 departments, note back ticks are necessary due to spaces in department names, could add hospital_code too
    //params :
    //returns :
    """
    print(f"Attempting To Create Base Table")
    # table creation query 
    query = "CREATE TABLE IF NOT EXISTS first_apt (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, hospital_name VARCHAR(200) NOT NULL, hospital_region VARCHAR(20) NOT NULL,\
            `Breast Surgery` INT(3) NULL, Cardiology INT(3) NULL, `Cardiothoracic Surgery` INT(3) NULL, `Clinical Haematology` INT(3) NULL, \
            `Colorectal Surgery` INT(3) NULL, Dermatology INT(3) NULL, `Ear Nose and Throat` INT(3) NULL, Gastroenterology INT(3) NULL, \
            `General Surgery` INT(3) NULL, Gynaecology INT(3) NULL, `General Internal Medicine` INT(3) NULL,`Maxillofacial Surgery` INT(3) NULL, \
            Neurology INT(3) NULL, Neurosurgical INT(3) NULL, Ophthalmology INT(3) NULL, `Oral Surgery` INT(3) NULL, \
            Paediatric INT(3) NULL, `Paediatric Surgery` INT(3) NULL, `Pain Management` INT(3) NULL, `Plastic Surgery` INT(3) NULL, \
            `Respiratory Medicine` INT(3) NULL, Rheumatology INT(3) NULL, `Spinal Surgery` INT(3) NULL, `Trauma and Orthopaedic` INT(3) NULL, \
            `Upper Gastrointestinal Surgery` INT(3) NULL, Urology INT(3) NULL, `Vascular Surgery` INT(3) NULL, \
            created_on datetime NOT NULL DEFAULT CURRENT_TIMESTAMP);"
    # commit the table to db
    db.secure_add_to_db(query)

async def main() -> None:
    # --
    print(f"Running CICD Pipeline")
    start_time = time.time()
    # --
    hosp_codes_list = ["RRK", "RKB", "RWE", "RBK"]
    webpage_data_list = await asyncio.gather(*[get_page_data(f"https://www.myplannedcare.nhs.uk/mpcjson/{code}.json") for code in set(hosp_codes_list)])
    hospital_data_list = await asyncio.gather(*[make_new_hospital_data_dict(hospital) for hospital in webpage_data_list])
    # -- 
    for hospital_data in hospital_data_list:
        add_first_wait_times_to_db_sync(hospital_data)
    # --
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Completed In {elapsed_time}s")



# -- driver --    
if __name__ == "__main__": 
    create_base_first_apt_table()
    asyncio.run(main()) 


# N0TE
# - class based, data structures, design patterns, think about this stuff during / for a first refactor (tho dont take donkeys on this project tho)

# RNRN
# - GET THIS WORKING ON CICD - TO TEST JUST EDIT ENTRIES TO BE FROM YESTERDAY
# - get to the whole collating daily averages thing after
#   - as per below ensure this is designed with the web app in mind
# - get some basic web app back up but instead of their api use my own db nice!
# - then get some basic web app up to start legit just put in your postcode and get a list of trusts, then start doing the whole map thing with this and expand from there

# TO CONFIRM
# - MAKE SURE IT SKIPS OVER IF THERE ARE STILL VALID

# GET GPT TO...
# - AS PER EXISTING PRINTS, CONVERT TO LOGS, ENSURE THEY ARE GIVING MORE ACCURATE INFO i.e. the hosp name duh