# -- author : ceefar --
# -- project : nhs etl 2023 --

# -- imports --
import datetime
import streamlit as st
from mysql.connector import DatabaseError
# -- internal imports --
from cls_db import Database
from func_misc import st_page_load

# -- global db conn --
try:
    db = Database()
    # st_page_load() # -- set to wide here if we don't hit an error connecting to the db --
except DatabaseError as dbErr:
    # -- run the st page load here for the first time as it needs to be the first st function run, and we then display a warning st callout if we error so this needs to run first here which is absolutely fine as its the web app api stuff anyways --
    st_page_load()   
    print(f"DB Error! : {dbErr = }")
    st.warning(body="DB Connection Error! The Dev's Are On It. Please Try Again Later.")

# -- funcs : api --
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

def format_date(date):
    """ move me to misc module once ur 100% done with me plis """
    if date is None:
        formatted_date = "CURDATE()"
    else:
        formatted_date = f"'{date.strftime('%Y-%m-%d')}'"
    return formatted_date

def get_swest_daily_avg_first_apt(user_department, date):
    """ could convert this to just 1 function btw but for now is fine since we are talking 100s of hospitals per region, if refactoring obvs do this properly """
    formatted_date = format_date(date)
    query = f"SELECT avg_{user_department.lower().replace(' ', '_')} FROM `daily_department_averages_swest` WHERE DATE(date) = {formatted_date};"
    res = db.secure_get_from_db(query, None)
    print(f"FUNC get_swest_daily_avg_first_apt : swest {res = }")
    return res[0][0]

def get_ney_daily_avg_first_apt(user_department, date):
    formatted_date = format_date(date)
    query = f"SELECT avg_{user_department.lower().replace(' ', '_')} FROM `daily_department_averages_ney` WHERE DATE(date) = {formatted_date};"
    res = db.secure_get_from_db(query, None)
    print(f"FUNC get_ney_daily_avg_first_apt : ney {res = }")
    return res[0][0]

def get_london_daily_avg_first_apt(user_department, date):
    formatted_date = format_date(date)
    query = f"SELECT avg_{user_department.lower().replace(' ', '_')} FROM `daily_department_averages_london` WHERE DATE(date) = {formatted_date};"
    res = db.secure_get_from_db(query, None)
    print(f"FUNC get_london_daily_avg_first_apt : london {res = }")
    return res[0][0]

def get_mids_daily_avg_first_apt(user_department, date):
    formatted_date = format_date(date)
    query = f"SELECT avg_{user_department.lower().replace(' ', '_')} FROM `daily_department_averages_mids` WHERE DATE(date) = {formatted_date};"
    res = db.secure_get_from_db(query, None)
    print(f"FUNC get_mids_daily_avg_first_apt : mids {res = }")
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

def check_pulse():
    """ run test to see if we're returning data from the db """
    query = "SELECT * FROM first_apt"
    res = db.secure_get_from_db(query, None)
    if res:
        print(f"\n- - - - - - - - - -\n[ DB Status : ALIVE ]\n- - - - - - - - - -\n")
    else:
        print(f"\n- - - - - - - - - -\n[ DB Status : DED ]\n- - - - - - - - - -\n")

# -- delete dis? --
def get_db_accurate_hospital_names():
    query = "SELECT DISTINCT(hospital_name) FROM `first_apt`"
    res = db.secure_get_from_db(query, None)
    return res

def rank_hospitals(department, date):
    ranked_data = db.rank_hospitals(department, date)
    return ranked_data


# -- driver --
if __name__ == "__main__":
    check_pulse()
