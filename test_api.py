# -- imports --
from flask import Flask, jsonify, request
import os
import mysql.connector

# -- read the db cnx vars from env --
host = os.environ.get("mysql_host")
user = os.environ.get("mysql_user")
password = os.environ.get("mysql_password")
database = os.environ.get("mysql_db")
port = 3306

# -- create an instance of the Flask class --
app = Flask(__name__)

# -- func to establish mysql db cnx --
def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(user=user,
                                             password=password,
                                             host=host,
                                             database=database)
    except Exception as e:
        print(e)
    return connection

# -- create a route /api/data that fetches all rows from the first_apt table in the db and returns them as a JSON response --
@app.route('/api/all_data', methods=['GET'])
def get_data():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM first_apt;')
    rows = cursor.fetchall()
    # data = []
    # for row in rows:
    #     data.append({'id': row[0], 'field1': row[1], 'field2': row[2]}) 
    cursor.close()
    connection.close()
    return jsonify(rows)

@app.route('/api/trust_data', methods=['GET'])
def get_hospital_name_data():
    param = request.args.get('param')
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM first_apt WHERE hospital_name = %s;', (param,))
    print(f"PARAM = {param}")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(rows)

if __name__ == '__main__':
    app.run(debug=True, port=5000)


