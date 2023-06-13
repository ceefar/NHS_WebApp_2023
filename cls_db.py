
# ---- imports ----
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# -- initial db cnx setup - load db vars from .env --
load_dotenv()
host = os.environ.get("host")
user = os.environ.get("user")
password = os.environ.get("password")
database = os.environ.get("database")
port = os.environ.get("port")


# -- classes --
class Database:
    """ base DB for making new connection and database interactions """

    def __init__(self) -> None:
        """ 
        //desc : db class constructor, initialise the connection and make it global so it can be accessed by extentions of this class
        //params : self
        //returns : None
        """
        global conn
        conn = self.init_connection()

    def init_connection(self) -> mysql.connector.connection_cext.CMySQLConnection:
        """
        //desc : leading underscore is necessary on the self parameter to ensure the connection isn't hashed by the singleton decorator but still cached
        //params : _self 
        //returns : the connection object
        """
        cnx = mysql.connector.connect(host=host, database=database, user=user, password=password, port=port)
        return(cnx)

    def refresh_connection(self) -> mysql.connector.connection_cext.CMySQLConnection:
        """
        //desc : reset to the global connection object, and then return it 
        //params : _self 
        //returns : the connection object
        """
        global conn
        cnx = mysql.connector.connect(host=host, database=database, user=user, password=password, port=port)
        conn = cnx
        return(cnx)

    def secure_add_to_db(self, query:str, parameters:tuple|None = None) -> int | None:
        """
        //desc : uses prepared statements/paramaterised queries,
                    prepared statements compile before inputs are added so the statement is only valid if the parameterised parts have changed, 
                    if there is a connection error, the cnx is restarted and the function is called recursively to commit the query again
        //params : self, query (as string), 
                    parameters to add to the query statement (as tuple) or None - defaults to None as we don't always need to send params
        //returns : the id of the last row that was inserted (as int), or None in the event of an error
        """
        with conn.cursor() as cur:
            # run the query with paramters added after compilation to prevent sql injection 
            cur.execute(query, parameters)
            # commit it to the database
            conn.commit()
            # return the last row id when adding something to the db
            return(cur.lastrowid)

    def secure_get_from_db(self, query:str, parameters:tuple|None = None, want_dict:bool = False):
        """ 
        //desc : write
        //params : me
        //returns : plis
        """  
        if want_dict:     
            with conn.cursor(dictionary=True) as cur: 
                cur.execute(query, parameters)
                result = cur.fetchall()
                return(result) 
        else:
            with conn.cursor() as cur: 
                cur.execute(query, parameters)
                result = cur.fetchall()
                return(result) 
        
    def wrap_up_db(self):
        """ close the connection, no need to close the cursor as its open with a context manager (so will close itself) """
        print("[ Closing DB Connection ]\n")
        conn.close()

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


