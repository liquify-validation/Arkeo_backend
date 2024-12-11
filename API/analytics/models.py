from DB import db
from datetime import datetime
import json

class NonceData(db.Model):
    __tablename__ = 'nonce_data'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    provider = db.Column(db.String(255), nullable=False)
    service = db.Column(db.Integer, nullable=False)
    nonce_count = db.Column(db.BigInteger, nullable=False)
    block_height = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<NonceData(provider={self.provider}, service={self.service}, nonce_count={self.nonce_count}, timestamp={self.timestamp})>"

class NonceAggregate(db.Model):
    __tablename__ = 'nonce_aggregates'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    time_period = db.Column(db.Enum('hourly', 'daily', 'weekly', name='time_period_enum'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    provider = db.Column(db.String(255), nullable=True)  # Nullable for overall aggregates
    service = db.Column(db.Integer, nullable=True)  # Nullable for overall aggregates
    nonce_count = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return f"<NonceAggregate(time_period={self.time_period}, provider={self.provider}, service={self.service}, nonce_count={self.nonce_count})>"