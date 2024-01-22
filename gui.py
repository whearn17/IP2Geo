import logging

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QMessageBox, QWidget, QPlainTextEdit
from PyQt5.QtGui import QIcon
import pyperclip
import concurrent.futures

from api_queries import read_config, is_valid_ip, query_ip

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


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.api_key = read_config()

        self.setStyleSheet(DARK_STYLE)
        self.setWindowTitle('IP2Geo')
        self.setWindowIcon(QIcon('window_icon.ico'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        lay = QVBoxLayout(self.central_widget)

        self.ip_textbox = QPlainTextEdit(self)
        self.ip_textbox.setLineWrapMode(QPlainTextEdit.NoWrap)
        # self.ip_textbox.setAcceptRichText(False)
        lay.addWidget(self.ip_textbox)

        self.lookup_button = QPushButton('Lookup IPs', self)
        self.lookup_button.clicked.connect(self.lookup_ips)
        lay.addWidget(self.lookup_button)

        self.setFixedSize(500, 500)

        self.results = []
        self.valid_ips = []
        self.cache = {}

        # Setting up logging
        logging.basicConfig(level=logging.INFO)

    def lookup_ips(self):
        ips_text = self.ip_textbox.toPlainText()
        ips = ips_text.split('\n')

        # Creating a set of unique IPs to look up
        unique_ips = set([ip for ip in ips if is_valid_ip(ip.strip())])

        self.results = [''] * len(ips)

        # Cache check
        to_lookup_ips = []
        for i, ip in enumerate(unique_ips):
            if ip not in self.cache:
                to_lookup_ips.append((i, ip))
            else:
                logging.info(f"IP {ip} found in cache")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {}

            for i, ip in to_lookup_ips:
                future = executor.submit(query_ip, ip, self.api_key)
                futures[future] = (i, ip)  # Store the ip along with the index

            for future in concurrent.futures.as_completed(futures):
                i, ip = futures[future]  # Extract the index and ip
                try:
                    data = future.result()
                    if data and data.get('status') == 'success':
                        result = "\t".join([data.get('country', ''), data.get('regionName', ''), data.get('isp', ''),
                                            str(data.get('proxy', ''))])
                        self.cache[ip] = result  # Add to cache
                        logging.info(f"Added {ip} to cache")
                except Exception as e:
                    logging.error(f"Error in thread: {e}")

            logging.info(f"Cache size: {len(self.cache)}")

        # Populate the results list based on the original ip list and the cache
        for i, ip in enumerate(ips):
            if ip in self.cache:
                self.results[i] = self.cache[ip]

        # Adding the column headers
        headers = ["Country", "Region", "ISP", "IsProxy"]
        result_string = "\t".join(headers) + '\n' + '\n'.join(self.results)

        # Remove last newline if the last result is an empty string
        if self.results[-1] == '':
            result_string = result_string[:-1]

        pyperclip.copy(result_string)
        QMessageBox.information(self, 'Copied to clipboard', 'The results have been copied to your clipboard.')
