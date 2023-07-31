import ipaddress
import requests
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


def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
