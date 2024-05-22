# GenieACS Northbound APIs
## Reference
https://github.com/genieacs/genieacs/blob/v1.2.12/docs/api-reference.rst
## Common bash script
Use following function to encode JSON payload for cURL commands (especially for **GET** commands)
```bash
#!/bin/bash

encode_json() {
    local json_string="$1"
    printf "%s" "$json_string" | xxd -plain | tr -d '\n' | sed 's/\(..\)/%\1/g'
}

# Define the JSON payloads
device_id='{"_id": "202BC1-BM632w-000000"}'
device_mac_id='{"Device.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": "20:2B:C1:E0:06:65"}'
last_inform_filter='{"_lastInform": {"$lt" : "2017-12-11 13:16:23 +0000"}}'

# Encode the JSON payload
encoded_device_id=$(encode_json "$payload")
encoded_device_mac_id=$(encode_jsion "$device_mac_id")
encoded_last_inform=$(encode_jsion "$last_inform_filter")
```
## Devices
### GET /devices/?query=\<query\>
Search for device records in **GenieACS database**. 
Returns a JSON representation of all items for the device(s) that match the search criteria.
#### Find a device by its ID 
```shell
curl -i 'http://localhost:7557/devices/?query=$encoded_device_id'
```
#### Find a device by its MAC address
```shell
curl -i 'http://localhost:7557/devices/?query=$encoded_device_mac_id
```
#### Search for devices that have not initiated an inform in the last 7 days
```shell
curl -i 'http://localhost:7557/devices/?query=$encoded_last_inform'
```
#### Return specific parameters for a given device
```shell
curl -i 'http://localhost:7557/devices/?query=$encoded_payload&projection=Device.DeviceInfo.ModelName,Device.DeviceInfo.Manufacturer'
```
### DELETE /devices/\<device_id\>
Delete the given device from **GenieACS database**.
#### Delete a device by using its ID 
```shell
curl -X DELETE -i 'http://localhost:7557/devices/202BC1-BM632w-000001'
```
### POST /devices/\<device_id\>/tasks?[connection_request]
Enqueue task(s) and optionally trigger a connection request to the device. 
Returns status code 200 if the tasks have been successfully executed, and 202 if the tasks have been queued to be executed at the next inform.

- _device_id_: The ID of the device.
- _connection_request_: Indicates that a connection request will be triggered to execute the tasks immediately. Otherwise, the tasks will be queued and be processed at the next inform.

The response body is the task object as it is inserted in the database. 
The object will include **_id** property which you can use to look up the task later.
#### Set Parameters - Change Wi-Fi SSID and Password
```shell
curl -i 'http://localhost:7557/devices/202BC1-BM632w-000000/tasks?connection_request' \
     -X POST \
     --data '{"name":"setParameterValues", "parameterValues": [["Device.LANDevice.1.WLANConfiguration.1.SSID", "GenieACS", "xsd:string"], ["Device.LANDevice.1.WLANConfiguration.1.PreSharedKey.1.PreSharedKey", "hello world", "xsd:string"]]}'
```
#### Get one or more Parameter Values
```shell
curl -i 'http://localhost:7557/devices/00236a-96318REF/tasks?timeout=3000&connection_request' \
     -X POST \
     --data '{"name": "getParameterValues", "parameterNames": ["InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnectionNumberOfEntries", "InternetGatewayDevice.Time.NTPServer1", "InternetGatewayDevice.Time.Status"]}'
```

#### Reboot the device
```shell
curl -i 'http://localhost:7557/devices/00236a-SR552n-SR552NA084%252D0003269/tasks?timeout=3000&connection_request' \
     -X POST \
     --data '{"name": "reboot"}'
```
#### Factory Reset the device
```shell
curl -i 'http://localhost:7557/devices/00236a-SR552n-SR552NA084%252D0003269/tasks?timeout=3000&connection_request' \
     -X POST \
     --data '{"name": "factoryReset"}'
```
#### Add specific object in the data model
```shell
curl -i 'http://localhost:7557/devices/00236a-SR552n-SR552NA084/tasks?timeout=3000 &connection_request' \
     -X POST \
     --data '{"name":"addObject","objectName":"Device.WANDevice.1.WANConnectionDevice.1.WANPPPConnection"}'
```
#### Delete specific object-tree in the data model
```shell
curl -i 'http://localhost:7557/devices/00236a-SR552n-SR552NA084/tasks?timeout=3000&connection_request' \
     -X POST \
     --data '{"name":"deleteObject","objectName":"Device.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1"}'
```
#### Refresh all device parameters now
```shell
curl -i 'http://localhost:7557/devices/202BC1-BM632w-000000/tasks?connection_request' \
     -X POST \
     --data '{"name": "refreshObject", "objectName": ""}'
```
#### Refresh parameters under specific object tree
```shell
curl -i 'http://localhost:7557/devices/00236a-SR552n-SR552NA084/tasks?timeout=3000&connection_request' \
     -X POST \
     --data '{"name": "refreshObject", "objectName": "Device.WANDevice.1.WANConnectionDevice"}'
```
## Tasks
### GET /tasks/?query=\<query\>
Search for task records in the database. Returns a JSON representation of all items that match the search criteria.

#### Show pending tasks for a given device:
```shell
curl -i 'http://localhost:7557/tasks/?query=$encoded_device_id'
```
### POST /tasks/\<task_id\>/retry
Retry a faulty task at the next inform.
- task_id: The ID of the task as returned by ‘GET /tasks’ request.
```shell
curl -i 'http://localhost:7557/tasks/5403908ef28ea3a25c138adc/retry' -X POST
```

### DELETE /tasks/\<task_id\>
Delete the given task.
- task_id: The ID of the task as returned by ‘GET /tasks’ request.
```shell
curl -i 'http://localhost:7557/tasks/5403908ef28ea3a25c138adc' -X DELETE
```

## Presets
### GET /presets/
#### Get list of existing presets:
```shell
curl -X GET -i 'http://localhost:7557/presets/' 
```
### DELETE /presets/\<preset_name\>
```shell
curl -i 'http://localhost:7557/presets/inform' -X DELETE
```
### PUT /presets/\<preset_name\>
Create or update a preset. Returns status code 200 if the preset has been added/updated successfully. The body of the request is a JSON representation of the preset as below:
```shell
{
  "weight": 0,
  "precondition": "{\"_tags\": \"test\"}"
  "configurations": [
    {
      "type": "value",
      "name": "Device.ManagementServer.PeriodicInformEnable",
      "value": "true"
    },
    {
      "type": "value",
      "name": "Device.ManagementServer.PeriodicInformInterval",
      "value": "300"
    }
  ]
}
```

The precondition property is a JSON string representation of the search filter to test if the preset applies to a given device. Examples preconditions are:
```shell
{"param": "value"}
{"param": "value", "param2": {"$ne": "value2"}}
```
Other operators that can be used are $gt, $lt, $gte and $lte.

The configuration property is an array containing the different configurations to be applied to a device, as shown below:
```shell
[
  {
    "type": "value",
    "name": "Device.ManagementServer.PeriodicInformEnable",
    "value": "true"
  },
  {
    "type": "value",
    "name": "Device.ManagementServer.PeriodicInformInterval",
    "value": "300"
  },
  {
    "type": "delete_object",
    "name": "object_parent",
    "object": "object_name"
  },
  {
    "type": "add_object",
    "name": "object_parent",
    "object": "object_name"
  },
  {
    "type": "provision",
    "name": "YourProvisionName"
  },
]
```

#### Example
```shell
curl -i 'http://localhost:7557/presets/inform' \
     -X PUT \
     --data '{"weight": 0, "precondition": "{\"_tags\": \"test\"}", "configurations": [{"type": "value", "name": "Device.ManagementServer.PeriodicInformEnable", "value": "true"}, {"type": "value", "name": "Device.ManagementServer.PeriodicInformInterval", "value": "300"}]}'
```

## Files
### GET /files/
### GET /files/?query={“filename”:”\<filename\>”}
#### PUT /files/\<file_name\>
Upload a new file or overwrite an existing one. Returns status code 200 if the file has been added/updated successfully. The file content should be sent as the request body.
- **file_name**: The name of the uploaded file.

The following file metadata may be sent as request headers:
- **fileType**: For firmware images it should be “1 Firmware Upgrade Image”. Other common types are “2 Web Content” and “3 Vendor Configuration File”.
- **oui**: The OUI of the device model that this file belongs to.
- **productClass**: The product class of the device.
- **version**: In case of firmware images, this refers to the firmware version.

#### Upload a firmware image file
```shell
curl -i 'http://localhost:7557/files/new_firmware_v1.0.bin' \
     -X PUT \
     --data-binary @"./new_firmware_v1.0.bin" \
     --header "fileType: 1 Firmware Upgrade Image" \
     --header "oui: 123456" \
     --header "productClass: ABC" \
     --header "version: 1.0"
```
#### Gets all previously uploaded files.
```shell
curl -i 'http://localhost:7557/files/' 
```
#### Delete a previously uploaded file:
```shell
curl -i 'http://localhost:7557/files/new_firmware_v1.0.bin' -X DELETE
```
## Provisions
### GET/PUT/DELETE /provisions/[\<provision-name\>]
#### Get list of existing provisions
```shell
curl -X GET -i 'http://localhost:7557/provisions/'
```
#### Create a provision
```shell
curl -X PUT -i 'http://localhost:7557/provisions/mynewprovision' --data 'log("Sample provision script executed at " + now);'
```
#### Delete a provision
```shell
curl -X DELETE -i 'http://localhost:7557/provisions/mynewprovision'
```
## Faults
### GET /faults/
Returns ID of the fault as string in < device_id >:< channel > format
### DELETE /faults/\<fault_id\>
Delete the given fault.
#### Example usage
```shell
curl -i 'http://localhost:7557/faults/202BC1-BM632w-000000:default' -X DELETE
```
## Objects (??)
**_Need further information_**
### GET /objects/
