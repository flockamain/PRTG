import requests
import urllib3
import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PRTG_SERVER = 'xxxx'  # e.g., https://prtg.company.net

def get_credentials():
    """Prompt for username and password at runtime"""
    print("🔐 PRTG Login")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    return username, password

def test_prtg_login(username, password):
    url = f"{PRTG_SERVER}/api/table.json"
    params = {
        'username': username,
        'password': password
    }
    try:
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        print("✅ Successfully connected to PRTG!")
        print(f"Logged in as: {username}")
        print(f"PRTG Version: {data.get('prtg-version')}")
        print(f"Total Devices: {data.get('treesize')}")
        return True
    except requests.exceptions.RequestException as e:
        print("❌ Failed to connect to PRTG:")
        print(e)
        return False

def get_all_devices(username, password):
    url = f"{PRTG_SERVER}/api/table.json"
    all_devices = []
    start = 0

    while True:
        params = {
            'content': 'devices',
            'output': 'json',
            'columns': 'objid,device',
            'username': username,
            'password': password,
            'count': 2500,
            'start': start
        }
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()

        devices = data.get('devices', [])
        all_devices.extend(devices)

        print(f"Fetched {len(all_devices)} / {data.get('treesize')} devices...")

        if len(all_devices) >= data.get('treesize', 0):
            break

        start += 2500

    return all_devices

def delete_device(username, password, objid, device_name):
    """Delete a device by its object ID"""
    # only allow delete if exactly one match was found
    confirm = input(f"\n⚠️  You are about to delete: {device_name} (ID: {objid})\nType 'YES I WANT TO DELETE THIS SINGLE NODE' to confirm: ").strip()
    
    if confirm != "YES I WANT TO DELETE THIS SINGLE NODE":
        print("❌ Confirmation did not match. Delete cancelled.")
        return

    url = f"{PRTG_SERVER}/api/deleteobject.htm"
    params = {
        'id': objid,
        'approve': 1,
        'username': username,
        'password': password
    }
    try:
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        print(f"✅ Successfully deleted: {device_name} (ID: {objid})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to delete device:")
        print(e)

def search_devices(username, password):
    search_term = input("🔍 Enter the string to search for in device names: ").strip().lower()
    if not search_term:
        print("⚠️ No search term provided. Exiting.")
        return

    devices = get_all_devices(username, password)
    matches = [d for d in devices if search_term in d['device'].lower()]

    if matches:
        print(f"\n✅ Found {len(matches)} device(s) containing '{search_term}':")
        for device in matches:
            print(f"- {device['device']} (ID: {device['objid']})")

        # only offer delete if exactly one device was found
        if len(matches) == 1:
            device = matches[0]
            delete_choice = input(f"\nWould you like to delete '{device['device']}'? (yes/no): ").strip().lower()
            if delete_choice == 'yes':
                delete_device(username, password, device['objid'], device['device'])
            else:
                print("Delete skipped.")
        else:
            print("\n⚠️  Multiple devices found — refine your search to a single result before deleting.")
    else:
        print(f"❌ No devices found containing '{search_term}'.")

if __name__ == '__main__':
    username, password = get_credentials()
    if test_prtg_login(username, password):
        search_devices(username, password)
