#!/usr/bin/env python
# LDF_Breathing_Space Dispatcher
# Ben Hussey <ben.hussey@arup.com> - September 2017
# Run from crontab every minute

import requests
from datetime import datetime, timedelta, time
from config import ESP_IPS, LOCATIONS


class Point():
    pm_value = None
    updated = datetime.now() - timedelta(seconds=90)

    def __init__(self, location):
        self.location = location

    def tick(self):
        now = datetime.now().time()
        if now >= time(6, 00) and now <= time(22, 00):
            if self.updated < datetime.now() - timedelta(seconds=90):
                self.value = self.get_api_value()
                # print(
                #    "%s: %s" % (LOCATIONS[self.location]['name'], self.value))
                self.updated = datetime.now()
            if self.value:
                self.set_leds()
        else:
            self.set_leds("black")

    def get_api_value(self):
        url = ("http://api.erg.kcl.ac.uk/"
               "AirQuality/Data/Nowcast/lat=%s/lon=%s/Json" %
               (LOCATIONS[self.location]['lat'],
                LOCATIONS[self.location]['long']))
        try:
            r = requests.get(url, timeout=1)
            out = r.json()
            print(out)
            return float(out['PointResult']['@NO2'])
        except Exception as e:
            print("Error getting data from API")
            print(e)
            return None

    def set_leds(self, state=None):
        if state:
            state = state
        elif self.value > 200:
            state = "pink"
        elif self.value > 125:
            state = "red"
        elif self.value > 50:
            state = "yellow"
        else:
            state = "green"

        try:
            url = "http://%s/%s" % (ESP_IPS[self.location], state)
            # print(url)
            r = requests.get(url, timeout=1)
            if r.status_code == requests.codes.ok:
                return True
        except Exception as e:
            print("Error sending colour to ESP")
            print(e)


for pk in LOCATIONS:
    Point(pk).tick()
