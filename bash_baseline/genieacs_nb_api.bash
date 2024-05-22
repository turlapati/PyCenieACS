#!/bin/bash

encode_json() {
    local json_string="$1"
    printf "%s" "$json_string" | xxd -plain | tr -d '\n' | sed 's/\(..\)/%\1/g'
}

# Prompt for inputs
read -p "Enter the base URL (e.g., http://localhost:7557): " base_url
read -p "Enter the device ID (e.g., 202BC1-BM632w-000000): " device_id
read -p "Enter the MAC address (e.g., 20:2B:C1:E0:06:65): " mac_address

# Define the JSON payloads
device_id_payload='{"_id": "'"$device_id"'"}'
device_mac_payload='{"Device.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": "'"$mac_address"'"}'
last_inform_filter='{"_lastInform": {"$lt" : "2017-12-11 13:16:23 +0000"}}'

# Encode the JSON payloads
encoded_device_id=$(encode_json "$device_id_payload")
encoded_device_mac=$(encode_json "$device_mac_payload")
encoded_last_inform=$(encode_json "$last_inform_filter")

# Find a device by its ID
printf "Device by ID"
curl -i "$base_url/devices/?query=$encoded_device_id"
printf "\n\n"

# Find a device by its MAC address
printf "Device by MAC Address"
curl -i "$base_url/devices/?query=$encoded_device_mac"
printf "\n\n"

# Search for devices that have not initiated an inform in the last 7 days
printf "Devices not seen in last 7 days"
curl -i "$base_url/devices/?query=$encoded_last_inform"
printf "\n\n"

# Return specific parameters for a given device
printf "Get specific parameters of the device"
curl -i "$base_url/devices/?query=$encoded_device_id&projection=Device.DeviceInfo.ModelName,Device.DeviceInfo.Manufacturer"
printf "\n\n"

# Show pending tasks for a given device
printf "Show any pending tasks"
curl -i "$base_url/tasks/?query=$encoded_device_id"
printf "\n\n"