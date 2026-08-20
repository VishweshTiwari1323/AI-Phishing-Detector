from datetime import datetime, timezone
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def utc_now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    scans = db.relationship(
        "ScanHistory", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class ScanHistory(db.Model):
    __tablename__ = "scan_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    url = db.Column(db.Text, nullable=False)
    cleaned_url = db.Column(db.String(500), nullable=False, index=True)
    ml_prediction = db.Column(db.String(20), nullable=False)
    vt_result = db.Column(db.String(50))
    vt_malicious = db.Column(db.Integer, default=0)
    vt_suspicious = db.Column(db.Integer, default=0)
    vt_harmless = db.Column(db.Integer, default=0)
    vt_undetected = db.Column(db.Integer, default=0)
    scan_timestamp = db.Column(db.DateTime, default=utc_now, index=True)
    ip_address = db.Column(db.String(50))

    def __repr__(self):
        return f"<ScanHistory {self.url[:50]}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "url": self.url,
            "cleaned_url": self.cleaned_url,
            "ml_prediction": self.ml_prediction,
            "vt_result": self.vt_result,
            "vt_malicious": self.vt_malicious,
            "vt_suspicious": self.vt_suspicious,
            "vt_harmless": self.vt_harmless,
            "vt_undetected": self.vt_undetected,
            "ip_address": self.ip_address,
            "scan_timestamp": (
                self.scan_timestamp.isoformat()
                if self.scan_timestamp
                else None
            ),
        }