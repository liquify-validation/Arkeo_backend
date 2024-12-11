import requests
import json
from config import config
import tldextract
import socket
import ipaddress
from datetime import datetime

ServiceReverseLookup = {
    0: "unknown",
    1: "mock",
    2: "arkeo-mainnet-fullnode",
    3: "avax-mainnet-fullnode",
    4: "avax-mainnet-archivenode",
    5: "bch-mainnet-fullnode",
    6: "bch-mainnet-lightnode",
    7: "bnb-mainnet-fullnode",
    8: "bsc-mainnet-fullnode",
    9: "bsc-mainnet-archivenode",
    10: "btc-mainnet-fullnode",
    11: "btc-mainnet-lightnode",
    12: "cardano-mainnet-relaynode",
    13: "gaia-mainnet-rpc",
    14: "doge-mainnet-fullnode",
    15: "doge-mainnet-lightnode",
    16: "etc-mainnet-archivenode",
    17: "etc-mainnet-fullnode",
    18: "etc-mainnet-lightnode",
    19: "eth-mainnet-archivenode",
    20: "eth-mainnet-fullnode",
    21: "eth-mainnet-lightnode",
    22: "ltc-mainnet-fullnode",
    23: "ltc-mainnet-lightnode",
    24: "optimism-mainnet-fullnode",
    25: "osmosis-mainnet-fullnode",
    26: "polkadot-mainnet-fullnode",
    27: "polkadot-mainnet-lightnode",
    28: "polkadot-mainnet-archivenode",
    29: "polygon-mainnet-fullnode",
    30: "polygon-mainnet-archivenode",
    31: "sol-mainnet-fullnode",
    32: "thorchain-mainnet-fullnode",
    33: "bch-mainnet-unchained",
    34: "btc-mainnet-unchained",
    35: "bnb-mainnet-unchained",
    36: "bsc-mainnet-unchained",
    37: "bsc-mainnet-unchained",
    38: "gaia-mainnet-unchained",
    39: "doge-mainnet-unchained",
    40: "eth-mainnet-unchained",
    41: "avax-mainnet-unchained",
    42: "ltc-mainnet-unchained",
    43: "osmosis-mainnet-unchained",
    44: "thorchain-mainnet-unchained",
    45: "optimism-mainnet-unchained",
    46: "gaia-mainnet-grpc",
    47: "btc-mainnet-blockbook",
    48: "ltc-mainnet-blockbook",
    49: "bch-mainnet-blockbook",
    50: "doge-mainnet-blockbook"
}


def convert_to_mysql_timestamp(timestamp):
    # Remove the 'Z' at the end (UTC indicator)
    timestamp = timestamp.rstrip('Z')

    # Truncate the fractional seconds to microseconds (6 digits)
    if '.' in timestamp:
        # Split the timestamp into the date-time part and the fractional part
        date_time_part, fractional_part = timestamp.split('.')

        # Truncate or pad the fractional part to exactly 6 digits
        fractional_part = (fractional_part + '000000')[:6]  # Truncate or pad to 6 digits

        # Reconstruct the timestamp with the truncated microseconds
        timestamp = f"{date_time_part}.{fractional_part}"

    # Parse the timestamp into a datetime object
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")

    # Return the datetime object
    return dt

def strip_port_from_url(url):
    parts = url.split(':')
    if len(parts) > 1 and parts[-1].isdigit():
        # If there are more than two parts and the last part is a number (port number)
        return ':'.join(parts[:-1])
    else:
        # Otherwise, return the original URL
        return url

def get_ip_address(address):
    address = address.split("/")[0]
    address = strip_port_from_url(address)
    try:
        # Check if the input is an IP address
        ip = ipaddress.ip_address(address)
        return str(ip)

    except ValueError:
        try:
            # Attempt DNS resolution if it's not an IP address
            ip_address = socket.gethostbyname(address)
            return ip_address
        except socket.error as e:
            print(f"Error: {e}")
            return None

def make_query(type, path):
    base_paths = {
        "api": config.Config.API,
        "rpc": config.Config.RPC
    }

    base_path = base_paths.get(type)
    if base_path is None:
        raise ValueError("Type not recognized")

    for bp in base_path:
        response_API = requests.get(bp + path)
        if response_API.status_code == 200:
            break
    else:
        raise ValueError("None of the base paths returned a successful response")

    data = json.loads(response_API.text)
    return data

def extract_main_domain(url):
    ext = tldextract.extract(url)
    return '.'.join([ext.domain])

def is_ip_address(value):
    try:
        # Try to create an IP address object
        ipaddress.ip_address(value)
        return True
    except ValueError:
        # If it raises a ValueError, it's not a valid IP address
        return False