import requests
import json
import time
from requests.auth import HTTPBasicAuth
from pywifi import PyWiFi, const


# Shelly device configuration
SHELLY_IP = 'http://192.168.33.1'  # Shelly device's IP address
SSID = 'MorsaWifi'  # Target Wi-Fi network SSID
PASSWORD = 'Matthias'  # Wi-Fi network password

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
            #update_wifi_config(SHELLY_IP, SSID, PASSWORD)
            update_led_status(shelly_ip, led_status_disable=True, led_power_disable=True)

        else:
            print(f"Failed to connect to {shelly_ap_ssid}. Please try again.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")