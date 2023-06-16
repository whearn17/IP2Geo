import requests
import json
import csv
import argparse
import concurrent.futures

FIELDS = ['status', 'message', 'country', 'regionName', 'city', 'district', 'zip', 'isp', 'org', 'as', 'mobile', 'proxy', 'query']

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="File containing IPs to query")
    parser.add_argument("--csv", required=True, help="CSV file to output results")
    parser.add_argument("-a", "--api", required=True, help="API key for IP query")
    args = parser.parse_args()

    try:
        with open(args.input, 'r') as f:
            ips = f.read().splitlines()
    except FileNotFoundError:
        print(f"Input file {args.input} not found.")
        return

    with concurrent.futures.ThreadPoolExecutor() as executor, open(args.csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        future_to_ip = {executor.submit(query_ip, ip, args.api): ip for ip in ips}
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
