# -- documentation -- 
# -- author : ceefar --
# -- project : nhs wait times api x web app --

# -- imports --
from flask import Flask, jsonify, request
import os
import mysql.connector


# -- read the db cnx vars from env --
host = os.environ.get("mysql_host")
user = os.environ.get("mysql_user")
password = os.environ.get("mysql_password")
database = os.environ.get("mysql_db")
port = int(os.environ.get("PORT", 5000)) # 3306

# -- create an instance of the Flask class --
app = Flask(__name__)

# -- func to establish mysql db cnx --
def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(user=user, password=password, host=host, database=database)
    except Exception as e:
        print(e)
    return connection

# -- api routes --
@app.route('/api/get_first_apt_wait_times', methods=['GET'])
def get_first_apt_wait_times():
    """ create a route /api/get_first_apt_wait_times that fetches wait times from first_apt table for a given dept and trust and returns the data as a JSON response """
    hospital_name = request.args.get('hospital')
    department = request.args.get('department')
    # -- make db cnx --
    connection = get_db_connection()
    cursor = connection.cursor()
    # -- construct the SQL query --
    query = 'SELECT {}, created_on FROM first_apt WHERE hospital_name = %s;'.format(department)
    cursor.execute(query, (hospital_name,))
    # -- get and clean the db response --
    rows = cursor.fetchall()
    data = []
    for row in rows: # print(f"{row = }")
        data.append({'dept': department, 'trust': hospital_name, 'wait_time': row[0], 'date': row[1]}) 
    # -- close db cnx and cursor, then return the cleaned db data --
    cursor.close()
    connection.close()
    return jsonify(data)

@app.route('/api/all_trusts', methods=['GET'])
def get_all_trust_names_data():
    """ create a route /api/all_trusts that fetches all unique trust names from the first_apt table in the db and returns them as a JSON response, with optional region arg """
    region = request.args.get('region')
    connection = get_db_connection()
    cursor = connection.cursor()
    # -- switch to get only hospitals for a given region if region is given --
    if region:
        cursor.execute('SELECT DISTINCT(hospital_name) FROM first_apt WHERE hospital_region = %s;', (region,))
    else:
        cursor.execute('SELECT DISTINCT(hospital_name) FROM first_apt;')
    # -- clean response --
    rows = cursor.fetchall()
    data = []
    for row in rows:
        data.append({'hospital_name': row[0]}) 
    # -- close and return --
    cursor.close()
    connection.close()
    return jsonify(data)

@app.route('/api/data', methods=['GET'])
def get_data():
    """ create a default test route /api/all_data that fetches all rows from the first_apt table in the db and returns them raw """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM first_apt;')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(rows)


# -- driver --
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)



# QUICKLY DO
# - API CALL TO GET THE HOSPITAL LISTS THING AND USE THIS TO POPULATE THE HOSPITAL TRUST NAMES, OBVS THEN CACHE IT THO
#   - duhhhhhh no, what you actually do is get all the hospital names in a list at the start in a dict and cache that!
# - THEN LEGIT MAKE THE API LIVE TO TEST
#   - REMEMBER WE ARE USING CONDA THO!
# - DO PROPER ERROR HANDLING AND UNIT TESTING FROM THE START

# ASK GPT
# - how to handle errors!
# - how to host, any associated costs (i think still do this via aws yanno but maybe not initially)
