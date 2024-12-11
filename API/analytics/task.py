from API.analytics.models import NonceData, NonceAggregate
from DB import db
from common.common import *
from flask import Flask
from sqlalchemy import func
from datetime import datetime, timedelta

def grab_nonce_counter(app: Flask):
    with app.app_context():
        # Fetch network status and current block height
        status = make_query("api", "/cosmos/base/node/v1beta1/status")
        height = int(status["height"])
        timestamp = convert_to_mysql_timestamp(status["timestamp"])  # Convert timestamp

        # Fetch contracts data
        contracts = make_query("api", "/arkeo/contracts")['contract']

        # Initialize nonce counters
        nonce_by_provider_service = {}
        nonce_by_service = {}

        # Process each contract
        for contract_data in contracts:
            provider = contract_data['provider']
            service = int(contract_data['service'])
            nonce = int(contract_data['nonce']) if contract_data['nonce'] else 0

            # Aggregate nonce counts by provider and service
            if (provider, service) not in nonce_by_provider_service:
                nonce_by_provider_service[(provider, service)] = 0
            nonce_by_provider_service[(provider, service)] += nonce

            # Aggregate nonce counts by service
            if service not in nonce_by_service:
                nonce_by_service[service] = 0
            nonce_by_service[service] += nonce

        # Store data in `nonce_data` table
        for (provider, service), nonce_count in nonce_by_provider_service.items():
            new_nonce_data = NonceData(
                timestamp=timestamp,
                provider=provider,
                service=service,
                nonce_count=nonce_count,
                block_height=height
            )
            db.session.add(new_nonce_data)

        # Optional: log aggregate data by service
        for service, total_nonce in nonce_by_service.items():
            print(f"Service {service}: Total Nonce = {total_nonce}")

        # Commit changes
        try:
            db.session.commit()
            print("Nonce data successfully stored.")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to store nonce data: {e}")

        # Populate NonceAggregate for hourly totals
        populate_nonce_aggregate(timestamp)

def populate_nonce_aggregate(current_time):
    """
    Computes and stores aggregate nonce data for hourly, daily, and weekly periods.
    """
    # Calculate the start time for the current hour
    start_time = current_time.replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)

    # Query data from NonceData
    nonce_data = db.session.query(
        NonceData.provider,
        NonceData.service,
        func.sum(NonceData.nonce_count).label('total_nonce')
    ).filter(
        NonceData.timestamp >= start_time,
        NonceData.timestamp < end_time
    ).group_by(
        NonceData.provider, NonceData.service
    ).all()

    # Store aggregates
    for entry in nonce_data:
        # Check if an aggregate entry already exists for this provider and service for the given time period
        existing_entry = db.session.query(NonceAggregate).filter(
            NonceAggregate.time_period == 'hourly',
            NonceAggregate.start_time == start_time,
            NonceAggregate.end_time == end_time,
            NonceAggregate.provider == entry.provider,
            NonceAggregate.service == entry.service
        ).first()

        if existing_entry:
            # Update existing entry if it exists
            existing_entry.nonce_count = entry.total_nonce
        else:
            # Insert a new aggregate entry if it does not exist
            aggregate_entry = NonceAggregate(
                time_period='hourly',
                start_time=start_time,
                end_time=end_time,
                provider=entry.provider,
                service=entry.service,
                nonce_count=entry.total_nonce
            )
            db.session.add(aggregate_entry)

    # Commit the aggregate entries
    try:
        db.session.commit()
        print(f"Nonce aggregate successfully stored for {start_time} - {end_time}.")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to store nonce aggregates: {e}")