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

# Function to handle the configuration of interfaces, VLANs, and routing
def handle_interface(interface, vlan, description, ip_address, subnet_mask, default_gateway):
    config_commands = []
    
    # Configure the interface
    config_commands.append(f"interface {interface}")
    if ip_address:
        config_commands.append(f"ip address {ip_address} {subnet_mask}")
    if default_gateway:
        config_commands.append(f"ip default-gateway {default_gateway}")
    config_commands.append(f"description {description}")
    config_commands.append("no shutdown")
    config_commands.append("exit")  # Exit interface configuration mode
    
    # For VLANs, configure them
    if vlan != '0':  # Skip if vlan is 0
        config_commands.append(f"vlan {vlan}")
        config_commands.append(f" name {description}")
        config_commands.append("exit")  # Exit VLAN configuration mode
    
    return config_commands

# Function to handle static routes for specific subnets
def handle_static_routes(network, subnet_mask, default_gateway):
    config_commands = []
    # Add a static route for the specified network via its gateway
    if network and subnet_mask and default_gateway:
        route_command = f"ip route {network} {subnet_mask} {default_gateway}"
        if route_command not in config_commands:  # Prevent duplicates
            config_commands.append(route_command)
    return config_commands

def handle_routing(wan_gateway):
    config_commands = []
    # Static route to the ISP gateway for internet access
    if wan_gateway:
        config_commands.append(f"ip route 0.0.0.0 0.0.0.0 {wan_gateway}")  # Default route to ISP gateway
    return config_commands

# Define a function to process the CSV data and generate configuration commands
def generate_config(csv_file):
    config_commands = []
    wan_gateway = None  # Store WAN gateway IP to configure the default route
    
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
            
            # Add interface and VLAN configuration commands
            if interface:
                print(f"Configuring {interface} for {description} with IP {ip_address}")
                interface_commands = handle_interface(interface, vlan, description, ip_address, subnet_mask, default_gateway)
                config_commands.extend(interface_commands)
            
            # Handle static routes for specific networks with gateways
            if network and default_gateway:
                print(f"Adding static route for {ip_address}/{subnet_mask} via {default_gateway}")
                static_routes = handle_static_routes(ip_address, subnet_mask, default_gateway)
                config_commands.extend(static_routes)
            
            # If this is the WAN interface, store its gateway for the default route
            if interface == 'gi0/0' and default_gateway:
                wan_gateway = default_gateway

    # Add static routing to provide internet access (default route) if WAN gateway is defined
    if wan_gateway:
        config_commands.extend(handle_routing(wan_gateway))
    
    # Enable IP routing if Layer 3 configuration (IP addressing) is used
    config_commands.insert(0, "ip routing")  # Add at the top of the configuration
    config_commands.append("! IP routing was enabled to allow internet access.")

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
    csv_file = 'config3.csv'  # Path to your CSV file
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
