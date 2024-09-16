import os
import time
from datetime import datetime, timedelta
from dateutil import parser 
import pytz
import RPi.GPIO as GPIO
import config
import msal
import requests

# Set the local timezone
local_tz = pytz.timezone("America/Los_Angeles")

MAX_RUNTIME_HOURS = 8  # Change this value to adjust the script's runtime

# Track the start time of the script
script_start_time = datetime.now(local_tz)

# Set up GPIO pins for LEDs
GPIO.setmode(GPIO.BCM)
YELLOW_PIN = 17  # Blinks 15 minutes before
ORANGE_PIN = 27  # Stays on 5 minutes before
RED_PIN = 22     # Stays on during the meeting

# Set up GPIO pins
GPIO.setup(YELLOW_PIN, GPIO.OUT)
GPIO.setup(ORANGE_PIN, GPIO.OUT)
GPIO.setup(RED_PIN, GPIO.OUT)

def flash_led(pin, duration):
    """Flash the specified LED pin for the given duration (in seconds)."""
    end_time = time.time() + duration
    while time.time() < end_time:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.5)

def turn_on_led(pin):
    """Turn on the specified LED pin."""
    GPIO.output(pin, GPIO.HIGH)

def turn_off_led(pin):
    """Turn off the specified LED pin."""
    GPIO.output(pin, GPIO.LOW)

# Ensure that all LEDs are turned off when the script starts
turn_off_led(YELLOW_PIN)
turn_off_led(ORANGE_PIN)
turn_off_led(RED_PIN)

# Fetch today's meetings from Microsoft Graph API
def get_todays_meetings():
    access_token = get_access_token()
    if not access_token:
        return None

    local_tz = pytz.timezone("America/Los_Angeles")
    today = datetime.now(local_tz).date()
    tomorrow = today + timedelta(days=1)

    start_time = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=local_tz).isoformat()
    end_time = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0, tzinfo=local_tz).isoformat()

    url = f"{config.GRAPH_API_ENDPOINT}/me/calendarview?startDateTime={start_time}&endDateTime={end_time}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Prefer': f'outlook.timezone="{local_tz.zone}"'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        meetings = response.json()['value']
        # Print the meetings for the day
        print("Meetings for the day:")
        for meeting in meetings:
            # Check if the time zone is provided in the event, otherwise default to UTC
            if 'timeZone' in meeting['start']:
                meeting_tz = pytz.timezone(meeting['start']['timeZone'])
            else:
                meeting_tz = pytz.utc  # Assume UTC if no time zone is provided

            # Convert the event times from their time zone to local time
            start_time = datetime.fromisoformat(meeting['start']['dateTime'][:-1]).replace(tzinfo=meeting_tz).astimezone(local_tz)
            end_time = datetime.fromisoformat(meeting['end']['dateTime'][:-1]).replace(tzinfo=meeting_tz).astimezone(local_tz)

            print(f"- {meeting['subject']}: Start - {start_time.strftime('%I:%M %p')}, End - {end_time.strftime('%I:%M %p')}")
        return meetings
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def get_access_token():
    cache = msal.SerializableTokenCache()
    if os.path.exists(config.CACHE_FILE):
        with open(config.CACHE_FILE, "r") as file:
            cache.deserialize(file.read())
    app = msal.PublicClientApplication(config.CLIENT_ID, authority=config.AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()
    if accounts:
        token_result = app.acquire_token_silent(config.SCOPES, account=accounts[0])
        if token_result:
            return token_result['access_token']
    token_result = app.acquire_token_interactive(scopes=config.SCOPES)
    if "access_token" in token_result:
        return token_result['access_token']
    return None

# Main loop to control the lights based on meeting times
def control_lights_based_on_meetings(meetings):
    while True:
        now = datetime.now(local_tz)
        print(f"Current time: {now.strftime('%Y-%m-%d %I:%M %p')}")

        # Flags to track if any meeting needs the lights to be on
        yellow_light_needed = False
        orange_light_needed = False
        red_light_needed = False

        for meeting in meetings:
            if 'timeZone' in meeting['start']:
                meeting_tz = pytz.timezone(meeting['start']['timeZone'])
            else:
                meeting_tz = pytz.utc  # Assume UTC if no time zone is provided

            # Convert the meeting times to local time zone
            start_time = parser.isoparse(meeting['start']['dateTime']).astimezone(meeting_tz).astimezone(local_tz)
            end_time = parser.isoparse(meeting['end']['dateTime']).astimezone(meeting_tz).astimezone(local_tz)

            time_until_meeting = start_time - now
            print(f"Meeting: {meeting['subject']}, Start: {start_time.strftime('%I:%M %p')}, End: {end_time.strftime('%I:%M %p')}, Time until meeting: {time_until_meeting}")

            # Check if the yellow light is needed (15 minutes before the meeting)
            if timedelta(minutes=5) < time_until_meeting <= timedelta(minutes=15):
                print("15 minutes until meeting: Yellow light needed.")
                yellow_light_needed = True

            # Check if the orange light is needed (5 minutes before the meeting)
            if timedelta(minutes=0) < time_until_meeting <= timedelta(minutes=5):
                print("5 minutes until meeting: Orange light needed.")
                orange_light_needed = True

            # Check if the red light is needed (during the meeting)
            if start_time <= now <= end_time:
                print("Meeting in progress: Red light needed.")
                red_light_needed = True

        # Control the lights based on the aggregated results
        if yellow_light_needed:
            turn_on_led(YELLOW_PIN)
        else:
            turn_off_led(YELLOW_PIN)

        if orange_light_needed:
            turn_on_led(ORANGE_PIN)
        else:
            turn_off_led(ORANGE_PIN)

        if red_light_needed:
            turn_on_led(RED_PIN)
        else:
            turn_off_led(RED_PIN)

        time.sleep(10)  # Sleep for 10 seconds before checking again

if __name__ == "__main__":
    try:
        meetings = get_todays_meetings()  # Fetch meetings once when the script launches
        if meetings:
            control_lights_based_on_meetings(meetings)  # Enter real-time light control loop
        else:
            print("No meetings found or an error occurred.")
    finally:
        GPIO.cleanup()  # Clean up GPIO when the script is terminated
