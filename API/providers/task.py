import requests
import json
from config import config
from requests.exceptions import Timeout
import tldextract
import socket
import ipaddress
import time
from API.providers.models import Provider
from DB import db
from common.common import *
from flask import current_app, Flask

def grab_provider(provider):
    provider_name = extract_main_domain(provider[0]["metadata_uri"])
    if provider_name == '':
        return None

    base_url = provider[0]["metadata_uri"][:provider[0]["metadata_uri"].rfind('/')]
    ip_addr = get_ip_address(base_url.replace("https://", "").replace("http://", ""))

    dict_of_dicts = {}
    for d in provider:
        service_string = base_url + "/" + ServiceReverseLookup[d["service"]]
        dict_of_dicts[service_string] = d

    # Default IP-related fields
    ip_dict = {
        'city': "UNKNOWN",
        'isp': "UNKNOWN",
        'country': "UNKNOWN",
        'countryCode': "UNKNOWN",
        'query': "UNKNOWN"
    }

    # Fetch IP information
    if ip_addr:
        response_code = 0
        while response_code != 200:
            response = requests.get(f"http://ip-api.com/json/{ip_addr}")
            response_code = response.status_code
            if response_code == 429:
                print("Rate limited, wait 60 seconds")
                time.sleep(60)
            elif response_code == 200:
                ip_dict = response.json()
    else:
        print("IP address is not available; defaulting to UNKNOWN values.")

    # Initialize provider data with defaults
    provider_data = {
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
        "offline_reason": "N/A",
        "isp": ip_dict,
        "provider_name": provider_name,
        "provider_pubkey": provider[0]['pub_key'],
        "status": "ONLINE"
    }

    # Try to fetch metadata from the provider's metadata_uri
    try:
        response_API = requests.get(provider[0]["metadata_uri"], timeout=3)
        if response_API.status_code == 200:
            data = response_API.json().get("config", {})
            provider_data.update({
                "website": data.get("website", ""),
                "description": data.get("description", ""),
                "location": data.get("location", ""),
                "free_tier_rate_limit": data.get("free_tier_rate_limit", 0),
                "meta_data_accessible": 1,
                "provider_name": data.get("moniker", "") if is_ip_address(provider_name) else provider_name
            })
    except requests.exceptions.RequestException:
        provider_data["meta_data_accessible"] = 0
        provider_data["offline_reason"] = "Metadata not accessible"
        provider_data["status"] = "OFFLINE"
        print("Timeout error: The request timed out.")

    # Check if provider already exists in the database
    existing_provider = Provider.query.filter_by(ip_addr=ip_addr).first()

    if existing_provider:
        # Update existing fields
        existing_provider.meta_data_accessible = provider_data["meta_data_accessible"]
        existing_provider.description = provider_data["description"]
        existing_provider.website = provider_data["website"]
        existing_provider.location = provider_data["location"]
        existing_provider.free_tier_rate_limit = provider_data["free_tier_rate_limit"]
        existing_provider.provider_pubkey = provider_data["provider_pubkey"]
        existing_provider.endpoints = json.dumps(provider_data["endpoints"])
        existing_provider.contracts = json.dumps(provider_data["contracts"])
        existing_provider.number_of_services = provider_data["number_of_services"]
        existing_provider.services = ",".join(map(str, provider_data["services"]))
        existing_provider.offline_reason = provider_data["offline_reason"]
        existing_provider.isp = ip_dict.get('isp', 'UNKNOWN')
        existing_provider.isp_country = ip_dict.get('country', 'UNKNOWN')
        existing_provider.ip_addr = ip_dict.get('query', 'UNKNOWN')
        existing_provider.provider_name = provider_data["provider_name"]
        existing_provider.status = provider_data["status"]

        print(f"Provider {provider_name} updated successfully.")
    else:
        # Insert new provider
        new_provider = Provider(
            provider_name=provider_data["provider_name"],
            meta_data_accessible=provider_data["meta_data_accessible"],
            description=provider_data["description"],
            website=provider_data["website"],
            location=provider_data["location"],
            free_tier_rate_limit=provider_data["free_tier_rate_limit"],
            provider_pubkey=provider_data["provider_pubkey"],
            endpoints=json.dumps(provider_data["endpoints"]),
            contracts=json.dumps(provider_data["contracts"]),
            number_of_services=provider_data["number_of_services"],
            services=",".join(map(str, provider_data["services"])),
            offline_reason=provider_data["offline_reason"],
            isp=ip_dict.get('isp', 'UNKNOWN'),
            isp_country=ip_dict.get('country', 'UNKNOWN'),
            ip_addr=ip_dict.get('query', 'UNKNOWN'),
            status=provider_data["status"]
        )
        db.session.add(new_provider)
        print(f"Provider {provider_name} added successfully.")

    # Commit changes to the database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving provider {provider_name}: {e}")

    return provider_data

def grab_providers(app: Flask):
    with app.app_context():
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

# def grab_network_stats():
#     providers = make_query("api", "/arkeo/providers")['provider']
#     bond = 0
#
#     for item in providers:
#         bond += int(item["bond"])
#
#     proivders = (grabQuery('SELECT * FROM Arkeo.providers'))
#     numProvider = len(proivders)
#     chains = []
#
#     for key in proivders:
#         chains.extend(json.loads(key['services']))
#
#     numServices = len(chains)
#
#     query = "INSERT INTO Arkeo.network (bond, number_of_providers, number_of_services) VALUES ('{bond}', '{number_of_providers}','{number_of_services}')".format(
#         bond=bond,
#         number_of_providers=numProvider,
#         number_of_services=numServices)
#
#     commitQuery(query)
#
#     test = 1