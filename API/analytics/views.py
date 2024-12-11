from flask_smorest import Blueprint, abort
from sqlalchemy import func
from API.analytics.models import NonceData,NonceAggregate
from flask import jsonify, request
from DB import db
from common.common import *
from datetime import datetime, timedelta

blp = Blueprint("analytics", __name__, description="Analytics API")


@blp.route('/total', methods=['GET'])
def get_total_nonce():
    """
    Get the total nonce count for a specified offset.
    ---
    tags:
      - Analytics
    parameters:
      - in: query
        name: offset_hours
        type: integer
        description: Number of hours to offset from the current time. Defaults to 1.
      - in: query
        name: offset_days
        type: integer
        description: Number of days to offset from the current time. Defaults to 0.
    responses:
      200:
        description: Total nonce count.
    """
    # Get offset values from query parameters
    offset_hours = int(request.args.get('offset_hours', 1))  # Default to 1 hour
    offset_days = int(request.args.get('offset_days', 0))  # Default to 0 days

    # Calculate the end time based on the offset values, aligned to the current hour
    now = datetime.utcnow()

    # Adjust end_time to the beginning of the next full hour
    end_time = (now - timedelta(days=offset_days, hours=offset_hours)).replace(minute=0, second=0,
                                                                               microsecond=0) + timedelta(hours=1)

    # Adjust start_time to one hour before end_time (aligned to the hour)
    start_time = end_time - timedelta(hours=1)

    # Query to get the total nonce count for the specified period
    total_nonce = db.session.query(func.sum(NonceAggregate.nonce_count)).filter(
        NonceAggregate.time_period == 'hourly',
        NonceAggregate.start_time >= start_time,
        NonceAggregate.end_time <= end_time
    ).scalar()

    # If no data is found, ensure total_nonce is 0
    total_nonce = total_nonce or 0

    # Return the results as JSON
    return jsonify({
        "total_nonce": total_nonce,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    })

@blp.route('/chains', methods=['GET'])
def get_chain_nonce():
    """
    Get nonce metrics grouped by chain (service) for a specified offset, optionally filtered by service.
    ---
    tags:
      - Analytics
    parameters:
      - in: query
        name: offset_hours
        type: integer
        description: Number of hours to offset from the current time. Defaults to 1.
      - in: query
        name: offset_days
        type: integer
        description: Number of days to offset from the current time. Defaults to 0.
      - in: query
        name: service
        type: integer
        description: Filter by a specific chain (service ID).
    responses:
      200:
        description: Nonce metrics grouped by chain (service).
    """
    offset_hours = int(request.args.get('offset_hours', 1))
    offset_days = int(request.args.get('offset_days', 0))
    service = request.args.get('service')

    now = datetime.utcnow()

    # Calculate the start and end time
    # Adjust end_time to the beginning of the next full hour
    end_time = (now - timedelta(days=offset_days, hours=offset_hours)).replace(minute=0, second=0,
                                                                               microsecond=0) + timedelta(hours=1)
    start_time = end_time - timedelta(hours=1)

    # Build the query
    query = db.session.query(
        NonceAggregate.service,
        func.sum(NonceAggregate.nonce_count).label('total_nonce')
    ).filter(
        NonceAggregate.time_period == 'hourly',
        NonceAggregate.start_time >= start_time,
        NonceAggregate.end_time <= end_time
    )

    # Apply service filter if provided
    if service:
        query = query.filter(NonceAggregate.service == int(service))

    # Group by service and fetch results
    chain_data = query.group_by(NonceAggregate.service).all()

    return jsonify({
        "chains": [
            {"service": entry.service, "total_nonce": entry.total_nonce}
            for entry in chain_data
        ],
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    })

@blp.route('/providers', methods=['GET'])
def get_provider_nonce():
    """
    Get nonce metrics grouped by provider for a specified offset, optionally filtered by provider.
    ---
    tags:
      - Analytics
    parameters:
      - in: query
        name: offset_hours
        type: integer
        description: Number of hours to offset from the current time. Defaults to 1.
      - in: query
        name: offset_days
        type: integer
        description: Number of days to offset from the current time. Defaults to 0.
      - in: query
        name: provider
        type: string
        description: Filter by a specific provider.
    responses:
      200:
        description: Nonce metrics grouped by provider.
    """
    offset_hours = int(request.args.get('offset_hours', 1))
    offset_days = int(request.args.get('offset_days', 0))
    provider = request.args.get('provider')

    now = datetime.utcnow()

    # Calculate the start and end time
    # Adjust end_time to the beginning of the next full hour
    end_time = (now - timedelta(days=offset_days, hours=offset_hours)).replace(minute=0, second=0,
                                                                               microsecond=0) + timedelta(hours=1)
    start_time = end_time - timedelta(hours=1)

    # Build the query
    query = db.session.query(
        NonceAggregate.provider,
        func.sum(NonceAggregate.nonce_count).label('total_nonce')
    ).filter(
        NonceAggregate.time_period == 'hourly',
        NonceAggregate.start_time >= start_time,
        NonceAggregate.end_time <= end_time
    )

    # Apply provider filter if provided
    if provider:
        query = query.filter(NonceAggregate.provider == provider)

    # Group by provider and fetch results
    provider_data = query.group_by(NonceAggregate.provider).all()

    return jsonify({
        "providers": [
            {"provider": entry.provider, "total_nonce": entry.total_nonce}
            for entry in provider_data
        ],
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    })