from API.network.models import Network, Nonce
from API.providers.models import Provider
from DB import db
from common.common import *
from flask import Flask

def grab_nonce_counter(app: Flask):
    with app.app_context():
        status = make_query("api", "/cosmos/base/node/v1beta1/status")
        height = int(status["height"])
        timestamp = convert_to_mysql_timestamp(status["timestamp"])

        contracts = make_query("api", "/arkeo/contracts")['contract']
        nonceTotal = 0

        for contract_data in contracts:
            nonce = int(contract_data['nonce']) if contract_data['nonce'] else 0
            nonceTotal += nonce

        existing_nonce = Nonce.query.get(height)

        if existing_nonce:
            # Update existing nonce entry
            existing_nonce.nonceCount = nonceTotal
            existing_nonce.timestamp = timestamp  # Update timestamp
        else:
            # Create a new nonce entry
            new_nonce = Nonce(
                blockHeight=height,
                nonceCount=nonceTotal,
                timestamp=timestamp
            )
            db.session.add(new_nonce)

        # Commit the changes
        try:
            db.session.commit()
            print("Network stats successfully updated.")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to update network stats: {e}")



def grab_network_stats(app: Flask):
    with app.app_context():
        """
            Fetches network statistics and updates the Network table using Flask SQLAlchemy.
            """
        # Fetch providers data
        providers = make_query("api", "/arkeo/providers")['provider']
        number_of_contracts = len(make_query("api", "/arkeo/contracts")['contract'])
        # Calculate total bond
        bond = sum(int(item["bond"]) for item in providers)

        # Query database for number of providers
        providers_from_db = Provider.query.all()
        num_providers = len(providers_from_db)

        # Extract all services from providers
        chains = []
        for provider in providers_from_db:
            services = provider.services
            if services:
                try:
                    # Try to parse services as JSON
                    parsed_services = json.loads(services)
                    if isinstance(parsed_services, list):
                        chains.extend(parsed_services)
                    else:
                        # If parsed result is not a list, treat it as a single service
                        chains.append(parsed_services)
                except (ValueError, TypeError):
                    # If JSON parsing fails, treat it as a single service string
                    chains.append(services)

        num_services = len(chains)

        # Check if an entry exists in the Network table
        network_entry = Network.query.first()

        if network_entry:
            # Update the existing entry
            network_entry.bond = bond
            network_entry.number_of_providers = num_providers
            network_entry.number_of_services = num_services
            network_entry.number_of_contracts = number_of_contracts
        else:
            # Create a new entry if none exists
            new_network = Network(
                bond=bond,
                number_of_providers=num_providers,
                number_of_services=num_services,
                number_of_contracts=number_of_contracts
            )
            db.session.add(new_network)

        # Commit the changes
        try:
            db.session.commit()
            print("Network stats successfully updated.")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to update network stats: {e}")