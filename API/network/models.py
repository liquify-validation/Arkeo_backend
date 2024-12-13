from DB import db
from datetime import datetime
import json


class Network(db.Model):
    __tablename__ = 'network'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    bond = db.Column(db.BigInteger, default=None)
    number_of_providers = db.Column(db.Integer, default=None)
    number_of_services = db.Column(db.Integer, default=None)
    number_of_contracts = db.Column(db.Integer, default=None)
    height = db.Column(db.Integer, default=None)
    blockTime = db.Column(db.Float, default=None)

    def __repr__(self):
        return f"<Network id={self.id}, bond={self.bond}, number_of_providers={self.number_of_providers}, number_of_services={self.number_of_services}>"

    def to_dict(self):
        return {
            "id": self.id,
            "bond": self.bond,
            "number_of_providers": self.number_of_providers,
            "number_of_services": self.number_of_services,
        }

    def to_json(self):
        """Convert the model instance to a JSON string."""
        return json.dumps(self.to_dict())