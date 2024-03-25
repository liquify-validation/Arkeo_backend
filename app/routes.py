import json

from flask import Blueprint, jsonify
from database.db_common import *
from collections import Counter,OrderedDict
main_bp = Blueprint('main', __name__)

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

@main_bp.route('/arkeo/api/providers')
def providers():
    """Grab a json of all providers on the arkeo network
           ---
           tags:
             - General
           responses:
             200:
               description: A json of all provider on the network
           """
    db = (grabQuery('SELECT * FROM Arkeo.providers'))

    dict_of_dicts = {}

    for d in db:
        dict_of_dicts[d['provider_name']] = d

    return dict_of_dicts

@main_bp.route('/arkeo/api/get-providers')
def get_providers():
    """Grab a list of provider names
       ---
       tags:
         - General
       responses:
         200:
           description: list of provider names
       """
    db = (grabQuery('SELECT provider_name FROM Arkeo.providers'))

    providerData = []

    for key in db:
        providerData.append(key["provider_name"])

    return providerData

@main_bp.route('/arkeo/api/chains')
def get_chains():
    """Grab a breakdown of chains and how many hosted providers there are for that chain
       ---
       tags:
         - General
       responses:
         200:
           description: the breakdown of chains
       """
    db = (grabQuery('SELECT * FROM Arkeo.providers'))

    chains = []


    for key in db:
        test = json.loads(key['services'])
        chains.extend(json.loads(key['services']))

    counted_numbers = Counter(chains)
    sorted_counts = sorted(counted_numbers.items(), key=lambda x: x[1], reverse=True)

    # Convert sorted list of tuples back to a dictionary
    sorted_dict = OrderedDict((key, {"count": value, "name": ServiceReverseLookup[key]}) for key, value in sorted_counts)

    return sorted_dict

@main_bp.route('/arkeo/api/locations')
def get_location():
    """Grab the hosted country of all Arkeo node providers
       ---
       tags:
         - General
       responses:
         200:
           description: the breakdown of node locations on the network
       """
    data = grabQuery('SELECT * FROM Arkeo.providers')

    output = {}
    for key in data:
        if key["isp_country"] != '':
            if key["isp_country"] not in output:
                output[key["isp_country"]] = 1
            else:
                output[key["isp_country"]] += 1

    return jsonify(output)