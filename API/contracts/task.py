from API.contracts.models import Contract
from DB import db
from common.common import *
from flask import Flask

def store_or_update_contracts_in_db(contracts):
    """
    Stores or updates a list of contracts in the database.

    :param contracts: List of contract dictionaries.
    """
    status = make_query("api", "/cosmos/base/node/v1beta1/status")
    height = status['height']

    for contract_data in contracts:
        try:
            # Check if a contract with the same ID already exists
            existing_contract = Contract.query.get(int(contract_data['id']))

            if existing_contract:
                # Update existing contract
                existing_contract.provider = contract_data['provider']
                existing_contract.service = int(contract_data['service'])
                existing_contract.client = contract_data['client']
                existing_contract.type = contract_data.get('type', None)
                existing_contract.height = int(contract_data['height'])
                existing_contract.duration = int(contract_data['duration']) if contract_data['duration'] else None
                existing_contract.rate = str(contract_data['rate'])  # Convert rate to string
                existing_contract.deposit = int(contract_data['deposit']) if contract_data['deposit'] else None
                existing_contract.paid = int(contract_data['paid']) if contract_data['paid'] else None
                existing_contract.settlement_height = int(contract_data['settlement_height']) if contract_data[
                    'settlement_height'] else None
                existing_contract.completed = 1 if (int(height) > int(contract_data['settlement_height'])) else 0
                existing_contract.queries_per_minute = int(contract_data['queries_per_minute']) if contract_data[
                    'queries_per_minute'] else None
                existing_contract.nonce = int(contract_data['nonce']) if contract_data['nonce'] else None
                existing_contract.authorization = contract_data.get('authorization', None)
                existing_contract.remaining = int(contract_data['settlement_height']) - int(height) if (int(height) < int(contract_data['settlement_height'])) else 0
            else:
                # Create a new contract if no existing entry
                new_contract = Contract(
                    id=int(contract_data['id']),
                    provider=contract_data['provider'],
                    service=int(contract_data['service']),
                    client=contract_data['client'],
                    type=contract_data.get('type', None),
                    height=int(contract_data['height']),
                    duration=int(contract_data['duration']) if contract_data['duration'] else None,
                    rate=str(contract_data['rate']),
                    deposit=int(contract_data['deposit']) if contract_data['deposit'] else None,
                    paid=int(contract_data['paid']) if contract_data['paid'] else None,
                    settlement_height=int(contract_data['settlement_height']) if contract_data[
                        'settlement_height'] else None,
                    completed=1 if (int(height) > int(contract_data['settlement_height'])) else 0,
                    queries_per_minute=int(contract_data['queries_per_minute']) if contract_data[
                        'queries_per_minute'] else None,
                    nonce=int(contract_data['nonce']) if contract_data['nonce'] else None,
                    authorization=contract_data.get('authorization', None),
                    remaining=int(contract_data['settlement_height']) - int(height) if (
                                int(height) < int(contract_data['settlement_height'])) else 0
                )
                db.session.add(new_contract)
        except Exception as e:
            print(f"Error processing contract with ID {contract_data['id']}: {e}")

    # Commit the session to save changes
    try:
        db.session.commit()
        print("Contracts successfully stored or updated in the database.")
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Failed to commit contracts to the database: {e}")

def grab_contracts(app: Flask):
    with app.app_context():
        contacts = make_query("api", "/arkeo/contracts")['contract']

        store_or_update_contracts_in_db(contacts)