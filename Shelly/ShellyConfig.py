import requests
import json
import time
from requests.auth import HTTPBasicAuth
from pywifi import PyWiFi, const
from ShellySettings import *

# Shelly device configuration
SHELLY_IP = f'http://{shelly_ip_address}'  # Shelly device's IP address
SSID = network_wifi_ssid  # Target Wi-Fi network SSID
PASSWORD = network_wifi_password

# Shelly enable/disable led status for either status or power
def update_led_status(ip_address, led_status_disable=None, led_power_disable=None):
    """
    Update the LED status settings on the Shelly device.
    
    :param ip_address: IP address of the Shelly device
    :param led_status_disable: Disable the status LED (True/False or None to skip)
    :param led_power_disable: Disable the power LED (True/False or None to skip)
    """
    # Map the parameters to their respective query strings
    settings = {
        "led_status_disable": led_status_disable,
        "led_power_disable": led_power_disable
    }
    
    for setting, value in settings.items():
        if value is not None:  # Only send the request if the value is specified
            url = f"{ip_address}/settings?{setting}={str(value).lower()}"  # Convert bool to lowercase string
            
            try:
                # Send GET request
                response = requests.get(url)
                
                # Print response details for debugging
                print(f"Request URL: {url}")
                print(f"Response status code: {response.status_code}")
                print(f"Response text: {response.text}")
                
                if response.status_code == 200:
                    print(f"Successfully updated {setting} to {value}.")
                else:
                    print(f"Failed to update {setting}. Response: {response.text}")
            except Exception as e:
                print(f"An error occurred while updating {setting}: {str(e)}")

# Function to update Wi-Fi settings
def update_wifi_config(ip_address, ssid, wifi_password):
    # Build the URL for the GET request
    url = f"{ip_address}/settings/sta?enabled=1&ssid={ssid}&key={wifi_password}&ipv4_method=dhcp"
    
    try:
        # Send the POST request with authentication
        response = requests.post(url)
        
        # Print response details for debugging
        print(f"Request URL: {url}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        # Check for success
        if response.status_code == 200:
            print(f"Wi-Fi configuration updated successfully. Device should connect to {ssid}.")
        else:
            print("Failed to update Wi-Fi configuration.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Function to update name of the device
def update_device_name(ip_address, new_name):
    """
    Update the device name on the Shelly device.
    
    :param ip_address: IP address of the Shelly device
    :param new_name: New name for the Shelly device
    """
    url = f"{ip_address}/settings"  # Target URL for the POST request
    payload = {"name": new_name}  # Payload with the new name
    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # Required content type

    try:
        # Send POST request
        response = requests.post(
            url,
            data=payload,
            headers=headers
        )
        
        # Print response details for debugging
        print(f"Request URL: {url}")
        print(f"Payload: {payload}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            print(f"Successfully updated device name to '{new_name}'.")
        else:
            print(f"Failed to update device name. Response: {response.text}")
    except Exception as e:
        print(f"An error occurred while updating the device name: {str(e)}")

# Function to set the maximum power limit
def set_max_power(ip_address, max_power):
    """
    Set the maximum power limit for the Shelly device.

    :param ip_address: IP address of the Shelly device
    :param max_power: Maximum power in watts
    """
    url = f"{ip_address}/settings/?max_power={max_power}"  # Target URL for GET request

    try:
        # Send GET request
        response = requests.post(url)
        
        # Print response details for debugging
        print(f"Request URL: {url}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            print(f"Successfully set maximum power to {max_power}W.")
        else:
            print(f"Failed to set maximum power. Response: {response.text}")
    except Exception as e:
        print(f"An error occurred while setting the maximum power: {str(e)}")

# Function to set the default state of a relay
def set_relay_default_state(ip_address, relay_id, default_state):
    """
    Set the default state of the specified relay on the Shelly device.

    :param ip_address: IP address of the Shelly device
    :param relay_id: ID of the relay to configure
    :param default_state: Default state for the relay ('off', 'on', etc.)
    """
    url = f"{ip_address}/settings/relay/{relay_id}?default_state={default_state}"  # Target URL for GET request

    try:
        # Send GET request
        response = requests.post(url)
        
        # Print response details for debugging
        print(f"Request URL: {url}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            print(f"Successfully set default state of relay {relay_id} to '{default_state}'.")
        else:
            print(f"Failed to set default state. Response: {response.text}")
    except Exception as e:
        print(f"An error occurred while setting the default state: {str(e)}")

# Function to configure MQTT settings
def configure_mqtt(ip_address, broker_ip, topic):
    """
    Configure MQTT settings on a Shelly device.

    :param ip_address: IP address of the Shelly device
    :param broker_ip: MQTT broker address
    :param topic: MQTT topic to publish on
    """
    # Construct the payload for MQTT settings
    payload = {
        "mqtt_server": broker_ip,
        "mqtt_enable": True,
        "mqtt_user": "",  # No authentication for this broker
        "mqtt_pass": "",
        "mqtt_id": topic,  # Use the constructed topic as the MQTT ID
        "mqtt_max_qos": 0,  # Default QoS level
        "mqtt_retain": False  # Default retain setting
    }

    # Build the URL
    url = f"{ip_address}/settings"

    try:
        # Send GET request to configure MQTT
        response = requests.get(url, params=payload)
        
        # Print response details
        print(f"Request URL: {response.url}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code == 200:
            print("MQTT configuration applied successfully.")
        else:
            print("Failed to configure MQTT. Check the response for details.")
    except Exception as e:
        print(f"An error occurred while configuring MQTT: {str(e)}")

# Function to reboot the device
def reboot_device(ip_address):
    """
    Reboot the Shelly device.

    :param ip_address: IP address of the Shelly device
    """
    url = f"{ip_address}/settings/reboot"  # Target URL for the POST request

    try:
        # Send POST request to reboot the device
        response = requests.post(url)
        
        # Print response details
        print(f"Request URL: {url}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code == 200:
            print("Device reboot initiated.")
        else:
            print("Failed to reboot the device. Check the response for details.")
    except Exception as e:
        print(f"An error occurred while rebooting the device: {str(e)}")

# Function to connect to Wi-Fi AP
def connect_to_wifi(ssid):
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(2)
    scan_results = iface.scan_results()
    for result in scan_results:
        if result.ssid == ssid:
            iface.connect(result)
            time.sleep(5)
            if iface.status() == const.IFACE_CONNECTED:
                print(f"Connected to {ssid}")
                return True
    return False


if __name__ == "__main__":
    try:
        # Scan and connect to Shelly AP
        shelly_ap_ssid = "shellyplug-s-7C87CEB51F45"  # Modify this to the Shelly AP SSID
        if connect_to_wifi(shelly_ap_ssid):
            shelly_ip = SHELLY_IP
            # Send the device name configuration
            update_led_status(shelly_ip, led_status_disable=True, led_power_disable=True)
            update_device_name(SHELLY_IP, "MorsaPlug")
            set_max_power(SHELLY_IP, 2200)
            set_relay_default_state(SHELLY_IP, 0, "off") # shelly plug s has only one relay
            configure_mqtt(SHELLY_IP, "172.23.83.254", "Morsa-Matthias-Outlet1")
            update_wifi_config(SHELLY_IP, SSID, PASSWORD)
            reboot_device(SHELLY_IP)# api1 doesn let reboot work after wifi config so we need to reboot manually
            print("Configuration completed. Take device out of the socket and plug it back in.")
        else:
            print(f"Failed to connect to {shelly_ap_ssid}. Please try again.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")