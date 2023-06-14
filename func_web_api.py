# -- author : ceefar --
# -- project : nhs etl 2023 --

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

def get_db_accurate_hospital_names():
    """ am 100% guna hardcode this but ideally would add some additional check that would check db names and hardcoded names match each day, if not inform me (via failed action), could even be a every other day kinda thing too """
    query = "SELECT DISTINCT(hospital_name) FROM `first_apt`"
    res = db.secure_get_from_db(query, None)
    return res


# -- driver --
if __name__ == "__main__":
    check_pulse()

