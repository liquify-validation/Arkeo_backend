from flask_smorest import Blueprint, abort
from sqlalchemy import func
from API.network.models import Network
from flask import jsonify, request
from common.common import *
blp = Blueprint("network", __name__, description="Network API")

@blp.route('/block-time')
def providers():
    """
    Return the average blocktime sampled over the last 100 blocks
    ---
    tags:
      - Network
    responses:
      200:
        description: avg blocktime in seconds.
    """
    # Query all providers using SQLAlchemy
    services = Network.query.with_entities(Network.blockTime).all()

    # Extract bond values into a list
    service_values = [service[0] for service in services]  # Each bond is a tuple

    # Return the data as a JSON response
    return jsonify(service_values)

@blp.route('/height')
def providers():
    """
    Return the height our indexer is at
    ---
    tags:
      - Network
    responses:
      200:
        description: current indexer height
    """
    # Query all providers using SQLAlchemy
    services = Network.query.with_entities(Network.height).all()

    # Extract bond values into a list
    service_values = [service[0] for service in services]  # Each bond is a tuple

    # Return the data as a JSON response
    return jsonify(service_values)

@blp.route('/cahin-id-decode')
def get_chain_reverse_lookup():
    """
    Convert an arkeo chain ID's to human readable discription
    ---
    tags:
      - Network
    parameters:
      - name: chain
        in: query
        type: string
        required: true
        description: The chain ID to filter contracts by.
    responses:
      200:
        description: A JSON of all completed contracts for the specified chain on the network.
    """
    # Get the chain argument from the query string
    chain = request.args.get('chain')
    if not chain:
        return jsonify({"error": "Missing 'chain' query parameter"}), 400

    if int(chain) in ServiceReverseLookup:
        return jsonify(ServiceReverseLookup[int(chain)])
    else:
        return jsonify({"error": "chain ID not found"}), 400


@blp.route('/chain-list', methods=['GET'])
def get_service_reverse_lookup():
    """
    Return arkeo chain ID's to human readable discription
    ---
    tags:
      - Network
    responses:
      200:
        description: human readable chain list
    """
    return jsonify(ServiceReverseLookup)

@blp.route('/number-of-services')
def providers():
    """
    Return the number of services on the Arkeo network
    ---
    tags:
      - Network
    responses:
      200:
        description: number of services on the network.
    """
    # Query all providers using SQLAlchemy
    services = Network.query.with_entities(Network.number_of_services).all()

    # Extract bond values into a list
    service_values = [service[0] for service in services]  # Each bond is a tuple

    # Return the data as a JSON response
    return jsonify(service_values)

@blp.route('/number-of-providers')
def providers():
    """
    Return the number of providers on the Arkeo network
    ---
    tags:
      - Network
    responses:
      200:
        description: A JSON of all contracts on the network.
    """
    # Query all providers using SQLAlchemy
    providers = Network.query.with_entities(Network.number_of_providers).all()

    # Extract bond values into a list
    provider_values = [provider[0] for provider in providers]  # Each bond is a tuple

    # Return the data as a JSON response
    return jsonify(provider_values)

@blp.route('/bond')
def providers():
    """
    Return the total bond amount on the Arkeo network
    ---
    tags:
      - Network
    responses:
      200:
        description: A JSON of all contracts on the network.
    """
    # Query all providers using SQLAlchemy
    bonds = Network.query.with_entities(Network.bond).all()

    # Extract bond values into a list
    bond_values = [bond[0] for bond in bonds]  # Each bond is a tuple

    # Return the data as a JSON response
    return jsonify(bond_values)

@blp.route('/network')
def providers():
    """
    Grab a JSON of all contracts on the Arkeo network.
    ---
    tags:
      - Network
    responses:
      200:
        description: A JSON of all contracts on the network.
    """
    # Query all providers using SQLAlchemy
    network = Network.query.all()

    # Convert each network entry to a dictionary
    network_data = [entry.to_dict() for entry in network]

    # Return the data as a JSON response
    return jsonify(network_data)
    
@blp.route('/number-of-services-per-chain')
def get_service_counts():
    """
        Grab a JSON of the number of services per chain
        ---
        tags:
          - Network
        responses:
          200:
            description: A JSON of number of services per chain
    """
    service_counts = defaultdict(int)

    providers = Provider.query.all()

    for provider in providers:
        if provider.services:
            service_ids = provider.services.split(',')
            for service_id in service_ids:
                service_id = service_id.strip()
                if service_id.isdigit():
                    service_counts[int(service_id)] += 1

    # Build dict indexed by chain id
    result = {
        service_id: {
            "name": ServiceReverseLookup.get(service_id, "unknown"),
            "count": count
        }
        for service_id, count in sorted(service_counts.items())
    }

    return jsonify(result)