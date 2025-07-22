from DB import db
import json

class Provider(db.Model):
    __tablename__ = 'providers'

    provider_name = db.Column(db.String(100), unique=True, nullable=False)
    meta_data_accessible = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(1024), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(45), nullable=True)
    free_tier_rate_limit = db.Column(db.Integer, nullable=True)
    provider_pubkey = db.Column(db.String(128), primary_key=True, nullable=True)
    endpoints = db.Column(db.Text, nullable=True)
    contracts = db.Column(db.Text, nullable=True)
    number_of_services = db.Column(db.Integer, default=0)
    services = db.Column(db.String(1024), nullable=True)
    offline_reason = db.Column(db.String(255), nullable=True)
    isp = db.Column(db.String(128), nullable=True)
    isp_country = db.Column(db.String(128), nullable=True)
    ip_addr = db.Column(db.String(48), nullable=True)
    id = db.Column(db.Integer, unique=True, autoincrement=True)

    def __repr__(self):
        return f"<Provider(provider_name='{self.provider_name}', number_of_services={self.number_of_services})>"

    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "provider_name": self.provider_name,
            "meta_data_accessible": self.meta_data_accessible,
            "description": self.description,
            "website": self.website,
            "location": self.location,
            "free_tier_rate_limit": self.free_tier_rate_limit,
            "provider_pubkey": self.provider_pubkey,
            "endpoints": self.endpoints,
            "contracts": self.contracts,
            "number_of_services": self.number_of_services,
            "services": self.services,
            "offline_reason": self.offline_reason,
            "isp": self.isp,
            "isp_country": self.isp_country,
            "ip_addr": self.ip_addr,
        }

    def to_json(self):
        """Convert the model instance to a JSON string."""
        return json.dumps(self.to_dict())