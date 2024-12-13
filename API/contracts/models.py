from DB import db
import json


class Contract(db.Model):
    __tablename__ = 'contracts'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    provider = db.Column(db.String(80), nullable=False)
    service = db.Column(db.Integer, nullable=False)
    client = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(45), default=None)
    height = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, default=None)
    rate = db.Column(db.String(1024), default=None)
    deposit = db.Column(db.Integer, default=None)
    paid = db.Column(db.Integer, default=None)
    settlement_height = db.Column(db.Integer, default=None)
    completed = db.Column(db.Boolean, default=None)
    queries_per_minute = db.Column(db.Integer, default=None)
    nonce = db.Column(db.Integer, default=None)
    authorization = db.Column(db.String(45), default=None)
    remaining = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Contract id={self.id}, provider={self.provider}, service={self.service}>"

    def to_dict(self):
        return {
            "id": self.id,
            "provider": self.provider,
            "service": self.service,
            "client": self.client,
            "type": self.type,
            "height": self.height,
            "duration": self.duration,
            "rate": self.rate,
            "deposit": self.deposit,
            "paid": self.paid,
            "settlement_height": self.settlement_height,
            "completed": self.completed,
            "queries_per_minute": self.queries_per_minute,
            "nonce": self.nonce,
            "authorization": self.authorization,
            "remaining": self.remaining,
        }

    def to_json(self):
        """Convert the model instance to a JSON string."""
        return json.dumps(self.to_dict())