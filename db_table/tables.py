from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()
Base = declarative_base()


class CustomerInteractions(db.Model):
    __tablename__ = 'customer_interactions'

    interaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.String(4), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)   # mandatory field
    phone_number = db.Column(db.String(20), nullable=False)     # mandatory field
    request_type = db.Column(db.String(50), nullable=False)     # mandatory field
    preferred_time = db.Column(db.DateTime, nullable=True)
    additional_info = db.Column(db.Text, nullable=True)
    dealer_name = db.Column(db.String(100), nullable=True)
    dealer_phone_number = db.Column(db.String(20), nullable=True)
    interaction_summary = db.Column(db.Text, nullable=True)
    next_steps = db.Column(db.String(255), nullable=True)
    customer_status = db.Column(db.String(50), default='Pending', nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            "interaction_id": self.interaction_id,
            "request_id": self.request_id,
            "customer_name": self.customer_name,
            "phone_number": self.phone_number,
            "request_type": self.request_type,
            "preferred_time": self.preferred_time,
            "additional_info": self.additional_info,
            "dealer_name": self.dealer_name,
            "dealer_phone_number": self.dealer_phone_number,
            "interaction_summary": self.interaction_summary,
            "next_steps": self.next_steps,
            "customer_status": self.customer_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
