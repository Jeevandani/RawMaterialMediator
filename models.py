from extensions import db
from datetime import datetime
from sqlalchemy import Text, Float, Integer, String, DateTime, Boolean
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin, db.Model):
    """Model for admin users with authentication"""
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return the admin ID as string for Flask-Login"""
        return str(self.id)
    
    @property
    def is_active(self):
        """Override Flask-Login is_active property"""
        return self.active
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class ProcurementRequest(db.Model):
    """Model for storing procurement requests"""
    id = db.Column(db.Integer, primary_key=True)
    material_type = db.Column(db.String(100), nullable=False)
    quantity_required = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    quality_standard = db.Column(db.String(50), nullable=False)
    budget_constraint = db.Column(db.Float, nullable=False)
    delivery_deadline = db.Column(db.String(50), nullable=False)
    additional_requirements = db.Column(Text)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'material_type': self.material_type,
            'quantity_required': self.quantity_required,
            'unit': self.unit,
            'quality_standard': self.quality_standard,
            'budget_constraint': self.budget_constraint,
            'delivery_deadline': self.delivery_deadline,
            'additional_requirements': self.additional_requirements,
            'request_date': self.request_date.isoformat() if self.request_date else None,
            'status': self.status
        }

class VendorAnalysis(db.Model):
    """Model for storing vendor analysis results"""
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('procurement_request.id'), nullable=False)
    analysis_data = db.Column(Text)  # JSON string of analysis results
    recommended_vendor = db.Column(db.String(100))
    selected_vendor = db.Column(db.String(100))  # Admin selected vendor
    selected_by = db.Column(db.Integer, db.ForeignKey('admin.id'))  # Admin who selected
    selection_date = db.Column(db.DateTime)
    selection_notes = db.Column(Text)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    request = db.relationship('ProcurementRequest', backref=db.backref('analyses', lazy=True))
    selected_by_admin = db.relationship('Admin', backref=db.backref('vendor_selections', lazy=True))
