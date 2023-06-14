# project : nhs etl 
# author : ceefar

# -- imports --
import requests
import json
import codecs 
from func_misc import *

 
# -- funcs : get json response from api -- 
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

