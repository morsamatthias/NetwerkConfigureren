import csv
from netmiko import ConnectHandler

# Define the router credentials and connection parameters
router = {
    'device_type': 'cisco_ios',  # or 'cisco_ios_telnet' for Telnet
    'host': '192.168.100.100',  # replace with your router IP
    'username': 'cisco',  # your router username
    'password': '123',  # your router password
    'secret': 'cisco',  # enable password
    'session_log': 'session_log.txt',  # Enable session logging to file
}
remote_execution = False  # Set to True to enable remote execution on the router

# Function to handle the configuration of interfaces and VLANs
def handle_interface(interface, vlan, description, ip_address, subnet_mask, default_gateway):
    config_commands = []
    
    # Configure the interface
    config_commands.append(f"interface {interface}")
    if ip_address:
        config_commands.append(f" ip address {ip_address} {subnet_mask}")
    if default_gateway:
        config_commands.append(f" ip default-gateway {default_gateway}")
    config_commands.append(f" description {description}")
    config_commands.append(" no shutdown")
    config_commands.append("exit")  # Exit interface configuration mode
    
    # For VLANs, configure them
    config_commands.append(f"vlan {vlan}")
    config_commands.append(f" name {description}")
    config_commands.append("exit")  # Exit VLAN configuration mode
    
    return config_commands

# Define a function to process the CSV data and generate configuration commands
def generate_config(csv_file):
    config_commands = []
    ip_routing_needed = False  # Flag to track if IP routing is needed

    # Open the CSV file and read it
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file, delimiter=';')

        for row in reader:
            network = row['network']
            interface = row['interface']
            description = row['description']
            vlan = row['vlan']
            ip_address = row['ipaddress']
            subnet_mask = row['subnetmask']
            default_gateway = row['defaultgateway']
            
            print(f"Configuring {interface} for VLAN {vlan} with IP {ip_address}")
            
            # Add interface and VLAN configuration commands
            interface_commands = handle_interface(interface, vlan, description, ip_address, subnet_mask, default_gateway)
            config_commands.extend(interface_commands)

    # Enable IP routing if Layer 3 configuration (IP addressing) is used
    if ip_routing_needed:
        config_commands.insert(0, "ip routing")  # Add at the top of the configuration
        config_commands.append("! IP routing was enabled because Layer 3 VLANs are configured. (first line of the config)")

    return config_commands

# Define a function to save the generated commands to a file
def save_config_to_file(config_commands, output_file):
    with open(output_file, mode='w') as file:
        for command in config_commands:
            file.write(command + '\n')
    print(f"Configuration commands saved to {output_file}")

# Main function to run the script
def main():
    # File paths
    csv_file = 'config4.csv'  # Path to your CSV file
    output_file = 'router_config.txt'  # Path to save the generated config file

    # Generate the configuration commands from CSV data
    config_commands = generate_config(csv_file)

    # Save the configuration commands to a file
    save_config_to_file(config_commands, output_file)

    # Connect to the router using Netmiko and apply the configuration
    if remote_execution:
        try:
            with ConnectHandler(**router) as net_connect:
                net_connect.enable()  # Enter enable mode
                # Send configuration commands to the router
                net_connect.send_config_set(config_commands, read_timeout=15)
                print("Configuration applied successfully to the router.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Remote execution is disabled. Configuration commands are ONLY saved to a file.")

if __name__ == "__main__":
    main()
