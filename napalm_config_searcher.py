#!/usr/bin/python
##################################################
#
#        NAPALM Config Compliance Utility
#
#  Extemely basic, searches for a line in file
#  Only used for quick spot-checks of configs
#
##################################################
import napalm
import getpass
import os
import csv
import re

# Define Global Variables
targetsfile = "targets.txt"
directory = "/output"
output_csv = "report.csv"
username = input("Input username: ").lower()
password = getpass.getpass(prompt="Input Password: ")
search_string = input("String to search: ")

# Do you want to skip gathering configs and only run a report?
skipcollection = False
# Are we looking for an exact match, or exists?
exact_match = False

 
# Function to backup the configuration of a device
def backup_config(device, username, password):
    driver = napalm.get_network_driver(device['type'])
    device_connection = driver(hostname=device['host'], username=username, password=password)
    
    try:
        device_connection.open()
        config = device_connection.get_config()
        device_connection.close()
        
		# Set hostname for backup filenames
        host = device['host']
              
        # Create the output directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Save the configuration to a file in the output directory using the hostname as the filename
        output_file = os.path.join(directory, "{}.txt".format(host))
        with open(output_file, "w") as f:
            f.write(config['running'])
        
        return config['running']
    except Exception as e:
        print(f"Error connecting to {device['host']}: {str(e)}")
        return None


# Function to search resulting config files for matches and write output
def search_and_write_to_csv(directory, search_string, output_csv, exact_match):
    # Initialize an empty list to store the results
    results = []

    # Create a regular expression pattern for exact or partial match
    pattern = re.compile(re.escape(search_string) if exact_match else search_string)

    # Iterate through the files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            # Open and read the file's contents
            with open(file_path, 'r') as file:
                file_contents = file.read()
                # Check if the search string exists in the file's contents
                if pattern.search(file_contents):
                    result = (filename, "Match")
                else:
                    result = (filename, "No Match")
                results.append(result)

    # Write the results to a CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the header row
        csv_writer.writerow(['File', 'Match Status'])
        # Write the results
        csv_writer.writerows(results)


def main():
    
    with open(targetsfile, "r") as f:
        devices = [line.strip().split(",") for line in f]
    
    for device_info in devices:
        device = {
            'type': device_info[0],
            'host': device_info[1]
        }
        config = backup_config(device, username, password)
        
        if config is not None:
            search_and_write_to_csv(directory, search_string, output_csv, exact_match)


if __name__ == "__main__":
    main()
