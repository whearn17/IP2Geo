from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTextEdit, QPushButton, QMessageBox, QWidget
from PyQt5.QtGui import QIcon
import ipaddress
import requests
import json
import pyperclip
import sys

FIELDS = ['query', 'country', 'regionName', 'city', 'district', 'zip', 'isp', 'org', 'as',
          'mobile', 'proxy', 'status', 'message']

CONFIG_FILE = 'config.json'

DARK_STYLE = """
    QWidget {
        background-color: #303030;
        color: #fff;
    }

    QPushButton {
        background-color: #505050;
        border: 1px solid #303030;
    }

    QPushButton:hover {
        border: 1px solid #fff;
    }

    QTextEdit {
        border: 2px solid #505050;
        padding: 10px;
        background-color: #303030;
        color: #fff;
    }
"""


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


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.api_key = read_config()

        self.setStyleSheet(DARK_STYLE)
        self.setWindowTitle('IP2Geo')
        self.setWindowIcon(QIcon('window_icon.png'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        lay = QVBoxLayout(self.central_widget)

        self.ip_textbox = QTextEdit(self)
        self.ip_textbox.setLineWrapMode(QTextEdit.NoWrap)
        lay.addWidget(self.ip_textbox)

        self.lookup_button = QPushButton('Lookup IPs', self)
        self.lookup_button.clicked.connect(self.lookup_ips)
        lay.addWidget(self.lookup_button)

        self.setGeometry(100, 100, 500, 500)

    def lookup_ips(self):
        ips_text = self.ip_textbox.toPlainText().lstrip()  # Remove leading newline characters
        ips = ips_text.split('\n')  # Split the input by line

        results_cache = dict()  # Create a cache to store results of previous lookups

        # Store results as list of strings to join later
        results = [''] * len(ips)  # Initialize a list with the same length as the input, filled with empty strings

        for i, ip in enumerate(ips):
            if is_valid_ip(ip.strip()):  # We also strip each line to remove leading/trailing whitespaces
                # Check the cache first
                if ip in results_cache:
                    results[i] = results_cache[ip]
                else:
                    data = query_ip(ip, self.api_key)
                    if data and data.get('status') == 'success':
                        result = "\t".join([data.get('country', ''), data.get('regionName', ''), data.get('isp', ''),
                                            str(data.get('proxy', ''))])
                        results[i] = result
                        results_cache[ip] = result  # Add to cache

        if not results:
            QMessageBox.information(self, 'No results', 'No IP addresses were provided.')
            return

        result_string = '\n'.join(results)
        pyperclip.copy(result_string)
        QMessageBox.information(self, 'Copied to clipboard', 'The results have been copied to your clipboard.')


def main():
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
