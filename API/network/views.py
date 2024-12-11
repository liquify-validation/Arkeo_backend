from flask_smorest import Blueprint, abort
from sqlalchemy import func
from API.network.models import Network
from flask import jsonify, request
from common.common import *
blp = Blueprint("network", __name__, description="Network API")

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