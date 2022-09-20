# Sensor-api-project
## Made by Troels Wittrup-Jensen

This is a project I made for monitoring tempature, humidity and air pressure using an m5go as client, and uploading the data to a raspberry pi 4 hosting a server.

It consists of 2 parts, the server(api) and client(Sensor).

# Setup
To set the server up download the "api" folder and install python 3.10 and the following command for the libraries:
pip install flask mariadb

Afterwards you can change the global variables in app.py to match your setup, and launch either "start-server.sh" or "start-server-debug.sh" if you would like automatic reload of the server on code-change.

To set the database up on the server download and install an sql service. I used mariadb which is an improved fork of mysql for archlinux. If you don't use arch I recommend using mysql, but it can have problems with utf8.
After installing an sql-service please import the "sensor_data.sql" file using pymyadmin or the command-line. 

To setup the client just download the "Sensor" folder and using platformio for vscode, simply upload the code to a m5go. Additional ECs will need to be added manually to the database.

# Features
## Client: 
* Monitors temperature, humidity and air pressure and displays it on it's display.
* Shows a countdown for the next time it will try to POST the sensor-data to the server using http.
* The middle button beneath the display can be pressed to manually trigger a POST for testing purposes.
* LED's are present above the display to indicate it's status:
<br>The leftmost LED shows WiFi-status (green for connected,  red for no connection).
<br>The LED in the middle shows status for connection to the server (green for connected,  red for no connection).
<br>The rightmost LED blinks blue whenever it receives status status-code 200 from a POST-request it sent. 

## Server
* Recieves data from clients at "http://[server-ip]:5000/api/v1/upload", and returns appropriate response codes.
* Uses a normalised database for optimal data-storage space.
* Only creates one connection the the database for each post request, and doesn't close it until the transaction is complete to ensure maximal performance.
* Only proceeds with data recieves the POST-request contains a secret-key matched to one saved in the secrets table in the database.
* Shows graphs of the sensors on "http://[server-ip]:5000/[controller-codename]" for the last two hours (can be configured in app.py).
