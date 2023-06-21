
# -- author : ceefar --
# -- project : nhs etl 2023 --

# -- imports --
import os
import mysql.connector
import streamlit as st
# -- unused imports --
from mysql.connector import Error
from dotenv import load_dotenv

# -- initial db cnx setup -- 
host = os.environ.get("mysql_host")
user = os.environ.get("mysql_user")
password = os.environ.get("mysql_password")
database = os.environ.get("mysql_db")
port = 3306
# -- if not load from env (which works locally and for github actions), then use streamlit secrets (as will be web app) 
if not host:
    host = st.secrets["MYSQL_HOST"]
    user = st.secrets["MYSQL_USER"]
    password = st.secrets["MYSQL_PASSWORD"]
    database = st.secrets["MYSQL_DB"]
    port = 3306

# -- purely for logging --
def check_load_from_env():
    print(f"\n- - - - - - - - - -\n[ Running Initial Setup ]\n- - - - - - - - - -\n")
    if host:
        print("Loaded Host from Env")
    if user:
        print("Loaded User from Env")
    if password:
        print("Loaded PW from Env")
    if database:
        print("Loaded DB from Env")
    if port:
        print("Loaded Port from Env")
    print(f"\n- - - - - - - - - -\n[ Initial Setup Complete ]\n- - - - - - - - - -")
check_load_from_env()


# -- DB Class --
class Database:
    """ base DB for making new connection and database interactions """

    def __init__(self) -> None:
        """ initialise the connection and make it global so it can be accessed by extentions of this class, now uses cached version not old init cnx funct """
        global conn
        conn = self.get_database_connection()
        if conn.is_connected():
            print(f"Yas")
        else:
            print(f"Nay")

    @st.cache_resource
    def get_database_connection(_self):
        """ leading underscore is necessary on the self parameter to ensure the connection isn't hashed by the singleton decorator but still cached """
        cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
        print(f"{cnx = }")
        return cnx

    def secure_add_to_db(self, query:str, parameters:tuple|None = None) -> int | None:
        """ prepared statements compile before inputs are added so the statement is only valid if the parameterised parts have changed """
        with conn.cursor() as cur: 
            cur.execute(query, parameters) # run the query with paramters added after compilation to prevent sql injection 
            conn.commit() # commit it to the database
            return cur.lastrowid # return the last row id when adding something to the db

    def secure_get_from_db(self, query:str, parameters:tuple|None = None, want_dict:bool = False):
        if want_dict:     
            with conn.cursor(dictionary=True) as cur: 
                cur.execute(query, parameters)
                result = cur.fetchall()
                return result 
        else:
            with conn.cursor() as cur: 
                cur.execute(query, parameters)
                result = cur.fetchall()
                return result 
            

    # -- new in dev alpha/test stuff --
    def rank_hospitals(self, department, date:str):
        """ requires date as string in fortmat : `2023-06-20`, note multi cursor & dict return """
        cursor = conn.cursor(dictionary=True) # -- use dict return -- 
        cursor.execute(f"SET @dept = '{department}';") # -- set the @dept and @date variables --
        cursor.execute(f"SET @date = '{date}';")
        # -- execute the main query --
        cursor.execute(f"""
            SELECT 
                hospital_name,
                `{department}` as wait_time,
                @rank := @rank + 1 as ranking
            FROM 
                first_apt, (SELECT @rank := 0) r
            WHERE 
                `{department}` IS NOT NULL
                AND DATE(created_on) = @date
            ORDER BY 
                wait_time ASC;
        """)
        # -- fetch and return result --
        result = cursor.fetchall()
        return result
    
    def check_existing_entry(self, hospital_name, date, table_name):
        """ checks for existing entry in database """
        # -- SQL query to check for existing entry with the same hospital name and date --
        sql_check = "SELECT * FROM {} WHERE hospital_name = %s AND DATE(created_on) = %s".format(table_name)
        params = (hospital_name, date)
        try:
            with conn.cursor() as cur: 
                # -- execute the SQL query --
                cur.execute(sql_check, params)
                # -- fetch one record and return result --
                result = cur.fetchone()
                # --
                if result != None:
                    return False
                else:
                    return True
        # --
        except mysql.connector.errors.InternalError:
            return False
        

    # -- old x unused : will likely bring back refresh cnx at some point tho for err handling --
    def init_connection(self):
        """ old now cnx without cached singleton """
        cnx = mysql.connector.connect(host=host, database=database, user=user, password=password, port=port) # charset='utf8',
        return cnx

    def refresh_connection(self):
        """ old now unused reset, likely worth still implementing tbf for error handling """
        global conn
        cnx = mysql.connector.connect(host=host, database=database, user=user, password=password, port=port)
        conn = cnx
        return cnx


       