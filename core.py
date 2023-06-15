# -- author : ceefar --
# -- project : nhs etl 2023 --


# -- imports --
import time
# -- internal imports --
from func_async_api import *


# -- main --
async def main() -> None:
    # --
    print(f"\n- - - - - - - - - -\n[ Running CICD Pipeline ]\n- - - - - - - - - -\n")
    start_time = time.time()
    # --
    hospital_codes = ['RBK', 'RFS', 'RJC', 'RJE', 'RK5', 'RKB', 'RL1', 'RL4', 'RLQ', 'RLT', 'RNA', 'RNQ', 'RNS', 'RQ3', 'RRJ', 'RRK', 'RTG', 'RWD', 'RWE', 'RX1', 'RXK', 'RXW']
    # --
    webpage_data_list = await asyncio.gather(*[get_page_data(f"https://www.myplannedcare.nhs.uk/mpcjson/{code}.json") for code in set(hospital_codes)])
    hospital_data_list = await asyncio.gather(*[make_new_hospital_data_dict(hospital) for hospital in webpage_data_list])
    # -- 
    print(f"- - - - - - - - - -\n[ Inserting New Hospital Data ]\n- - - - - - - - - -\n")
    for hospital_data in hospital_data_list:
        add_first_wait_times_to_db_sync(hospital_data)
    # --
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n- - - - - - - - - -\n[ COMPLETE ]\n - Completed In {elapsed_time}s\n- - - - - - - - - -\n")


# -- driver --    
if __name__ == "__main__": 
    create_base_first_apt_table()
    asyncio.run(main()) 




# MIDS NOT WORKING
# 'RWP'


# RENAME DB TABLE FROM FIRST_APT TO WAIT_TIMES PLEASE! 



# ADD NEW HOSPS
# GET WEBAPP ON CLOUD WITH NEW GPT CONCEPT
# START DOING NEW DB TABLE CICD AND HOOKING THAT UP TO THE WEB APP TOO (AND GPT FUNCTIONS TOO OOOOOOOOO)


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