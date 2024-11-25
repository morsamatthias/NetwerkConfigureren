import requests
import json
import time
import hashlib
import subprocess
from pywifi import PyWiFi, const
import os
import re
from ShellySettings import * 

SHELLY_IP = shelly_ip_address
WIFI_SSID = network_wifi_ssid
WIFI_PASSWORD = network_wifi_password
GATEWAY = network_gateway
NETMASK = network_netmask
DNS = network_dns
PASSWORD = shelly_password
USERNAME = shelly_username

def get_current_config(ip_address):
    url = f"http://{ip_address}/rpc/Sys.GetConfig"
    try:
        response = requests.get(url)
        if response.status_code == 200: 
            print("Current configuration fetched successfully")
            print(response.json())
            return response.json()
        else:
            print(f"Failed to fetch current configuration. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while fetching current configuration: {str(e)}")
    return None

def send_wifi_config(ip_address, static_ip, wifi_ssid, wifi_password, gateway, netmask, dns):
    payload = {
        "config": {
            "sta": {
                "ipv4mode": "static",
                "ip": static_ip,
                "ssid": wifi_ssid,
                "pass": wifi_password,
                "enable": True,
                "gw": gateway,
                "netmask": netmask,
                "nameserver": dns
            }
        }
    }

    url = f"http://{ip_address}/rpc/WiFi.SetConfig"
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("Wi-Fi configuration sent successfully.")
            print(f"Joined Network: {wifi_ssid}")
            # print(response.text)
        else:
            print(f"Failed to send Wi-Fi configuration. Status code: {response.status_code}")
            print(f"Could not join network: {wifi_ssid}")
            # print(response.text)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def send_device_name_config(ip_address, device_name):
    payload = {
        "config": { 
            "device": {
                "name": device_name
            }
        }
    }

    url = f"http://{ip_address}/rpc/Sys.SetConfig"
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("Device name configuration sent successfully.")
            print(f"New Name: {device_name}")
            # print(response.text)
        else:
            print(f"Failed to send device name configuration. Status code: {response.status_code}")
            # print(response.text)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def check_for_update(ip_address):
    try:
        url = f"http://{ip_address}/rpc/Shelly.CheckForUpdate"
        response = requests.get(url)
        if response.status_code == 200:
            update_info = response.json()
            stable_version = update_info.get("stable")
            beta_version = update_info.get("beta")
            if stable_version or beta_version:
                print("New firmware version found!")
                if stable_version:
                    print(f"Stable version: {stable_version['version']}, Build ID: {stable_version['build_id']}")
                if beta_version:
                    print(f"Beta version: {beta_version['version']}, Build ID: {beta_version['build_id']}")
                return True
            else:
                print("No new firmware updates available.")
        else:
            print(f"No new firmware updates available.")
    except Exception as e:
        print(f"An error occurred while checking for firmware update: {str(e)}")
    return False

def perform_update(ip_address, stage="stable", url=None):
    try:
        payload = {
            "stage": stage
        }
        if url:
            payload["url"] = url
        
        url = f"http://{ip_address}/rpc/Shelly.Update"
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Starting firmware update...")
        else:
            print(f"Firmware update failed. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred during firmware update: {str(e)}")

def disable_bluetooth(ip_address):
    payload = {
        "config": {
            "enable": False
        }
    }
    url = f"http://{ip_address}/rpc/BLE.SetConfig"
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("Bluetooth disabled successfully.")
            # print(response.text)
        else:
            print(f"Failed to disable Bluetooth. Status code: {response.status_code}")
            # print(response.text)
    except Exception as e:
        print(f"An error occurred while disabling Bluetooth: {str(e)}")

def calculate_ha1(username, realm, password):
    ha1_input = f"{username}:{realm}:{password}"
    ha1 = hashlib.sha256(ha1_input.encode('utf-8')).hexdigest()
    return ha1

def reboot_device(ip_address):
    url = f"http://{ip_address}/rpc/Shelly.Reboot"
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps({}))
        if response.status_code == 200:
            print("Device reboot initiated successfully.")
        else:
            print(f"Failed to reboot device. Status code: {response.status_code}")
            # print(response.text)
    except Exception as e:
        print(f"An error occurred while rebooting the device: {str(e)}")

def profile_exists(ssid):
    command = ["netsh", "wlan", "show", "profiles"]
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return ssid in result.stdout

def add_wifi_profile(ssid):
    profile_xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>open</authentication>
                <encryption>none</encryption>
            </authEncryption>
        </security>
    </MSM>
</WLANProfile>"""
    
    profile_path = f"{ssid}.xml"
    with open(profile_path, 'w') as file:
        file.write(profile_xml)

    command = ["netsh", "wlan", "add", "profile", f"filename={profile_path}"]
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    os.remove(profile_path)

    if result.returncode != 0:
        print(f"Failed to add profile for {ssid}: {result.stderr}")
    else:
        print(f"Profile added for {ssid}")

def connect_to_wifi(ssid):
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]
    
    profile = None
    for profile in iface.network_profiles():
        if profile.ssid == ssid:
            iface.connect(profile)
            time.sleep(5)
            if iface.status() == const.IFACE_CONNECTED:
                return True
            else:
                return False
    
    return False

def validate_ip(ip_address: str) -> bool:
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    
    if not ip_pattern.match(ip_address):
        print("Invalid IP format")
        return False

    octets = ip_address.split('.')
    
    for octet in octets:
        if not octet.isdigit():
            print(f"Invalid character: '{octet}' is not a number.")
            return False
        if not (0 <= int(octet) <= 255):
            print(f"Out of range: '{octet}' is not between 0 and 255.")
            return False
    
    return True

def set_auth_credentials(device_ip, username, realm, password, device_id):
    ha1 = calculate_ha1(username, realm, password)
    url = f"http://{device_ip}/rpc/Shelly.SetAuth"

    payload = {
        "pass": password,
        "user": username,
        "realm": device_id,
        "ha1": ha1,
        "auth": {
        "protect": True
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("Authentication credentials set successfully.")
            # print(response.text)

        else:
            print(f"Failed to set authentication credentials. Status code: {response.status_code}")
            # print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error setting authentication credentials: {e}")

def wait_for_device(ip_address, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://{ip_address}/rpc/Sys.GetConfig")
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            time.sleep(5)
    return False

if __name__ == "__main__":
    try:
        shelly_access_points = []    
        wifi = PyWiFi()
        iface = wifi.interfaces()[0] 
        iface.scan()
        time.sleep(2)

        scan_results = iface.scan_results()
        for result in scan_results:
            if result.ssid.startswith('Shelly') and result.ssid not in shelly_access_points:
                shelly_access_points.append(result.ssid)

        if shelly_access_points:
            print("Shelly Access Points found:", shelly_access_points)
            
            for shelly_ap_ssid in shelly_access_points:
                print("Iterating New Shelly Device:")
                time.sleep(.8)
                print(".")
                time.sleep(.8)
                print(".")
                time.sleep(.8)
                print(".")
                time.sleep(.8)
                print('\n'*100)
                print(f"Shelly AP SSID: {shelly_ap_ssid}")

                if not profile_exists(shelly_ap_ssid):
                    print(f"Profile for {shelly_ap_ssid} does not exist. Adding profile.")
                    add_wifi_profile(shelly_ap_ssid)
                else:
                    print(f"Profile for {shelly_ap_ssid} already exists.")

                if connect_to_wifi(shelly_ap_ssid):
                    shelly_ip = SHELLY_IP
                    static_ip = input("New Static IP:")
                    device_name = input("New Device Name: ")
                    wifi_ssid = WIFI_SSID
                    wifi_password = WIFI_PASSWORD
                    gateway = GATEWAY
                    netmask = NETMASK
                    dns = DNS
                    password = PASSWORD
                    username = USERNAME
                    realm = shelly_ap_ssid.lower()

                    if validate_ip(static_ip):
                        current_config = get_current_config(shelly_ip)
                        time.sleep(2)

                        disable_bluetooth(shelly_ip)
                        time.sleep(2)

                        send_wifi_config(shelly_ip, static_ip, wifi_ssid, wifi_password, gateway, netmask, dns)
                        time.sleep(10)

                        if wait_for_device(shelly_ip):
                            if check_for_update(shelly_ip):
                                perform_update(shelly_ip)
                                time.sleep(30)
                                
                            if wait_for_device(shelly_ip):
                                send_device_name_config(shelly_ip, device_name)
                                time.sleep(10)
                                
                                if wait_for_device(shelly_ip):
                                    reboot_device(shelly_ip)
                                    time.sleep(10)
                                        
                                    if wait_for_device(shelly_ip):
                                        set_auth_credentials(shelly_ip, username, realm, password, realm)
                                    else:
                                        print("Device did not become available after setting password.")
                                else:
                                    print("Device did not become available after setting device name.")
                            else:
                                print("Device did not become available after firmware update.")
                        else:
                            print("Device did not become available after setting Wi-Fi configuration.")
                    else:
                        print("Invalid IP Address. Please try again.")
                else:
                    print(f"Failed to connect to {shelly_ap_ssid}.")
        else:
            print("No Shelly AP found.")
    except (RuntimeError, TypeError, NameError) as e:
        print(f"Code stopped running due to an error: {e}")