# -- author : ceefar --
# -- project : nhs etl 2023 --

# -- imports --
import time
import os
# -- internal imports --
from func_async_api import *


# -- main funcs --
async def main() -> None:
    """ mids, swest, london, ney """
    print(f"\n- - - - - - - - - -\n[ Running CICD Pipeline : Part 1 ]\n- - - - - - - - - -\n")
    mids_hospital_codes = ['RBK', 'RFS', 'RJC', 'RJE', 'RK5', 'RKB', 'RL1', 'RL4', 'RLQ', 'RLT', 'RNA', 'RNQ', 'RNS', 'RQ3', 'RRJ', 'RRK', 'RTG', 'RWD', 'RWE', 'RWP', 'RX1', 'RXK', 'RXW']
    london_hospital_codes = ["R1H", "R1K", "RAL", "RAN", "RAP", "RAS", "RAX", "RJ1", "RJ2", "RJ6", "RJ7", "RJZ", "RKE", "RP6", "RQM", "RQX", "RRV", "RVR", "RYJ", "RF4"]
    swest_hospital_codes = ["R0D", "RA4", "RA7", "RA9", "RBD", "RD1", "REF", "RH5", "RH8", "RK9", "RN3", "RNZ", "RTE", "RVJ"]
    ney_hospital_codes = ["R0B", "RAE", "RCB", "RCD", "RCF", "RFF", "RFR", "RHQ", "RJL", "RNN", "RR7", "RR8", "RTD", "RTF", "RTR", "RVW", "RWA", "RWY", "RXF", "RXP"]
    # --
    hospital_codes = []
    hospital_codes.extend(mids_hospital_codes)
    hospital_codes.extend(london_hospital_codes)
    hospital_codes.extend(swest_hospital_codes)
    hospital_codes.extend(ney_hospital_codes)
    # --
    webpage_data_list = await asyncio.gather(*[get_page_data(f"https://www.myplannedcare.nhs.uk/mpcjson/{code}.json") for code in set(hospital_codes)])
    hospital_data_list = await asyncio.gather(*[make_new_hospital_data_dict(hospital) for hospital in webpage_data_list])
    # -- 
    print(f"- - - - - - - - - -\n[ Inserting New Hospital Data : Part 1 ]\n- - - - - - - - - -\n")
    for hospital_data in hospital_data_list:
        add_first_wait_times_to_db_sync(hospital_data)
        add_avg_wait_times_to_db_sync(hospital_data)
    # -- end main --

async def main_extension() -> None:
    """ seast, nwest, east """
    print(f"\n- - - - - - - - - -\n[ Running CICD Pipeline : Part 2 ]\n- - - - - - - - - -\n")
    seast_hospital_codes = ['R1F', 'RDU', 'RHM', 'RHW', 'RN5', 'RN7', 'RPA', 'RPC', 'RTH', 'RTP', 'RVV', 'RWF', 'RXC', 'RXQ', 'RYR']
    nwest_hospital_codes = ['R0A', 'RBL', 'RBN', 'RBQ', 'RBS', 'RBT', 'REM', 'REP', 'RET', 'RJN', 'RJR', 'RM3', 'RMC', 'RMP', 'RRF', 'RTX', 'RVY', 'RWJ', 'RXL', 'RXN', 'RXR']
    east_hospital_codes = ['RAJ', 'RC9', 'RD8', 'RDE', 'RGM', 'RGN', 'RGP', 'RGR', 'RGT', 'RQW', 'RWG', 'RWH']
    # --
    hospital_codes = []
    hospital_codes.extend(seast_hospital_codes)
    hospital_codes.extend(nwest_hospital_codes)
    hospital_codes.extend(east_hospital_codes)
    # --
    webpage_data_list = await asyncio.gather(*[get_page_data(f"https://www.myplannedcare.nhs.uk/mpcjson/{code}.json") for code in set(hospital_codes)])
    hospital_data_list = await asyncio.gather(*[make_new_hospital_data_dict(hospital) for hospital in webpage_data_list])
    # -- 
    print(f"- - - - - - - - - -\n[ Inserting New Hospital Data : Part 2 ]\n- - - - - - - - - -\n")
    for hospital_data in hospital_data_list:
        add_first_wait_times_to_db_sync(hospital_data)
        add_avg_wait_times_to_db_sync(hospital_data)
    # -- end main part 2 --
    

# -- driver --    
if __name__ == "__main__": 
    # -- start timing, create tables (removed for now as not needed) --
    start_time = time.time()
    # create_base_first_apt_tables()

    # -- run cicd pipeline for part 1 or part 2 (different region groupings), use default parameter to run parts manually -- 
    task_type = os.environ.get('TASK_TYPE', default='part2')
    print(f"\n- - - - - - - - - -\n[ Loaded Env Var : TASK_TYPE = {task_type} ]\n- - - - - - - - - -")

    if task_type == "part1":
        asyncio.run(main()) 
        run_averages_stored_procedure()
    # -- seast, nwest, east --
    elif task_type == "part2":
        asyncio.run(main_extension()) 
        run_averages_stored_procedure(is_part_2=True)
    
    # -- log timing --
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n- - - - - - - - - -\n[ COMPLETE ]\n - Completed In {elapsed_time}s\n- - - - - - - - - -\n")


