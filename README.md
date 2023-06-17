# IP2Geo

This is a Python script that uses the ip-api.com API to query a list of IP addresses and get the geolocation data for each IP. The information retrieved includes country, region, city, district, zip code, ISP, and more. The results are saved in a CSV file. API supports IPV4 and IPV6.

## Prerequisites

This script requires Python 3.6 or higher.

It also requires the following Python libraries:

* requests

You can install these libraries using pip:

```
pip install requests
```

## Usage

Before you run the script, you will need a text file containing the IP addresses you want to query, with one IP per line. You also need an API key from ip-api.com.

To run the script, navigate to the directory containing the script in your command prompt or terminal, and use the following command:

```
python IP2Geo.py -i INPUT -a APIKEY --csv OUTPUT
```

Replace INPUT with the path to your file containing IP addresses, APIKEY with your ip-api.com API key, and OUTPUT with the desired path for the output CSV file.

For example:
```
python IP2Geo.py -i ips.txt -a yourapikey --csv results.csv
```

This will start the script, which will query each IP address in the file and write the results to the specified CSV file. If an error occurs while querying an IP, the error will be printed to the console.
