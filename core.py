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
    
    # --
    mids_hospital_codes = ['RBK', 'RFS', 'RJC', 'RJE', 'RK5', 'RKB', 'RL1', 'RL4', 'RLQ', 'RLT', 'RNA', 'RNQ', 'RNS', 'RQ3', 'RRJ', 'RRK', 'RTG', 'RWD', 'RWE', 'RWP', 'RX1', 'RXK', 'RXW']
    london_hospital_codes = ["R1H", "R1K", "RAL", "RAN", "RAP", "RAS", "RAX", "RJ1", "RJ2", "RJ6", "RJ7", "RJZ", "RKE", "RP6", "RQM", "RQX", "RRV", "RVR", "RYJ", "RF4"]
    swest_hospital_codes = ["R0D", "RA4", "RA7", "RA9", "RBD", "RD1", "REF", "RH5", "RH8", "RK9", "RN3", "RNZ", "RTE", "RVJ"]
    ney_hospital_codes = ["R0B", "RAE", "RCB", "RCD", "RCF", "RFF", "RFR", "RHQ", "RJL", "RNN", "RR7", "RR8", "RTD", "RTF", "RTR", "RVW", "RWA", "RWY", "RXF", "RXP"]
    # -- new regions --
    seast_hospital_codes = ['R1F', 'RDU', 'RHM', 'RHW', 'RN5', 'RN7', 'RPA', 'RPC', 'RTH', 'RTP', 'RVV', 'RWF', 'RXC', 'RXQ', 'RYR']
    nwest_hospital_codes = ['R0A', 'RBL', 'RBN', 'RBQ', 'RBS', 'RBT', 'REM', 'REP', 'RET', 'RJN', 'RJR', 'RM3', 'RMC', 'RMP', 'RRF', 'RTX', 'RVY', 'RWJ', 'RXL', 'RXN', 'RXR']
    east_hospital_codes = ['RAJ', 'RC9', 'RD8', 'RDE', 'RGM', 'RGN', 'RGP', 'RGR', 'RGT', 'RQW', 'RWG', 'RWH']
    # -- end new regions --
    hospital_codes = []
    hospital_codes.extend(mids_hospital_codes)
    hospital_codes.extend(london_hospital_codes)
    hospital_codes.extend(swest_hospital_codes)
    hospital_codes.extend(ney_hospital_codes)
    # -- group codes for new regions seperately --
    hospital_codes_part_2 = []
    hospital_codes_part_2.extend(seast_hospital_codes)
    hospital_codes_part_2.extend(nwest_hospital_codes)
    hospital_codes_part_2.extend(east_hospital_codes)
    # -- end seperate new regions --
    # --
    webpage_data_list = await asyncio.gather(*[get_page_data(f"https://www.myplannedcare.nhs.uk/mpcjson/{code}.json") for code in set(hospital_codes)])
    hospital_data_list = await asyncio.gather(*[make_new_hospital_data_dict(hospital) for hospital in webpage_data_list])
    # -- 
    print(f"- - - - - - - - - -\n[ Inserting New Hospital Data ]\n- - - - - - - - - -\n")
    for hospital_data in hospital_data_list:
        add_first_wait_times_to_db_sync(hospital_data)
        add_avg_wait_times_to_db_sync(hospital_data)
    # --
    


# -- driver --    
if __name__ == "__main__": 
    # --
    start_time = time.time()
    # --
    # create_base_first_apt_tables()
    asyncio.run(main()) 
    run_averages_stored_procedure()
    # --
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n- - - - - - - - - -\n[ COMPLETE ]\n - Completed In {elapsed_time}s\n- - - - - - - - - -\n")



# TOD0!
# -----
# DISPLAY SWEST AND NEY AVGS IN PROPER METRIC COL DISPLAY
# NEW CACHED API CODE FOR FASTEST AND SLOWEST IN THE COUNTRY TING TOO (USING SQL OBVS)
# POSTCODE AND MAPS STUFF
# CHOOSE BY DAY
# DEL ALL DATA AND SEE IF CICD STILL WORKS
# ON CLOUD



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