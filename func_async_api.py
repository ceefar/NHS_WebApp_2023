# -- author : ceefar --
# -- project : nhs etl 2023 --

# -- imports --
import asyncio
import bs4 
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import json
import urllib.error
import datetime
import time
# -- internal imports --
from func_misc import *
from cls_db import Database
# -- currently unused imports --
import requests

# -- global db conn --
db = Database()

# -- funcs --
def make_new_hospital_data_dict_sync(data_dict) -> tuple[str, dict]:
    """ creates a more accessible data dict from the json """
    new_hospital_data_dict = {}
    hospital_name = data_dict["Provider_Name"]
    hospital_wait_times_list = (data_dict["TFC"])
    for department_dict in hospital_wait_times_list:
        department_name = department_dict["TFC_Description"]
        department_first_wait = department_dict["First_Av_Wait"] # first appointment
        department_avg_wait = department_dict["Av_Wait"] # avg wait
        # -- make the key the deparment name (tfc desc) and the value a tuple of the two wait times --
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
    """ add KeyError error handling here pls """
    region = Misc.hospitals_regions[hospital_name]
    return(region)

def add_first_wait_times_to_db_sync(hospital_data):
    """ for one hospital, wait (in weeks) until first appointment """
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

# N0TE - PLEASE JUST CREATE ONE FUNCTION TO HANDLE BOTH!
def add_avg_wait_times_to_db_sync(hospital_data):
    """ for one hospital, wait (in weeks) until treatment (tbc) """
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
            params_list.append(wait_times[1])
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
                        dep_dict["Upper Gastrointestinal Surgery"], dep_dict["Urology"], dep_dict["Vascular Surgery"], table_name="avg_wait")

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
        # -- only insert data if no matching entry for the current date exists in the database --
        if not db.check_existing_entry(hospital_name, date, table_name):
            print(f"[ Skipping Entry ]\n - Found Existing Data For {hospital_name} - {str(date)}")
        else:
            print(f"[ Saving Data ]\n - No Data Found For {hospital_name} - {str(date)}")
            # --
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

def create_base_first_apt_tables():
    """
    //desc : create wait to first appointment table, 27 departments, note back ticks are necessary due to spaces in department names, could add hospital_code too
    //params :
    //returns :
    """
    print(f"\n- - - - - - - - - -\n[ Checking For Base Tables ]\n- - - - - - - - - -")
    # -- table creation queries --  
    first_apt_table_query = "CREATE TABLE IF NOT EXISTS first_apt (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, hospital_name VARCHAR(200) NOT NULL, hospital_region VARCHAR(20) NOT NULL,\
            `Breast Surgery` INT(3) NULL, Cardiology INT(3) NULL, `Cardiothoracic Surgery` INT(3) NULL, `Clinical Haematology` INT(3) NULL, \
            `Colorectal Surgery` INT(3) NULL, Dermatology INT(3) NULL, `Ear Nose and Throat` INT(3) NULL, Gastroenterology INT(3) NULL, \
            `General Surgery` INT(3) NULL, Gynaecology INT(3) NULL, `General Internal Medicine` INT(3) NULL,`Maxillofacial Surgery` INT(3) NULL, \
            Neurology INT(3) NULL, Neurosurgical INT(3) NULL, Ophthalmology INT(3) NULL, `Oral Surgery` INT(3) NULL, \
            Paediatric INT(3) NULL, `Paediatric Surgery` INT(3) NULL, `Pain Management` INT(3) NULL, `Plastic Surgery` INT(3) NULL, \
            `Respiratory Medicine` INT(3) NULL, Rheumatology INT(3) NULL, `Spinal Surgery` INT(3) NULL, `Trauma and Orthopaedic` INT(3) NULL, \
            `Upper Gastrointestinal Surgery` INT(3) NULL, Urology INT(3) NULL, `Vascular Surgery` INT(3) NULL, \
            created_on datetime NOT NULL DEFAULT CURRENT_TIMESTAMP);"
    avg_wait_table_query = "CREATE TABLE IF NOT EXISTS avg_wait (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, hospital_name VARCHAR(200) NOT NULL, hospital_region VARCHAR(20) NOT NULL,\
            `Breast Surgery` INT(3) NULL, Cardiology INT(3) NULL, `Cardiothoracic Surgery` INT(3) NULL, `Clinical Haematology` INT(3) NULL, \
            `Colorectal Surgery` INT(3) NULL, Dermatology INT(3) NULL, `Ear Nose and Throat` INT(3) NULL, Gastroenterology INT(3) NULL, \
            `General Surgery` INT(3) NULL, Gynaecology INT(3) NULL, `General Internal Medicine` INT(3) NULL,`Maxillofacial Surgery` INT(3) NULL, \
            Neurology INT(3) NULL, Neurosurgical INT(3) NULL, Ophthalmology INT(3) NULL, `Oral Surgery` INT(3) NULL, \
            Paediatric INT(3) NULL, `Paediatric Surgery` INT(3) NULL, `Pain Management` INT(3) NULL, `Plastic Surgery` INT(3) NULL, \
            `Respiratory Medicine` INT(3) NULL, Rheumatology INT(3) NULL, `Spinal Surgery` INT(3) NULL, `Trauma and Orthopaedic` INT(3) NULL, \
            `Upper Gastrointestinal Surgery` INT(3) NULL, Urology INT(3) NULL, `Vascular Surgery` INT(3) NULL, \
            created_on datetime NOT NULL DEFAULT CURRENT_TIMESTAMP);"
    averages_table_mids_query = "CREATE TABLE IF NOT EXISTS daily_department_averages_mids ( \
            id INT AUTO_INCREMENT PRIMARY KEY, date DATE NOT NULL, avg_breast_surgery DECIMAL(5,2), avg_cardiology DECIMAL(5,2), avg_cardiothoracic_surgery DECIMAL(5,2), avg_clinical_haematology DECIMAL(5,2), avg_colorectal_surgery DECIMAL(5,2), avg_dermatology DECIMAL(5,2), avg_ent DECIMAL(5,2), avg_gastroenterology DECIMAL(5,2), avg_general_surgery DECIMAL(5,2), \
            avg_gynaecology DECIMAL(5,2), avg_general_internal_medicine DECIMAL(5,2), avg_maxillofacial_surgery DECIMAL(5,2), avg_neurology DECIMAL(5,2), avg_neurosurgical DECIMAL(5,2), avg_ophthalmology DECIMAL(5,2), avg_oral_surgery DECIMAL(5,2), avg_paediatric DECIMAL(5,2), avg_paediatric_surgery DECIMAL(5,2), avg_pain_management DECIMAL(5,2), \
            avg_plastic_surgery DECIMAL(5,2), avg_respiratory_medicine DECIMAL(5,2), avg_rheumatology DECIMAL(5,2), avg_spinal_surgery DECIMAL(5,2), avg_trauma_orthopaedic DECIMAL(5,2), avg_upper_gi_surgery DECIMAL(5,2), avg_urology DECIMAL(5,2), avg_vascular_surgery DECIMAL(5,2))"
    averages_table_london_query = "CREATE TABLE IF NOT EXISTS daily_department_averages_london ( \
            id INT AUTO_INCREMENT PRIMARY KEY, date DATE NOT NULL, avg_breast_surgery DECIMAL(5,2), avg_cardiology DECIMAL(5,2), avg_cardiothoracic_surgery DECIMAL(5,2), avg_clinical_haematology DECIMAL(5,2), avg_colorectal_surgery DECIMAL(5,2), avg_dermatology DECIMAL(5,2), avg_ent DECIMAL(5,2), avg_gastroenterology DECIMAL(5,2), avg_general_surgery DECIMAL(5,2), \
            avg_gynaecology DECIMAL(5,2), avg_general_internal_medicine DECIMAL(5,2), avg_maxillofacial_surgery DECIMAL(5,2), avg_neurology DECIMAL(5,2), avg_neurosurgical DECIMAL(5,2), avg_ophthalmology DECIMAL(5,2), avg_oral_surgery DECIMAL(5,2), avg_paediatric DECIMAL(5,2), avg_paediatric_surgery DECIMAL(5,2), avg_pain_management DECIMAL(5,2), \
            avg_plastic_surgery DECIMAL(5,2), avg_respiratory_medicine DECIMAL(5,2), avg_rheumatology DECIMAL(5,2), avg_spinal_surgery DECIMAL(5,2), avg_trauma_orthopaedic DECIMAL(5,2), avg_upper_gi_surgery DECIMAL(5,2), avg_urology DECIMAL(5,2), avg_vascular_surgery DECIMAL(5,2))"
    averages_table_swest_query = "CREATE TABLE IF NOT EXISTS daily_department_averages_swest ( \
            id INT AUTO_INCREMENT PRIMARY KEY, date DATE NOT NULL, avg_breast_surgery DECIMAL(5,2), avg_cardiology DECIMAL(5,2), avg_cardiothoracic_surgery DECIMAL(5,2), avg_clinical_haematology DECIMAL(5,2), avg_colorectal_surgery DECIMAL(5,2), avg_dermatology DECIMAL(5,2), avg_ent DECIMAL(5,2), avg_gastroenterology DECIMAL(5,2), avg_general_surgery DECIMAL(5,2), \
            avg_gynaecology DECIMAL(5,2), avg_general_internal_medicine DECIMAL(5,2), avg_maxillofacial_surgery DECIMAL(5,2), avg_neurology DECIMAL(5,2), avg_neurosurgical DECIMAL(5,2), avg_ophthalmology DECIMAL(5,2), avg_oral_surgery DECIMAL(5,2), avg_paediatric DECIMAL(5,2), avg_paediatric_surgery DECIMAL(5,2), avg_pain_management DECIMAL(5,2), \
            avg_plastic_surgery DECIMAL(5,2), avg_respiratory_medicine DECIMAL(5,2), avg_rheumatology DECIMAL(5,2), avg_spinal_surgery DECIMAL(5,2), avg_trauma_orthopaedic DECIMAL(5,2), avg_upper_gi_surgery DECIMAL(5,2), avg_urology DECIMAL(5,2), avg_vascular_surgery DECIMAL(5,2))"
    averages_table_ney_query = "CREATE TABLE IF NOT EXISTS daily_department_averages_ney ( \
            id INT AUTO_INCREMENT PRIMARY KEY, date DATE NOT NULL, avg_breast_surgery DECIMAL(5,2), avg_cardiology DECIMAL(5,2), avg_cardiothoracic_surgery DECIMAL(5,2), avg_clinical_haematology DECIMAL(5,2), avg_colorectal_surgery DECIMAL(5,2), avg_dermatology DECIMAL(5,2), avg_ent DECIMAL(5,2), avg_gastroenterology DECIMAL(5,2), avg_general_surgery DECIMAL(5,2), \
            avg_gynaecology DECIMAL(5,2), avg_general_internal_medicine DECIMAL(5,2), avg_maxillofacial_surgery DECIMAL(5,2), avg_neurology DECIMAL(5,2), avg_neurosurgical DECIMAL(5,2), avg_ophthalmology DECIMAL(5,2), avg_oral_surgery DECIMAL(5,2), avg_paediatric DECIMAL(5,2), avg_paediatric_surgery DECIMAL(5,2), avg_pain_management DECIMAL(5,2), \
            avg_plastic_surgery DECIMAL(5,2), avg_respiratory_medicine DECIMAL(5,2), avg_rheumatology DECIMAL(5,2), avg_spinal_surgery DECIMAL(5,2), avg_trauma_orthopaedic DECIMAL(5,2), avg_upper_gi_surgery DECIMAL(5,2), avg_urology DECIMAL(5,2), avg_vascular_surgery DECIMAL(5,2))"
    averages_table_nwest_query = "CREATE TABLE IF NOT EXISTS daily_department_averages_nwest ( \
            id INT AUTO_INCREMENT PRIMARY KEY, date DATE NOT NULL, avg_breast_surgery DECIMAL(5,2), avg_cardiology DECIMAL(5,2), avg_cardiothoracic_surgery DECIMAL(5,2), avg_clinical_haematology DECIMAL(5,2), avg_colorectal_surgery DECIMAL(5,2), avg_dermatology DECIMAL(5,2), avg_ent DECIMAL(5,2), avg_gastroenterology DECIMAL(5,2), avg_general_surgery DECIMAL(5,2), \
            avg_gynaecology DECIMAL(5,2), avg_general_internal_medicine DECIMAL(5,2), avg_maxillofacial_surgery DECIMAL(5,2), avg_neurology DECIMAL(5,2), avg_neurosurgical DECIMAL(5,2), avg_ophthalmology DECIMAL(5,2), avg_oral_surgery DECIMAL(5,2), avg_paediatric DECIMAL(5,2), avg_paediatric_surgery DECIMAL(5,2), avg_pain_management DECIMAL(5,2), \
            avg_plastic_surgery DECIMAL(5,2), avg_respiratory_medicine DECIMAL(5,2), avg_rheumatology DECIMAL(5,2), avg_spinal_surgery DECIMAL(5,2), avg_trauma_orthopaedic DECIMAL(5,2), avg_upper_gi_surgery DECIMAL(5,2), avg_urology DECIMAL(5,2), avg_vascular_surgery DECIMAL(5,2))"
    averages_table_seast_query = "CREATE TABLE IF NOT EXISTS daily_department_averages_seast ( \
            id INT AUTO_INCREMENT PRIMARY KEY, date DATE NOT NULL, avg_breast_surgery DECIMAL(5,2), avg_cardiology DECIMAL(5,2), avg_cardiothoracic_surgery DECIMAL(5,2), avg_clinical_haematology DECIMAL(5,2), avg_colorectal_surgery DECIMAL(5,2), avg_dermatology DECIMAL(5,2), avg_ent DECIMAL(5,2), avg_gastroenterology DECIMAL(5,2), avg_general_surgery DECIMAL(5,2), \
            avg_gynaecology DECIMAL(5,2), avg_general_internal_medicine DECIMAL(5,2), avg_maxillofacial_surgery DECIMAL(5,2), avg_neurology DECIMAL(5,2), avg_neurosurgical DECIMAL(5,2), avg_ophthalmology DECIMAL(5,2), avg_oral_surgery DECIMAL(5,2), avg_paediatric DECIMAL(5,2), avg_paediatric_surgery DECIMAL(5,2), avg_pain_management DECIMAL(5,2), \
            avg_plastic_surgery DECIMAL(5,2), avg_respiratory_medicine DECIMAL(5,2), avg_rheumatology DECIMAL(5,2), avg_spinal_surgery DECIMAL(5,2), avg_trauma_orthopaedic DECIMAL(5,2), avg_upper_gi_surgery DECIMAL(5,2), avg_urology DECIMAL(5,2), avg_vascular_surgery DECIMAL(5,2))"
    averages_table_east_query = "CREATE TABLE IF NOT EXISTS daily_department_averages_east ( \
            id INT AUTO_INCREMENT PRIMARY KEY, date DATE NOT NULL, avg_breast_surgery DECIMAL(5,2), avg_cardiology DECIMAL(5,2), avg_cardiothoracic_surgery DECIMAL(5,2), avg_clinical_haematology DECIMAL(5,2), avg_colorectal_surgery DECIMAL(5,2), avg_dermatology DECIMAL(5,2), avg_ent DECIMAL(5,2), avg_gastroenterology DECIMAL(5,2), avg_general_surgery DECIMAL(5,2), \
            avg_gynaecology DECIMAL(5,2), avg_general_internal_medicine DECIMAL(5,2), avg_maxillofacial_surgery DECIMAL(5,2), avg_neurology DECIMAL(5,2), avg_neurosurgical DECIMAL(5,2), avg_ophthalmology DECIMAL(5,2), avg_oral_surgery DECIMAL(5,2), avg_paediatric DECIMAL(5,2), avg_paediatric_surgery DECIMAL(5,2), avg_pain_management DECIMAL(5,2), \
            avg_plastic_surgery DECIMAL(5,2), avg_respiratory_medicine DECIMAL(5,2), avg_rheumatology DECIMAL(5,2), avg_spinal_surgery DECIMAL(5,2), avg_trauma_orthopaedic DECIMAL(5,2), avg_upper_gi_surgery DECIMAL(5,2), avg_urology DECIMAL(5,2), avg_vascular_surgery DECIMAL(5,2))"
    # -- commit the tables to db -- 
    table_queries = [first_apt_table_query, avg_wait_table_query, averages_table_mids_query, averages_table_london_query, averages_table_swest_query, averages_table_ney_query, averages_table_nwest_query, averages_table_seast_query, averages_table_east_query]
    [db.secure_add_to_db(table_query) for table_query in table_queries] 

def run_averages_stored_procedure(extension=False):
    # -- check if table has data for the current day
    today = datetime.date.today()
    if not extension:
        regions = ["mids", "london", "swest", "ney"]
    else:
        regions = ["seast", "nwest", "east"]
    # -- 
    for region in regions:
        query = f"SELECT COUNT(*) FROM daily_department_averages_{region} WHERE date = '{today}';"
        result = db.secure_get_from_db(query)
        data_exists = result[0][0]
        # -- if data doesnt exist then run the stored procedure to process the averages for first_apts in mids --
        if data_exists == 0:
            print(f"\n- - - - - - - - - -\n[ Running Stored Procedure - {region.title()} ]\n- - - - - - - - - -")
            query = f"CALL InsertDailyAverages{region.title()}();"
            db.secure_add_to_db(query) 
            print(f"\n- - - - - - - - - -\n[ First Apt Averages Data [ {region.title()} ] Updated Successfully ]\n- - - - - - - - - -")
        else:
            print(f"\n- - - - - - - - - -\n[ Skipping Stored Procedure [ {region.title()} ] Execution As Data Exists ]\n- - - - - - - - - -")


