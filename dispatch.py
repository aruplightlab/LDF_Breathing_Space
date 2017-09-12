#!/usr/bin/env python
# LDF_Breathing_Space Dispatcher
# Ben Hussey <ben.hussey@arup.com> - September 2017
# Run from crontab every minute

import requests
from datetime import datetime, timedelta
from config import ESP_IPS, LOCATIONS


class Point():
    pm_value = None
    updated = datetime.now() - timedelta(seconds=90)

    def __init__(self, location):
        self.location = location

    def tick(self):
        if self.updated < datetime.now() - timedelta(seconds=90):
            self.value = self.get_api_value()
            # print("%s: %s" % (LOCATIONS[self.location]['name'], self.value))
            self.updated = datetime.now()
        if self.value:
            self.set_colour()

    def get_api_value(self):
        url = ("http://api.erg.kcl.ac.uk/"
               "AirQuality/Data/Nowcast/lat=%s/lon=%s/Json" %
               (LOCATIONS[self.location]['lat'],
                LOCATIONS[self.location]['long']))
        try:
            r = requests.get(url, timeout=1)
            out = r.json()
            return float(out['PointResult']['@PM10'])
        except Exception as e:
            print("Error getting data from API")
            print(e)
            return None

    def set_colour(self):
        if self.pm_value > 100:
            colour = "pink"
        elif self.pm_value > 75:
            colour = "red"
        elif self.pm_value > 50:
            colour = "yellow"
        else:
            colour = "green"

        try:
            url = "http://%s/%s" % (ESP_IPS[self.location], colour)
            r = requests.get(url, timeout=1)
            if r.status_code == requests.codes.ok:
                return True
        except Exception as e:
            print("Error sending colour to ESP")
            print(e)


for pk in LOCATIONS:
    Point(pk).tick()
