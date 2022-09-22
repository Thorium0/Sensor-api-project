from mariadb import connect, Error

# Credentials for the database
host="localhost"
user="root"
password="enter-password-here"
database="sensor_data"
db = None

# Create connection to the database
def start_conn():
    global db
    try:
        db = connect(host=host, user=user, password=password, database=database)
    except Error as ex:
        print(f"An error occurred while connecting to MariaDB: {ex}")

# Close connection to the database
def stop_conn():
    global db
    db.close()

    
# gets the selector from the connection
def get_conn():
    return db.cursor()

# Compares give secret-key to the one in the database
def check_secret(secret, keyname):
    conn = get_conn()
    sql = "SELECT secret FROM secrets WHERE keyname = ?"

    conn.execute(sql, (keyname,))
    data = conn.fetchone()[0]
    conn.close()
    return secret==data


# Gets sensor_id based on controller, and sensor-type
def get_sensor_id(controller_codename, sensor_type):
    conn = get_conn()
    
    sql = """SELECT s.id FROM sensors AS s 
        LEFT JOIN sensor_types AS st ON s.sensor_type_id=st.id
        LEFT JOIN controllers AS c ON s.controller_id=c.id
        WHERE c.codename = ? AND st.type = ? """

    conn.execute(sql, (controller_codename, sensor_type))
    data = conn.fetchone()
    conn.close()
    if data != None:
        return data[0]


# Gets data from sensor within given timeframe
def get_sensor_data(sensor_id, from_time, to_time):
    conn = get_conn()
    sql = "SELECT value, datetime FROM logs WHERE sensor_id=? AND datetime>? AND datetime<?"

    conn.execute(sql, (sensor_id, from_time, to_time))
    data = []
    for value in conn:
        data.append(value)
    conn.close()
    return data


# High-level function to quickly pull out all data for a specific controller
def get_sensor_data_for_controller(controller_codename, from_time, to_time):
    types = ["T", "H", "P"]
    sensor_data = {"T": [], "H": [], "P": []}
    for type in types:
        sensor_id = get_sensor_id(controller_codename, type)
        sensor_data[type].extend(get_sensor_data(sensor_id, from_time, to_time))
    return sensor_data
    
    
    
# Inserts sensor-data into the database
def upload_to_db(controller_codename, sensor_type, value):
    sensor_id = get_sensor_id(controller_codename, sensor_type)
    conn = get_conn()
    sql = "INSERT INTO logs (value, sensor_id) VALUES (?, ?)"
    try:
        conn.execute(sql, (value, sensor_id))
        db.commit()
    except:
        status = False
    else:
        status = True
    conn.close()
    return status
    
    
