import requests
import urllib3

# Suppress SSL warnings (for self-signed certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Replace these with your actual values
PRTG_SERVER = 'xxxx'  # e.g., https://prtg.company.net
USERNAME = 'xxxx' # e.g., 'your username'
PASSHASH = 'xxxx'  # NOT your plain password, go to setup->account settings to get your passhash

def test_prtg_login():
    url = f"{PRTG_SERVER}/api/table.json"
    params = {
        'username': USERNAME,
        'passhash': PASSHASH
    }

    try:
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        print("✅ Successfully connected to PRTG!")
        print(f"Logged in as: {USERNAME}")
        print(f"PRTG Version: {data.get('prtg-version')}")
        print(f"Probes Connected: {data.get('treesize')}")
    except requests.exceptions.RequestException as e:
        print("❌ Failed to connect to PRTG:")
        print(e)
def get_all_devices():
    url = f"{PRTG_SERVER}/api/table.json"
    params = {
        'content': 'devices',
        'output': 'json',
        'columns': 'objid,device',
        'username': USERNAME,
        'passhash': PASSHASH
    }
    response = requests.get(url, params=params, verify=False)
    response.raise_for_status()
    return response.json().get('devices', [])

def search_devices():
    search_term = input("🔍 Enter the string to search for in device names: ").strip().lower()
    if not search_term:
        print("⚠️ No search term provided. Exiting.")
        return

    devices = get_all_devices()
    matches = [d for d in devices if search_term in d['device'].lower()]

    if matches:
        print(f"\n✅ Found {len(matches)} device(s) containing '{search_term}':")
        if len(matches) > 1:
            print("Here are the matching devices:")
            for device in matches:
                print(f"- {device['device']} (ID: {device['objid']})")
        else:
            #can use this for deletes if the results are 1 or less, unless...
            for device in matches:
                print(f"- {device['device']} (ID: {device['objid']})")
    else:
        print(f"❌ No devices found containing '{search_term}'.")

if __name__ == '__main__':
    test_prtg_login()
    search_devices()