# project : nhs etl 
# file : my planned care api scraper 
# author : ceefar

# -- imports --
import requests
import json
import codecs # can be removed if necessary as alternative functionality has been added
from pprint import pprint # will remove in future

# -- predefine some handy objects --
JSON = int | str | float | bool | None | dict [str, "JSON"] | list["JSON"]
JSONobject = dict[str, JSON]
JSONList = list[JSON]
 
# -- get json response from api -- 
def get_json_response_from_mpc(provider_code:str):
    url = f"https://www.myplannedcare.nhs.uk/mpcjson/{provider_code}.json"
    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}
    response = requests.request("GET", url, headers=header)
    return response

def convert_response_to_json_via_codex(page_response:str) -> JSONobject:
    """ uses the codex module to remove the bom """
    decoded_data=codecs.decode(page_response.encode(), 'utf-8-sig')
    data = json.loads(decoded_data)
    return data
 
def convert_response_to_json(page_response:str) -> JSONobject:
    """ due to BOM (byte order mark)... without using codecs, also allows us to get additional information from the api call that codex removes with the bom during decoding """
    dict_start_pos = page_response.find("{")
    dict_end_pos = page_response.rfind("}") + 1
    dict_string = page_response[dict_start_pos : dict_end_pos]
    dict_json = json.loads(dict_string)
    return dict_json

def get_department_wait_times_from_json_response(json:JSONobject):
    dept_wait_times_json = json.get("TFC")
    return dept_wait_times_json
 
# -- main -- 
if __name__ == "__main__":
    response = get_json_response_from_mpc("RRK")

    page_json = convert_response_to_json(response.text) # page_json = convert_response_to_json_via_codex(response.text) # < if using codex the need to unpack the return => page_json[0]

    prov_code = page_json.get("Provider_Code")
    prov_name = page_json.get("Provider_Name")
    prov_full = page_json.get("Provider_Full")
    week_ending = page_json.get("WeekEnding")

    print(f"{prov_code}")
    print(f"{prov_name}")
    print(f"{prov_full}")
    print(f"{week_ending}")

    page_json = convert_response_to_json_via_codex(response.text)

    for item in page_json[0].get("TFC"):
        dept_code = item["TFC_Code"]
        dept_name = item["TFC_Description"]
        dept_full = item["Treatment_Function"]
        first_avg_wait = item["First_Av_Wait"]
        avg_wait = item["Av_Wait"]

        print(f"{item}")
        print(f"{dept_code}")
        print(f"{dept_name}")
        print(f"{dept_full}")
        print(f"{first_avg_wait}")
        print(f"{avg_wait}")



# get codes, unsure of the 'best' way to do this but for now i think just group them by region and have them hardcoded since i have them
# loop over all codes asycnronously 
# store the data locally (mays well do this anyway huh? - atleast for now, maybe not in cicd?)
# upload it to a new database

# then do a basic page to test it works fine
# then idk whatever either page or cicd or ...

# initially plis make 2 versions of the test page, one working via my db and one working via api (showing the same data)
# - as ideally i would like that functionality, maybe just for one page or whatever but still

# - do a simple first version then we'll think about a proper or improved schema when adding the csv stuff
# - actually guna do that today too cause can actually do it dynamically (just get legit all the dates of data too but obvs will have cicd to do it monthly)
#   - for this can actually use the date to check if its around the time of upload being expected per month, and if it isnt close then dont run the full yaml







# THINK ABOUT MODULES
# THINK ABOUT CLASSES
# - get json response from api etc - legit that other function should just work too sick
#   - screw it just make this a class for the sake of reuseability too, and legit make the py file a name_cls.py bosh

