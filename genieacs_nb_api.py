import json
import os
from enum import Enum
from typing import Dict, List, Tuple

import requests


class Collection(Enum):
    DEVICES = "devices"
    TASKS = "tasks"
    PRESETS = "presets"
    FILES = "files"


def _extract_parameter_values_from_response(json_payload: Dict, paths: List[str]) -> Dict:
    result = {}
    for path in paths:
        # Split the path into components
        components = path.split(".")

        # Traverse the JSON object
        current = json_payload
        for component in components:
            if isinstance(current, dict) and component in current:
                current = current[component]
            else:
                current = None
                break

        if current is not None:
            result[path] = current.get("_value")

    return result


class GenieAcsNbApi:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _search_db(self, collection: Collection, query_filter: Dict) -> Dict:
        url = f"{self.base_url}/{collection.value}/"
        params = {"query": query_filter}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def search_db_get_devices_by_id(self, device_id: str) -> Dict:
        """Get a device by ID"""
        if not device_id:
            raise ValueError("Device ID cannot be empty")
        query_filter = {"_id": device_id}
        params = {"query": json.dumps(query_filter)}
        headers = {'Content-Type': 'application/json'}

        url = f"{self.base_url}/devices/"
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def search_db_get_devices_by_filter(self, query_filter: Dict) -> List[Dict]:
        """Get a list of devices that match the query"""
        url = f"{self.base_url}/devices/"
        params = {"query": json.dumps(query_filter)}
        headers = {'Content-Type': 'application/json'}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def search_db_get_device_parameter_values(self, device_id: str, parameter_names: List[str]) -> Dict:
        """ Get a device's parameter values"""
        url = f"{self.base_url}/devices/"
        if not device_id:
            raise ValueError("Device ID cannot be empty")
        query_filter = {"_id": device_id}
        params = {"query": json.dumps(query_filter), "projection": ",".join(parameter_names), }
        headers = {'Content-Type': 'application/json'}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return _extract_parameter_values_from_response(response.json()[0], parameter_names)

    def search_db_get_tasks_by_id(self, task_id: str) -> Dict:
        pass

    def search_db_list_all_registered_devices(self) -> List[Dict]:
        """Get a list of devices that match the query"""
        url = f"{self.base_url}/devices/"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def delete_device_from_db(self, device_id: str) -> None:
        url = f"{self.base_url}/devices/{device_id}"
        response = requests.delete(url)
        response.raise_for_status()

    def _enqueue_task(self, device_id: str, task_data: Dict, connection_request: bool, timeout: int) -> Dict:
        if connection_request:
            url = f"{self.base_url}/devices/{device_id}/tasks?connection_request&timeout={timeout}"
        else:
            url = f"{self.base_url}/devices/{device_id}/tasks"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(task_data))
        if response.status_code == 200:
            print("Request successful")
        elif response.status_code == 202:
            print("Request accepted")
        else:
            print(f"Request failed with status code {response.status_code}")
            response.raise_for_status()
        return response.json()

    def reboot_device(self, device_id: str, force_connect: bool = False, timeout: int = 3000) -> Dict:
        """Reboot a device"""
        task_payload = {"name": "reboot"}
        return self._enqueue_task(device_id, task_payload, force_connect, timeout)

    def factory_reset_device(self, device_id: str, force_connect: bool = False, timeout: int = 3000) -> Dict:
        """Factory reset a device"""
        task_payload = {"name": "factoryReset"}
        return self._enqueue_task(device_id, task_payload, force_connect, timeout)

    def get_parameter_values(self, device_id: str, parameter_names: List[str], force_connect: bool = False,
                             timeout: int = 3000) -> Dict:
        """Get a device parameter value"""
        task_payload = {"name": "getParameterValues", "parameterNames": parameter_names}
        response = self._enqueue_task(device_id, task_payload, force_connect, timeout)
        return response

    def set_parameter_values(self, device_id: str, parameter_values: List[Tuple[str, str, str]],
                             force_connect: bool = False, timeout: int = 3000) -> Dict:
        """Set a device parameter value"""
        task_payload = {"name": "setParameterValues", "parameterValues": parameter_values}
        return self._enqueue_task(device_id, task_payload, force_connect, timeout)

    def refresh_device_object(self, device_id: str, object_name: str) -> Dict:
        """Refresh a device object"""
        task_payload = {"name": "refreshObject", "objectName": object_name}
        return self._enqueue_task(device_id, task_payload, connection_request=True, timeout=3000)

    def add_device_object(self, device_id: str, object_name: str) -> Dict:
        """Add a device object"""
        task_payload = {"name": "addObject", "objectName": object_name}
        return self._enqueue_task(device_id, task_payload, connection_request=True, timeout=3000)

    def delete_device_object(self, device_id: str, object_name: str) -> Dict:
        """Delete a device object"""
        task_payload = {"name": "deleteObject", "objectName": object_name}
        return self._enqueue_task(device_id, task_payload, connection_request=True, timeout=3000)

    def retry_task(self, task_id: str) -> None:
        url = f"{self.base_url}/tasks/{task_id}/retry"
        response = requests.post(url)
        response.raise_for_status()

    def delete_task(self, task_id: str) -> None:
        url = f"{self.base_url}/tasks/{task_id}"
        response = requests.delete(url)
        response.raise_for_status()

    def assign_tag(self, device_id: str, tag: str) -> None:
        url = f"{self.base_url}/devices/{device_id}/tags/{tag}"
        response = requests.post(url)
        response.raise_for_status()

    def remove_tag(self, device_id: str, tag: str) -> None:
        url = f"{self.base_url}/devices/{device_id}/tags/{tag}"
        response = requests.delete(url)
        response.raise_for_status()

    def create_preset(self, preset_name: str, preset: Dict) -> None:
        url = f"{self.base_url}/presets/{preset_name}"
        response = requests.put(url, json=preset)
        response.raise_for_status()

    def delete_preset(self, preset_name: str) -> None:
        url = f"{self.base_url}/presets/{preset_name}"
        response = requests.delete(url)
        response.raise_for_status()

    def upload_file(self, file_name: str, file_content: bytes, file_type: str, oui: str, product_class: str,
                    version: str) -> None:
        url = f"{self.base_url}/files/{file_name}"
        headers = {"fileType": file_type, "oui": oui, "productClass": product_class, "version": version}
        response = requests.put(url, data=file_content, headers=headers)
        response.raise_for_status()

    def delete_file(self, file_name: str) -> None:
        url = f"{self.base_url}/files/{file_name}"
        response = requests.delete(url)
        response.raise_for_status()

    def get_files(self) -> List[Dict]:
        url = f"{self.base_url}/files/"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_file(self, file_name: str) -> Dict:
        url = f"{self.base_url}/files/{file_name}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


if __name__ == '__main__':
    # Read from .env file in the current directory
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(raise_error_if_not_found=True, usecwd=True))
    GENIEACS_URL = os.getenv("GENIEACS_URL")

    # Connect to the GenieACS instance
    api = GenieAcsNbApi(GENIEACS_URL)
    for device in api.search_db_list_all_registered_devices():
        print(device["_id"])
