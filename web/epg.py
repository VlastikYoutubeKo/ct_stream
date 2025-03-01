import requests
import json
import time

# Configuration for VOD channels
SOURCE_URL_PLUS = 'https://hbbtv.ceskatelevize.cz/online/services/data/online.json'
MAPPING_SERVICES_PLUS = {
    "CH_25": "CT iVysilani+ 1",
    "CH_26": "CT iVysilani+ 2",
    "CH_27": "CT iVysilani+ 3",
    "CH_28": "CT iVysilani+ 4",
    "CH_29": "CT iVysilani+ 5",
    "CH_30": "CT iVysilani+ 6",
    "CH_31": "CT iVysilani+ 7",
    "CH_32": "CT iVysilani+ 8",
    "CH_MOB_01": "CT iVysilani+ 9",
    "CH_MP_01": "CT iVysilani+ 10",
    "CH_MP_02": "CT iVysilani+ 11",
    "CH_MP_03": "CT iVysilani+ 12",
    "CH_MP_04": "CT iVysilani+ 13",
    "CH_MP_05": "CT iVysilani+ 14",
    "CH_MP_06": "CT iVysilani+ 15",
    "CH_MP_07": "CT iVysilani+ 16",
    "CH_MP_08": "CT iVysilani+ 17"
}

def get_json_epg(url, repeat=5, delay=2):
    """Fetch JSON EPG data with retry logic."""
    while repeat > 0:
        try:
            response = requests.get(url)
            return response.json()
        except:
            repeat -= 1
            print(f"WARNING: Failed to fetch data, retries left: {repeat}, retrying in {delay} seconds.")
            time.sleep(delay)
    return None

def get_xml_epg(url, repeat=1, delay=60):
    """Fetch XML EPG data with retry logic."""
    while repeat > 0:
        try:
            response = requests.get(url)
            return response.text  # Assuming further XML parsing will be done elsewhere
        except:
            repeat -= 1
            print(f"WARNING: Failed to fetch data, retries left: {repeat}, retrying in {delay} seconds.")
            time.sleep(delay)
    return None

def fetch_epg_for_channel(channel, date):
    """Fetch EPG data for a given channel and date."""
    if channel in MAPPING_SERVICES_PLUS:
        # Fetch JSON EPG for VOD channels
        return get_json_epg(SOURCE_URL_PLUS)
    else:
        # Fetch XML EPG for normal channels
        epg_url = f"https://www.ceskatelevize.cz/services-old/programme/xml/schedule.php?user=test&date={date}&channel={channel}"
        return get_xml_epg(epg_url)