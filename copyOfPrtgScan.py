import requests
import urllib3
import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PRTG_SERVER = 'xxxx'  # e.g., https://prtg.company.net

def get_credentials():
    """Prompt for username and passhash at runtime"""
    print("🔐 PRTG Login")
    username = input("Username: ").strip()
    passhash = getpass.getpass("Passhash: ")  # input is hidden
    return username, passhash

def test_prtg_login(username, passhash):
    url = f"{PRTG_SERVER}/api/table.json"
    params = {
        'username': username,
        'passhash': passhash
    }
    try:
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        print("✅ Successfully connected to PRTG!")
        print(f"Logged in as: {username}")
        print(f"PRTG Version: {data.get('prtg-version')}")
        print(f"Probes Connected: {data.get('treesize')}")
        return True
    except requests.exceptions.RequestException as e:
        print("❌ Failed to connect to PRTG:")
        print(e)
        return False

def get_all_devices(username, passhash):
    url = f"{PRTG_SERVER}/api/table.json"
    params = {
        'content': 'devices',
        'output': 'json',
        'columns': 'objid,device',
        'username': username,
        'passhash': passhash
    }
    response = requests.get(url, params=params, verify=False)
    response.raise_for_status()
    return response.json().get('devices', [])

def search_devices(username, passhash):
    search_term = input("🔍 Enter the string to search for in device names: ").strip().lower()
    if not search_term:
        print("⚠️ No search term provided. Exiting.")
        return

    devices = get_all_devices(username, passhash)
    matches = [d for d in devices if search_term in d['device'].lower()]

    if matches:
        print(f"\n✅ Found {len(matches)} device(s) containing '{search_term}':")
        for device in matches:
            print(f"- {device['device']} (ID: {device['objid']})")
    else:
        print(f"❌ No devices found containing '{search_term}'.")

if __name__ == '__main__':
    username, passhash = get_credentials()
    if test_prtg_login(username, passhash):
        search_devices(username, passhash)
