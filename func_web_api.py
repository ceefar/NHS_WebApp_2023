# -- author : ceefar --
# -- project : nhs etl 2023 --

# -- imports --
import datetime
# -- internal imports --
from cls_db import Database

# -- global db conn --
db = Database()

# -- funcs : faux api --
def check_pulse():
    """ literally just a test to see if we're returning data from the db """
    query = "SELECT * FROM first_apt"
    res = db.secure_get_from_db(query, None)
    if res:
        print(f"\n- - - - - - - - - -\n[ DB Status : ALIVE ]\n- - - - - - - - - -\n")
    else:
        print(f"\n- - - - - - - - - -\n[ DB Status : DED ]\n- - - - - - - - - -\n")
    # print(f"{res = }")

def get_trust_curr_first_apt_for_a_department(user_department, user_trust):
    query = f"SELECT hospital_name, `{user_department}` FROM first_apt \
                WHERE hospital_name = '{user_trust}' AND DATE(created_on) = CURDATE();"
    res = db.secure_get_from_db(query, None)
    return res

def get_trust_curr_avg_wait_time_for_a_department(user_department, user_trust):
    query = f"SELECT hospital_name, `{user_department}` FROM avg_wait \
                WHERE hospital_name = '{user_trust}' AND DATE(created_on) = CURDATE();"
    res = db.secure_get_from_db(query, None)
    return res

def get_london_daily_avg_first_apt(user_department):
    query = f"SELECT avg_{user_department.lower().replace(' ', '_')} FROM `daily_department_averages_london` WHERE DATE(date) = CURDATE();"
    res = db.secure_get_from_db(query, None)
    return res[0][0]

def get_mids_daily_avg_first_apt(user_department):
    # PASS IN A DATE THING REMEMBER!!!! < [ TODO ]
    query = f"SELECT avg_{user_department.lower().replace(' ', '_')} FROM `daily_department_averages_mids` WHERE DATE(date) = CURDATE();"
    res = db.secure_get_from_db(query, None)
    return res[0][0]

def get_min_max_first_apt_wait_for_department_and_region(user_department, user_region):
    query = f"SELECT (SELECT hospital_name FROM first_apt WHERE hospital_region = '{user_region}' ORDER BY `{user_department}` ASC LIMIT 1) AS hospital_min_wait, (SELECT MIN(`{user_department}`) FROM first_apt WHERE hospital_region = '{user_region}') AS min_{user_department.lower().replace(' ','_')}_wait_time, (SELECT hospital_name FROM first_apt WHERE hospital_region = '{user_region}' ORDER BY `{user_department}` DESC LIMIT 1) AS hospital_max_wait, (SELECT MAX(`{user_department}`) FROM first_apt WHERE hospital_region = '{user_region}') AS max_{user_department.lower().replace(' ','_')}_wait_time;"
    res = db.secure_get_from_db(query, None)
    return res

def get_min_max_first_apt_wait_for_department_countrywide(user_department):    
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")
    print(f"{formatted_date = }")
    query = f"SELECT hospital_name, hospital_region, `{user_department}` AS wait_time FROM avg_wait WHERE DATE(created_on) = '{formatted_date}' AND `{user_department}` IN (SELECT MIN(`{user_department}`) FROM avg_wait WHERE DATE(created_on) = '{formatted_date}' UNION SELECT MAX(`{user_department}`) FROM avg_wait WHERE DATE(created_on) = '{formatted_date}');"
    res = db.secure_get_from_db(query, None)
    return res

# -- leave this for now but will delete and hardcode once db and cicd pipeline is completed --
def get_db_accurate_hospital_names():
    """ am 100% guna hardcode this but ideally would add some additional check that would check db names and hardcoded names match each day, if not inform me (via failed action), could even be a every other day kinda thing too """
    query = "SELECT DISTINCT(hospital_name) FROM `first_apt`"
    res = db.secure_get_from_db(query, None)
    return res


# -- driver --
if __name__ == "__main__":
    check_pulse()


# add this to notes, query for getting all hosp codes from a region from old db
# "SELECT hospital_code FROM nhs_hosp_codes WHERE hospital_name IN (SELECT hospital_name FROM first_apt WHERE hospital_region = 'swest');"
