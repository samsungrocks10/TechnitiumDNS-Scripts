# Technitium DHCP Reservation Import Script

This Python script imports static DHCP reservations into your [Technitium DNS Server](https://technitium.com/dns/) using its REST API. It lets you interactively select a DHCP scope, optionally purge existing reservations, and import new ones from a CSV file.

---

## Features

- Interactive prompts for URL, username, password, CSV path, and scope
- Automatically lists all available DHCP scopes
- Optionally delete all existing reservations in a scope
- Validates and imports MAC/IP/name entries from CSV
- Uses Technitium's `/set` endpoint to fully overwrite reservation lists
- Prints before/after reservation counts for GUI verification

---

## Requirements

- Python 3.x
- No external dependencies (only uses standard `requests`, `csv`, `getpass`)

---

## CSV Format

The CSV must contain three headers (case-insensitive):

```csv
MAC,IP,Name
AA:BB:CC:DD:EE:FF,192.168.11.1,HomeAssistant
11:22:33:44:55:66,192.168.11.11,Proxmox
```

- **MAC** – Colon-separated MAC address
- **IP** – IP address within the selected scope’s subnet
- **Name** – Hostname or friendly description

Invalid or incomplete rows (e.g., missing MAC address) are skipped.

---

## How to Use

1. **Run the Script**
   ```bash
   python3 dns_import_csv.py
   ```

2. **Follow the Prompts**
   - Enter the Technitium DNS API URL (e.g., `http://192.168.x.x:5380`)
   - Provide your admin username and password
   - Provide full path to your reservations CSV file
   - Select the DHCP scope from the presented list
   - Choose whether to delete all existing reservations first
   - Review how many reservations were parsed and updated

3. **Example Output**
   ```
   Enter Technitium DNS Base URL: http://192.168.x.x:5380
   Username: admin
   Password:
   Path to CSV file: /path/tp/reservations.csv

   Available DHCP Scopes:
     [1] TestScope1 (192.168.1.0/255.255.255.0)
     [2] TestScope-IoT (192.168.40.0/255.255.255.0)
   Select a scope number to update: 1
   Do you want to delete all existing reservations first? (yes/no): yes

   Cleared all reservations in scope TestScope1
   Parsed 47 valid reservations from CSV
   Updated 47 reservations in scope TestScope1
   Post-update reservation count: 47
   ```

---

## API References

- POST `/api/user/login`
- POST `/api/dhcp/scopes/list`
- POST `/api/dhcp/scopes/get`
- POST `/api/dhcp/scopes/set`

For full API details, see: [Technitium DNS Server API Documentation](https://technitium.com/dns/)
