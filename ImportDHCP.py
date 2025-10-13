import requests
import csv
import os
import sys
from getpass import getpass

def login(base_url, username, password):
    response = requests.post(
        f"{base_url}/api/login",
        json={"userName": username, "password": password}
    )
    if response.status_code == 200 and response.json().get("status") == "ok":
        return response.json().get("token")
    else:
        print("Login failed.")
        sys.exit(1)

def get_dhcp_scopes(base_url, token):
    response = requests.get(
        f"{base_url}/api/dhcp/scopes/list?token={token}"
    )
    response.raise_for_status()
    return response.json().get("response", [])

def delete_all_reservations(base_url, token, scope_name):
    reservations = get_reserved_leases(base_url, token, scope_name)
    for res in reservations:
        requests.get(
            f"{base_url}/api/dhcp/scopes/deleteReservedLease",
            params={
                "token": token,
                "name": scope_name,
                "ipAddress": res.get("ipAddress")
            }
        )
    print(f"Cleared all reservations in scope {scope_name}.")
    return reservations

def get_reserved_leases(base_url, token, scope_name):
    response = requests.get(
        f"{base_url}/api/dhcp/scopes/listReservedLeases",
        params={"token": token, "name": scope_name}
    )
    response.raise_for_status()
    return response.json().get("response", [])

def read_reservations(csv_path):
    reservations = []
    with open(csv_path.strip("'\""), 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            mac = row.get("MAC").strip().lower()
            ip = row.get("IP").strip()
            name = row.get("Name").strip()
            if mac and ip:
                reservations.append({
                    "hardwareAddress": mac,
                    "ipAddress": ip,
                    "hostName": name
                })
    return reservations

def add_reserved_lease(base_url, token, scope_name, lease):
    params = {
        "token": token,
        "name": scope_name,
        "hardwareAddress": lease["hardwareAddress"],
        "ipAddress": lease["ipAddress"],
        "hostName": lease["hostName"]
    }
    response = requests.get(f"{base_url}/api/dhcp/scopes/addReservedLease", params=params)
    return response.status_code == 200 and response.json().get("status") == "ok"

def main():
    print("Logging into Technitium DNS...")
    base_url = input("Enter Technitium DNS Base URL (e.g., http://192.168.1.120:5380): ").strip()
    username = input("Username: ").strip()
    password = getpass("Password: ")
    csv_path = input("Path to CSV file: ").strip()

    if not os.path.exists(csv_path.strip("'\"")):
        print(f"File not found: {csv_path}")
        sys.exit(1)

    token = login(base_url, username, password)

    scopes = get_dhcp_scopes(base_url, token)
    if not scopes:
        print("No DHCP scopes found.")
        sys.exit(1)

    print("\nAvailable DHCP Scopes:")
    for i, scope in enumerate(scopes, start=1):
        print(f"  [{i}] {scope['name']} ({scope['subnet']}/{scope['subnetMask']})")

    selected = int(input("Select a scope number to update: ").strip()) - 1
    scope = scopes[selected]
    scope_name = scope["name"]
    print(f"Selected Scope: {scope_name}")

    choice = input("Do you want to delete all existing reservations first? (yes/no): ").strip().lower()
    if choice == "yes":
        old_reservations = delete_all_reservations(base_url, token, scope_name)
        remaining = get_reserved_leases(base_url, token, scope_name)
        print(f"Reservation count after delete: {len(remaining)}")
    else:
        current = get_reserved_leases(base_url, token, scope_name)
        print(f"{len(current)} existing reservations will remain.")

    reservations = read_reservations(csv_path)
    print(f"Parsed {len(reservations)} valid reservations from CSV\n")

    print(f"Updating reservations in scope: {scope_name}")
    success = 0
    for res in reservations:
        if add_reserved_lease(base_url, token, scope_name, res):
            success += 1
        else:
            print(f"Failed: {res['hostName']} ({res['ipAddress']})")

    print(f"\nCompleted: {success}/{len(reservations)} reservations updated.")

if __name__ == "__main__":
    main()
