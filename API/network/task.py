from API.network.models import Network
from API.providers.models import Provider
from DB import db
from common.common import *
from flask import Flask
import datetime

def getBlockTime():
    status = make_query("api", "/cosmos/base/node/v1beta1/status")
    height = status['height']
    offsetStatus = make_query("api", "/cosmos/base/tendermint/v1beta1/blocks/" + str(int(height)-100))
    bt1 = status["timestamp"]
    bt2 = offsetStatus["block"]["header"]["time"]
    date_format = datetime.datetime.strptime(bt1.split('.', 1)[0] + 'Z', "%Y-%m-%dT%H:%M:%SZ")
    bt1_unix = datetime.datetime.timestamp(date_format)
    date_format = datetime.datetime.strptime(bt2.split('.', 1)[0] + 'Z', "%Y-%m-%dT%H:%M:%SZ")
    bt2_unix = datetime.datetime.timestamp(date_format)
    diff = bt1_unix - bt2_unix
    avgBlock = str(diff / 100)
    return {"height": height, "avgBlockTime": float(avgBlock)}
    test = 1

def grab_network_stats(app: Flask):
    with app.app_context():
        """
            Fetches network statistics and updates the Network table using Flask SQLAlchemy.
            """
        # Fetch providers data
        times = getBlockTime()
        providers = make_query("api", "/arkeo/providers")['provider']
        number_of_contracts = len(make_query("api", "/arkeo/contracts")['contract'])
        # Calculate total bond
        bond = sum(int(item["bond"]) for item in providers)

        # Query database for number of providers
        providers_from_db = Provider.query.all()
        num_providers = len(providers_from_db)

        # Extract all services from providers
        chains = []  # This will hold all services
        unique_services = set()  # To track unique services
        total_services = 0  # To count total services

        for provider in providers_from_db:
            services = provider.services
            if services:
                try:
                    parsed_services = json.loads(services)
                    if isinstance(parsed_services, list):
                        chains.extend(parsed_services)
                        total_services += len(parsed_services)
                        unique_services.update(parsed_services)
                    else:
                        chains.append(parsed_services)
                        total_services += 1
                        unique_services.add(parsed_services)
                except (ValueError, TypeError):
                    # Fall back to comma-separated parsing
                    split_services = [s.strip() for s in services.split(',') if s.strip()]
                    chains.extend(split_services)
                    total_services += len(split_services)
                    unique_services.update(split_services)

        print("Total services:", total_services)
        print("Unique services:", len(unique_services))

        num_services = total_services

        # Check if an entry exists in the Network table
        network_entry = Network.query.first()

        if network_entry:
            # Update the existing entry
            network_entry.bond = bond
            network_entry.number_of_providers = num_providers
            network_entry.number_of_services = num_services
            network_entry.number_of_contracts = number_of_contracts
            network_entry.number_of_chains = len(unique_services)
            network_entry.height = times["height"]
            network_entry.blockTime = times["avgBlockTime"]
        else:
            # Create a new entry if none exists
            new_network = Network(
                bond=bond,
                number_of_providers=num_providers,
                number_of_services=num_services,
                number_of_contracts=number_of_contracts,
                number_of_chains=len(unique_services),
                height=times["height"],
                blockTime=times["avgBlockTime"]
            )
            db.session.add(new_network)

        # Commit the changes
        try:
            db.session.commit()
            print("Network stats successfully updated.")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to update network stats: {e}")