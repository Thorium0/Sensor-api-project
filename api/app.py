import flask, json
from flask import request, jsonify
from datetime import datetime, timedelta
import db
from tools import *

app = flask.Flask(__name__)

api_url = "/api/v1/"


@app.route('/', methods=['GET'])
def home():
    to_time = datetime.now()
    from_time = to_time + timedelta(hours=-2)

    db.start_conn()
    sensor_data = db.get_sensor_data_for_controller("school-client", from_time, to_time)
    db.stop_conn()

    context = {
        "title": "Sensor overview",
        "sensor_data": sensor_data
    }
    return render("home.html", context)



@app.route(api_url+'test', methods=['GET'])
def api_all():
    db.upload_to_db("0.0.0.0", "T", 1.0)
    return jsonify({"success":True})


@app.route(api_url+'upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        if request.is_json:
            
            data = json.loads(request.data)
            print(data)

            db.start_conn()
            secret = data["secret"]
            if not db.check_secret(secret, "upload"):
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
