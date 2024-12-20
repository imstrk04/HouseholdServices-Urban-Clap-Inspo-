from .database import db
from datetime import date

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)

class ServiceProfessional(db.Model):
    __tablename__ = 'service_professionals'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    profile_doc = db.Column(db.String(200), nullable=False)  
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.DateTime, default=date.today())
    status = db.Column(db.String(50), nullable=False)

    service = db.relationship('Service', backref='service_professionals', lazy=True)
    
    @property
    def average_rating(self):
        ratings = Rating.query.filter_by(professional_id=self.id).all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0.0

class Service(db.Model):
    __tablename__ = 'services'
    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50), nullable=False)
    descriptions = db.Column(db.Text, nullable=True)

    service_requests_list = db.relationship('ServiceRequest', backref='service', cascade='all, delete-orphan', lazy=True)

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    serv_req_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    cust_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professionals.id'), nullable=True)
    date_of_req = db.Column(db.DateTime, default=date.today)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(50), nullable=False)  # requested, assigned, completed
    remarks = db.Column(db.Text, nullable=True)

    professional = db.relationship('ServiceProfessional', backref='service_requests', lazy=True)
    customer = db.relationship('Customer', backref='service_requests', lazy=True)

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professionals.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    serv_req_id = db.Column(db.Integer, db.ForeignKey('service_requests.serv_req_id'), nullable=False) 
    rating = db.Column(db.Float, nullable=False)
    review = db.Column(db.Text, nullable=True)
    rating_status = db.Column(db.String(50), nullable=False)

    service = db.relationship('Service', backref='ratings', lazy=True)
    professional = db.relationship('ServiceProfessional', backref='ratings', lazy=True)
    customer = db.relationship('Customer', backref='ratings', lazy=True)
    service_request = db.relationship('ServiceRequest', backref='ratings', lazy=True)  

def get_total_services():
    return Service.query.count()

def get_total_customers():
    return User.query.filter_by(role='Customer').count()

def get_total_professionals():
    return User.query.filter_by(role='ServiceProfessional').count()

def get_total_service_requests():
    return ServiceRequest.query.count()
