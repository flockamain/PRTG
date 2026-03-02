PRTG Node Deletion tool

Logs into the specified PRTG server, asks for the username and password
Verifies we can log in using the combo of server URL, username, and password
Displays information about the server - nodes, etc.

Asks for a device name (can be typed in not case-sensitive)
whatever is type in just has to be somewhere in the device name

Looks for the device - allows pagination after 2500 results because API limits to 2500 per request

If a single device is found, ask for deletion.
If more devices/no devices are found, state deletion is not allowed

For deletion, Provide detail about the node - name and object ID, then ask to type confirmation
type "YES I WANT TO DELETE THIS SINGLE NODE" exactly and the node will be deleted using
/api/deleteobject.htm, the object ID and the username/pass combo we've used this whole time along with approve set as 1

confirmation message sent to terminal upon deletion
