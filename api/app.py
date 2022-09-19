import flask, json
from flask import request, jsonify
from datetime import datetime, timedelta
import db
from tools import *

app = flask.Flask(__name__)

api_url = "/api/v1/"

# Show Graphs
@app.route('/<controller>', methods=['GET'])
def home(controller):
    to_time = datetime.now()
    from_time = to_time + timedelta(hours=-2)

    db.start_conn()
    sensor_data = db.get_sensor_data_for_controller(controller, from_time, to_time)
    db.stop_conn()

    context = {
        "title": "Sensor overview",
        "sensor_data": sensor_data
    }
    return render("home.html", context)

# Revives POST-requests and inserts it into the database
@app.route(api_url+'upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        if request.is_json:
            
            data = json.loads(request.data)
            print(data)

            db.start_conn()
            secret = data["secret"]
            if not db.check_secret(secret, "upload"): # Makes sure the secret-key is correct before proceeding
                return jsonify({"success":False, "msg": "Secret is incorrect"})
            

            controller_codename = data["controller_codename"]
            for key, value in data["data"].items():
                sensor_type = key
                status = db.upload_to_db(controller_codename, sensor_type, value)

            db.stop_conn()
            return jsonify({"success":status})
        
    return jsonify({"success":False, "msg": "POST data invalid"})


if __name__ == "__main__":
    app.run()
