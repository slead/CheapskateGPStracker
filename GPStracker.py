import sys
import time as t
from pyicloud import PyiCloudService
import datetime as dt
import csv
import os
from math import radians, sin, cos, sqrt, atan2
import json

file_path = "/Users/steve/Dropbox/shitbox rally/tracking/tracks.csv"

def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Calculate the change in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula to calculate distance
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in meters
    distance = R * c * 1000

    return distance


def tracker(iphone, prev_longitude, prev_latitude, firstRun:bool):
    
    try:
        if is_daylight_hours():
            current_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            location = iphone.location()
            timestamp = location['timeStamp'] #datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            latitude = location['latitude']
            longitude = location['longitude']

            if prev_latitude == 0:
                prev_latitude = latitude
            if prev_longitude == 0:
                prev_longitude = longitude

            # check whether the position has moved enough to track
            distance_threshold = 1  # metres
            if firstRun or calculate_distance(prev_latitude, prev_longitude, latitude, longitude) >= distance_threshold:
                prev_longitude = longitude
                prev_latitude = latitude
                data = [current_time,timestamp, latitude, longitude]
                print(data)

                # write to file
                with open(file_path, 'a', newline='\n') as csvfile:
                    # Create a CSV writer object
                    csv_writer = csv.writer(csvfile)
                
                    # Append the data to the CSV file
                    csv_writer.writerow(data)
                
                # Sleep then run again
                t.sleep(600)
                tracker(iphone, prev_longitude, prev_latitude, False)
            else:
                print("Point has not moved by more than 50 meters.")
                t.sleep(600)
                tracker(iphone, prev_longitude, prev_latitude, False)

        else: 
            t.sleep(600)
    except Exception as e:
        print("There was a problem, trying again in 30 seconds")
        print(e.args)
        t.sleep(30)
        tracker(iphone, prev_longitude, prev_latitude, False)

def is_daylight_hours():
    return True

    # Get the current local time
    current_time = dt.datetime.now().time()

    # Define the time boundaries (8am and 6pm)
    start_time = dt.time(6, 0, 0)   # 6:00:00 AM
    end_time = dt.time(20, 0, 0)    # 8:00:00 PM

    # Check if the current time is between the start and end time
    return start_time <= current_time <= end_time

# Read from config.json
with open('config.json', 'r') as file:
    config = json.load(file)
    email = config['email']
    password = config['password']

api = PyiCloudService(email, password)

if api.requires_2fa:
    print("Two-factor authentication required.")
    code = input("Enter the code you received of one of your approved devices: ")
    result = api.validate_2fa_code(code)
    print("Code validation result: %s" % result)

    if not result:
        print("Failed to verify security code")
        sys.exit(1)

    if not api.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result = api.trust_session()
        print("Session trust result %s" % result)

        if not result:
            print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
elif api.requires_2sa:
    import click
    print("Two-step authentication required. Your trusted devices are:")

    devices = api.trusted_devices
    for i, device in enumerate(devices):
        print(
            "  %s: %s" % (i, device.get('deviceName',
            "SMS to %s" % device.get('phoneNumber')))
        )

    device = click.prompt('Which device would you like to use?', default=0)
    device = devices[device]
    if not api.send_verification_code(device):
        print("Failed to send verification code")
        sys.exit(1)

    code = click.prompt('Please enter validation code')
    if not api.validate_verification_code(device, code):
        print("Failed to verify verification code")
        sys.exit(1)

if not os.path.isfile(file_path):
    with open(file_path, 'w', newline='\n') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['CurrentTime', 'Timestamp', 'Latitude', 'Longitude'])
iphone = api.devices[1]

# keep track of the last known position
prev_latitude = 0
prev_longitude = 0

tracker(iphone, prev_longitude, prev_latitude, True)
        