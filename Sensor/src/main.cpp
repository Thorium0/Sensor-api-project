#include <M5Stack.h>
#include "M5_ENV.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_NeoPixel.h>
#include <AsyncTimer.h>

#define LED_PIN 26
#define NUMPIXELS 3

SHT3X sht30;
QMP6988 qmp6988;
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(
	NUMPIXELS, LED_PIN,
	NEO_GRB + NEO_KHZ800
);

String controller_codename = "rasp-client-1";
String secret = "HdQJEaxDn0WBBFfhh7hoUiXyPw5ZyLbz5PGp9plbb4lIwPe7nQ";
String url = "http://192.168.1.125:5000/api/v1/upload";

const char *ssid = "small-network";
const char *password = "kagemand123";

float tmp = 0.0;
float hum = 0.0;
float pressure = 0.0;

unsigned long postDelay = 1000 * 60 * 5 ;
unsigned long sensorDelay = 1000;
int delayCounter = postDelay - 1000;

AsyncTimer startupTimeout;
AsyncTimer postLoop;
AsyncTimer sensorLoop;

const int buttonPin = 38; 
int buttonState = 0;


void postSensorData() {
	delayCounter = postDelay - 1000;
	if (WiFi.isConnected()) {
			HTTPClient http;
			http.begin(url.c_str());
			http.addHeader("Content-Type", "application/json");
			String json = "{\"secret\":\""+secret+"\", \"controller_codename\": \""+controller_codename+"\", \"data\": {\"T\":"+tmp+", \"H\":"+hum+", \"P\":"+pressure+"}}";
			int respCode = http.POST(json);

			if (respCode == 200) {
				pixels.setPixelColor(1, pixels.Color(0, 100, 0)); // Green
				pixels.setPixelColor(2, pixels.Color(0, 0, 100)); // Blue
				pixels.show();
				delay(100);
				pixels.setPixelColor(2, pixels.Color(0, 0, 0)); // Off
				pixels.show();
			} else {
				pixels.setPixelColor(1, pixels.Color(100, 0, 0)); // Red
				pixels.show();
			}
			
			http.end();
		}
}

void getSensorData() {
	pressure = qmp6988.calcPressure();
	if (sht30.get() == 0) {
		tmp = sht30.cTemp;

		hum = sht30.humidity;
	} else {
		tmp = 0, hum = 0;
	}
	M5.lcd.fillRect(0, 20, 100, 60, BLACK);

	M5.lcd.setCursor(0, 0);
	if (WiFi.isConnected()) {
		pixels.setPixelColor(0, pixels.Color(0, 100, 0)); // Green
	} else {
		pixels.setPixelColor(0, pixels.Color(100, 0, 0)); // Red
	}
	pixels.show();
	int minutes = (delayCounter / 1000) / 60;
	int seconds = (delayCounter / 1000) % 60;
	M5.Lcd.printf("Temp: %2.1f  \r\nHumi: %2.0f%%  \r\nPressure:%2.0fPa  \r\nPOST in: %1iM %2iS\r\n", tmp, hum, pressure, minutes, seconds);
	delayCounter -= 1000;
}

void startup() {
	getSensorData();
	postSensorData();
}

void setup() {
	M5.begin();
	M5.Power.begin();
	M5.lcd.setTextSize(2);
	Serial.begin(115200); 
	WiFi.begin(ssid, password);
	pixels.begin();
	qmp6988.init();

	pinMode(buttonPin, INPUT);

	startupTimeout.setTimeout(startup, 3000);

	sensorLoop.setInterval(getSensorData, sensorDelay);
	postLoop.setInterval(postSensorData, postDelay);
}

void loop() {
	startupTimeout.handle();
	sensorLoop.handle();
	postLoop.handle();
	if (digitalRead(buttonPin) == LOW && buttonState==0) {
		buttonState = 1;
		getSensorData();
		postSensorData();
	} else if (digitalRead(buttonPin) == HIGH) {
		buttonState = 0;
	}
}
