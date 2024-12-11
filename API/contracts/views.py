from flask_smorest import Blueprint, abort
from sqlalchemy import func
from API.contracts.models import Contract
from flask import jsonify, request

blp = Blueprint("contracts", __name__, description="Contracts API")

@blp.route('/client')
def providers():
    """
    Grab a JSON of all contracts for a specific client on the Arkeo network.
    ---
    tags:
      - Contracts
    parameters:
      - name: client
        in: query
        type: string
        required: true
        description: The provider to filter contracts by.
    responses:
      200:
        description: A JSON of all completed contracts for the specified chain on the network.
    """
    # Get the chain argument from the query string
    client = request.args.get('client')
    if not client:
        return jsonify({"error": "Missing 'client' query parameter"}), 400

    # Query completed contracts for the specified chain
    contracts = Contract.query.filter_by(provider=client).all()

    # Convert the contracts to a dictionary
    dict_of_dicts = {contract.id: contract.to_dict() for contract in contracts}

    # Return the data as a JSON response
    return jsonify(dict_of_dicts)

@blp.route('/provider')
def providers():
    """
    Grab a JSON of all contracts for a specific provider on the Arkeo network.
    ---
    tags:
      - Contracts
    parameters:
      - name: provider
        in: query
        type: string
        required: true
        description: The provider to filter contracts by.
    responses:
      200:
        description: A JSON of all completed contracts for the specified chain on the network.
    """
    # Get the chain argument from the query string
    provider = request.args.get('provider')
    if not provider:
        return jsonify({"error": "Missing 'provider' query parameter"}), 400

    # Query completed contracts for the specified chain
    contracts = Contract.query.filter_by(provider=provider).all()

    # Convert the contracts to a dictionary
    dict_of_dicts = {contract.id: contract.to_dict() for contract in contracts}

    # Return the data as a JSON response
    return jsonify(dict_of_dicts)

@blp.route('/chain')
def providers():
    """
    Grab a JSON of all completed contracts for a specific chain on the Arkeo network.
    ---
    tags:
      - Contracts
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

    # Query completed contracts for the specified chain
    contracts = Contract.query.filter_by(service=int(chain)).all()

    # Convert the contracts to a dictionary
    dict_of_dicts = {contract.id: contract.to_dict() for contract in contracts}

    # Return the data as a JSON response
    return jsonify(dict_of_dicts)

@blp.route('/completed')
def providers():
    """
    Grab a JSON of all completed contracts on the Arkeo network.
    ---
    tags:
      - Contracts
    responses:
      200:
        description: A JSON of all contracts on the network.
    """
    # Query all providers using SQLAlchemy
    contracts = Contract.query.filter_by(completed=True).all()

    # Convert the providers to a dictionary
    dict_of_dicts = {contract.id: contract.to_dict() for contract in contracts}

    # Return the data as a JSON response
    return jsonify(dict_of_dicts)

@blp.route('/active')
def providers():
    """
    Grab a JSON of all active contracts on the Arkeo network.
    ---
    tags:
      - Contracts
    responses:
      200:
        description: A JSON of all contracts on the network.
    """
    # Query all providers using SQLAlchemy
    contracts = Contract.query.filter_by(completed=False).all()

    # Convert the providers to a dictionary
    dict_of_dicts = {contract.id: contract.to_dict() for contract in contracts}

    # Return the data as a JSON response
    return jsonify(dict_of_dicts)

@blp.route('/contracts')
def providers():
    """
    Grab a JSON of all contracts on the Arkeo network.
    ---
    tags:
      - Contracts
    responses:
      200:
        description: A JSON of all contracts on the network.
    """
    # Query all providers using SQLAlchemy
    contracts = Contract.query.all()

    # Convert the providers to a dictionary
    dict_of_dicts = {contract.id: contract.to_dict() for contract in contracts}

    # Return the data as a JSON response
    return jsonify(dict_of_dicts)