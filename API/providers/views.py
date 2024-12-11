from flask_smorest import Blueprint, abort
from sqlalchemy import func
from API.providers.models import Provider
from flask import jsonify

blp = Blueprint("providers", __name__, description="Provider API")

@blp.route('/providers')
def providers():
    """
    Grab a JSON of all providers on the Arkeo network.
    ---
    tags:
      - Providers
    responses:
      200:
        description: A JSON of all providers on the network.
    """
    # Query all providers using SQLAlchemy
    providers = Provider.query.all()

    # Convert the providers to a dictionary
    dict_of_dicts = {provider.provider_name: provider.to_dict() for provider in providers}

    # Return the data as a JSON response
    return jsonify(dict_of_dicts)

@blp.route('/get-providers')
def get_providers():
    """Grab a list of provider names
       ---
       tags:
         - Providers
       responses:
         200:
           description: list of provider names
       """
    provider_names = Provider.query.with_entities(Provider.provider_name).all()

    # Convert list of tuples into a flat list of names
    name_list = [name[0] for name in provider_names]

    return jsonify(name_list)

@blp.route('/locations')
def get_location():
    """
    Grab the hosted country of all Arkeo node providers.
    ---
    tags:
      - Providers
    responses:
      200:
        description: The breakdown of node locations on the network.
    """
    # Query to group by isp_country and count occurrences
    country_counts = (
        Provider.query
        .with_entities(Provider.isp_country, func.count(Provider.id).label('count'))
        .filter(Provider.isp_country != '')  # Exclude empty values
        .group_by(Provider.isp_country)
        .all()
    )

    # Convert results into a dictionary
    output = {country: count for country, count in country_counts}

    # Return as JSON
    return jsonify(output)