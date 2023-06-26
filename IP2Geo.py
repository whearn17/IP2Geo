import ipaddress
import argparse
import csv
import requests
import concurrent.futures
import os
import json

FIELDS = ['query', 'country', 'regionName', 'city', 'district', 'zip', 'isp', 'org', 'as',
          'mobile', 'proxy', 'status', 'message']

CONFIG_FILE = 'config.json'


def read_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('api_key', '')
    except FileNotFoundError:
        print(f"Config file {CONFIG_FILE} not found.")
        return None


def query_ip(ip, api_key):
    try:
        response = requests.get(f'https://pro.ip-api.com/json/{ip}?fields={",".join(FIELDS)}&key={api_key}', timeout=5)
        data = response.json()

        data = {field: data.get(field, '') for field in FIELDS}

        return data
    except requests.exceptions.RequestException as e:
        print(f"Error querying {ip}: {e}")
        return None


def write_to_csv(data, writer):
    if data is not None:
        writer.writerow(data)


def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="File containing IPs to query")
    args = parser.parse_args()

    api_key = read_config()
    if not api_key:
        return

    try:
        with open(args.input, 'r') as f:
            ips = f.read().splitlines()
    except FileNotFoundError:
        print(f"Input file {args.input} not found.")
        return

    # Validate the IPs here and remove the invalid ones
    ips = [ip for ip in ips if is_valid_ip(ip)]
    if len(ips) == 0:
        print("No valid IP addresses found.")
        return

    output_file = os.path.splitext(args.input)[0] + ".csv"
    with concurrent.futures.ThreadPoolExecutor() as executor, open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        future_to_ip = {executor.submit(query_ip, ip, api_key): ip for ip in ips}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f"{ip} generated an exception: {exc}")
            else:
                write_to_csv(data, writer)


if __name__ == '__main__':
    main()
