import requests
import urllib3
import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PRTG_SERVER = 'xxxx'  # e.g., https://prtg.company.net

def get_credentials():
    #Prompt for username and password
    print("PRTG Login")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    return username, password

#initial login - test connection and print some info about the prtg instance
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
        print("Successfully connected to PRTG!")
        print(f"Logged in as: {username}")
        print(f"PRTG Version: {data.get('prtg-version')}")
        print(f"Total Devices: {data.get('treesize')}")
        return True
    except requests.exceptions.RequestException as e:
        print("Failed to connect to PRTG:")
        print(e)
        return False

#function to fetch all devices with pagination, since some instannces have over 2500
#devices and the API limits to 2500 per request. This will fetch all devices
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

#function to delete a device by its object ID, only on confirmation typed out
#exactly as specified, to prevent accidental deletion. Also only allows delete if exactly one
#match was found in the search, to prevent deleting the wrong device.
def delete_device(username, password, objid, device_name):
    # only allow delete if exactly one match was found
    confirm = input(f"\nYou are about to delete: {device_name} (ID: {objid})\nType 'YES I WANT TO DELETE THIS SINGLE NODE' to confirm: ").strip()
    
    #confirmation must match exactly to proceed with deletion
    if confirm != "YES I WANT TO DELETE THIS SINGLE NODE":
        print("Confirmation did not match. Delete cancelled.")
        return

    #url for api call to delete the device by its object ID,
    #only with the approve parameter set to 1, which is required for deletion.
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
        print(f"Successfully deleted: {device_name} (ID: {objid})")
    #if deletion doesnt work, print error message with details
    except requests.exceptions.RequestException as e:
        print(f"Failed to delete device:")
        print(e)

#search function to look for the devices that we want to delete, by device name.
#not case senitive, and will return all devices that contain the search term in their name.
def search_devices(username, password):
    #turn input into lowercase and strip whitespace for case-insensitive searching
    search_term = input("Enter the string to search for in device names: ").strip().lower()
    if not search_term:
        print("No search term provided. Exiting.")
        return

    devices = get_all_devices(username, password)
    #search for the lowercase search term
    matches = [d for d in devices if search_term in d['device'].lower()]

    if matches:
        print(f"\nFound {len(matches)} device(s) containing '{search_term}':")
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
            print("\nMultiple devices found — refine your search to a single result before deleting.")
    else:
        print(f"No devices found containing '{search_term}'.")

#run the script
if __name__ == '__main__':
    username, password = get_credentials()
    if test_prtg_login(username, password):
        search_devices(username, password)
