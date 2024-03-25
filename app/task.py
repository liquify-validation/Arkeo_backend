from app import scheduler
import requests
import json
from config import Config
from database.db_common import *
from requests.exceptions import Timeout
import tldextract

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


def make_query(type, path):
    base_paths = {
        "api": Config.API,
        "rpc": Config.RPC
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


def grab_provider(provider):
    provider_name = extract_main_domain(provider[0]["metadata_uri"])
    if provider_name == '':
        return None
    base_url = provider[0]["metadata_uri"][:provider[0]["metadata_uri"].rfind('/')]

    dict_of_dicts = {}

    for d in provider:
        service_string = base_url + "/" + ServiceReverseLookup[d["service"]]
        dict_of_dicts[service_string] = d

    provider_data = {
        provider_name: {
            "meta_data_accessible": 0,
            "description": "UNKNOWN",
            "website": "UNKNOWN",
            "location": "UNKNOWN",
            "free_tier_rate_limit": 0,
            "provider_pubkey": "",
            "endpoints": dict_of_dicts,
            "contracts": {},
            "number_of_services": len(provider),
            "services": [endpoint['service'] for endpoint in provider],
            "offline_reason": "N/A"
        }
    }

    try:
        response_API = requests.get(provider[0]["metadata_uri"], timeout=3)
        if response_API.status_code == 200:
            data = response_API.json().get("config", {})
            provider_data[provider_name].update({
                "website": data.get("website", ""),
                "description": data.get("description", ""),
                "location": data.get("location", ""),
                "free_tier_rate_limit": data.get("free_tier_rate_limit", 0),
                "provider_pubkey": data.get("provider_pubkey", ""),
                "meta_data_accessible": 1
            })
    except requests.exceptions.RequestException as e:
        provider_data[provider_name]["meta_data_accessible"] = 0
        provider_data[provider_name]["offline_reason"] = "Metadata not accessible"
        print("Timeout error: The request timed out.")

    query = "INSERT INTO Arkeo.providers (provider_name, meta_data_accessible, description, website, " \
            "location, free_tier_rate_limit, provider_pubkey, endpoints, contracts,number_of_services, " \
            "services, offline_reason) VALUES ('{provider_name}', '{meta_data_accessible}','{description}','{website}'," \
            "'{location}','{free_tier_rate_limit}','{provider_pubkey}','{endpoints}','{contracts}'," \
            "'{number_of_services}','{services}', '{offline_reason}')".format(provider_name=provider_name,
                                                                              meta_data_accessible=
                                                                              provider_data[provider_name][
                                                                                  "meta_data_accessible"],
                                                                              description=provider_data[provider_name][
                                                                                  "description"],
                                                                              website=provider_data[provider_name][
                                                                                  "website"],
                                                                              location=provider_data[provider_name][
                                                                                  "location"],
                                                                              free_tier_rate_limit=
                                                                              provider_data[provider_name][
                                                                                  "free_tier_rate_limit"],
                                                                              provider_pubkey=
                                                                              provider_data[provider_name][
                                                                                  "provider_pubkey"],
                                                                              endpoints=json.dumps(
                                                                                  provider_data[provider_name][
                                                                                      "endpoints"]),
                                                                              contracts=json.dumps(
                                                                                  provider_data[provider_name][
                                                                                      "contracts"]),
                                                                              number_of_services=
                                                                              provider_data[provider_name][
                                                                                  "number_of_services"],
                                                                              services=provider_data[provider_name][
                                                                                  "services"],
                                                                              offline_reason=
                                                                              provider_data[provider_name][
                                                                                  "offline_reason"])
    commitQuery(query)

    return provider_data


@scheduler.task('interval', id='grab_providers', seconds=6000000)
def grab_providers():
    # Your code to update the database
    providers = make_query("api", "/arkeo/providers")['provider']

    indexed_by_provider = {}

    # Iterate over the original dictionary
    for item in providers:
        metadata_name = item["metadata_uri"]
        if metadata_name not in indexed_by_provider:
            indexed_by_provider[metadata_name] = []
        indexed_by_provider[metadata_name].append(item)

    provider_data = {}

    for provider in indexed_by_provider:
        data = grab_provider(indexed_by_provider[provider])
        if data != None:
            provider_data = {**provider_data, **data}

    # Print the new dictionary
    print(indexed_by_provider)

    print(providers)
    test = 1
