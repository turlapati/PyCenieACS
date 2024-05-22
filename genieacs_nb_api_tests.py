import os
import pprint
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv, find_dotenv

from genieacs_nb_api import GenieAcsNbApi


def test_search_genie_acs_db(acs: GenieAcsNbApi):
    # Search for a device by its ID
    device_id = os.getenv("CWMP_DEVICE_ID")
    pprint.pprint(acs.search_db_get_devices_by_id(device_id))


def test_list_inactive_devices(acs: GenieAcsNbApi, days_inactive: int = 7):
    # Search for a device that have not initiated Inform in last 7 days
    days7ago = datetime.now(timezone.utc) - timedelta(days=days_inactive)
    timestamp = days7ago.strftime("%Y-%m-%d %H:%M:%S %z")
    query_payload = {"_lastInform": {"$lt": timestamp}}
    device_list = acs.search_db_get_devices_by_filter(query_payload)
    for device in device_list:
        print(device["_id"], device["Device"]["DeviceInfo"]["ModelName"]["_value"])


def test_find_device_by_imei(acs: GenieAcsNbApi):
    # Search for a device by its IMEI
    device_imei = os.getenv("CWMP_DEVICE_IMEI")
    imei_payload = {"Device.Cellular.Interface.1.IMEI": device_imei}
    pprint.pprint(acs.search_db_get_devices_by_filter(imei_payload))


def test_list_all_registered_devices(acs: GenieAcsNbApi):
    # List all devices
    results = acs.search_db_list_all_registered_devices()
    for result in results:
        try:
            print(result["_id"], result["Device"]["DeviceInfo"]["ModelName"]["_value"])
        except KeyError as e:
            print(result["_id"], f"Key: {e} not found")


def test_list_all_registered_devices_2(acs: GenieAcsNbApi):
    # List devices - using "empty" filter will return all devices
    results = acs.search_db_get_devices_by_filter({})
    for result in results:
        try:
            print(result["_id"], result["Device"]["DeviceInfo"]["ModelName"]["_value"])
        except KeyError as e:
            print(result["_id"], f"Key: {e} not found")


def test_delete_device_from_acs_db(acs: GenieAcsNbApi):
    # Search for a device by its ID
    device_id = os.getenv("CWMP_DEVICE_ID")
    device = acs.search_db_get_devices_by_id(device_id)
    acs.delete_device_from_db(device[0]["_id"])


def test_db_actions(acs: GenieAcsNbApi):
    # Tests for retrieving information from Genie ACS DB
    test_search_genie_acs_db(
        acs)  # test_find_device_by_imei(acs)  # test_list_inactive_devices(acs)  # test_list_all_registered_devices(acs)  # test_list_all_registered_devices_2(acs)  # test_delete_device_from_acs_db(acs)


def test_device_reboot_active(acs: GenieAcsNbApi):
    # Search for a device by its ID
    device_id = os.getenv("CWMP_DEVICE_ID")
    device = acs.search_db_get_devices_by_id(device_id)
    result = acs.reboot_device(device[0]["_id"], force_connect=True, timeout=5)
    pprint.pprint(result)


def test_device_reboot_passive(acs: GenieAcsNbApi):
    # Search for a device by its ID
    device_id = os.getenv("CWMP_DEVICE_ID")
    device = acs.search_db_get_devices_by_id(device_id)
    result = acs.reboot_device(device[0]["_id"])  # force_connect=False
    pprint.pprint(result)


def test_get_parameter_values(acs: GenieAcsNbApi):
    # Find the device by its ID
    device_id = os.getenv("CWMP_DEVICE_ID")
    device = acs.search_db_get_devices_by_id(device_id)
    parameter_names = ["Device.DeviceInfo.Manufacturer", "Device.DeviceInfo.ModelName", "Device.DeviceInfo.ModelNumber",
        "Device.DeviceInfo.SerialNumber", "Device.DeviceInfo.HardwareVersion", "Device.DeviceInfo.SoftwareVersion",
        "Device.DeviceInfo.UpTime", ]
    # Trigger a connect request (force_connect=True) to query the device
    response = acs.get_parameter_values(device[0]["_id"], parameter_names, force_connect=True, timeout=5)
    # pprint.pprint(response)

    # Extract the vales from the database
    results = acs.search_db_get_device_parameter_values(device[0]["_id"], parameter_names)

    for param, value in results.items():
        pprint.pprint(f"{param}: {value}")


def test_set_parameter_values(acs: GenieAcsNbApi):
    device_id = os.getenv("CWMP_DEVICE_ID")
    device = acs.search_db_get_devices_by_id(device_id)

    parameter_values = [("Device.ManagementServer.PeriodicInformInterval", "300", "xsd:unsignedInt"),
        ("Device.Time.Enable", "true", "xsd:boolean")]
    response = acs.set_parameter_values(device_id=device_id, parameter_values=parameter_values, force_connect=True,
        timeout=5)
    pprint.pprint(response)


def test_device_tasks(acs: GenieAcsNbApi):
    # test_device_reboot_passive(acs)
    # test_device_reboot_active(acs)
    # test_get_parameter_values(acs)
    test_set_parameter_values(acs)


if __name__ == '__main__':
    # Read from .env file in the current directory
    load_dotenv(find_dotenv(raise_error_if_not_found=True, usecwd=True))
    GENIEACS_URL = os.getenv("GENIEACS_URL")

    acs_server = GenieAcsNbApi(GENIEACS_URL)

    # test_db_actions(acs_server)
    test_device_tasks(acs_server)
