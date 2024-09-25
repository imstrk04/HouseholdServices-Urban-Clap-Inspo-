from flask import Flask
from application.database import db
from application.models import Service, ServiceProfessional, Customer, ServiceRequest
from datetime import datetime

app = Flask(__name__)
# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'
app.app_context().push()
db.init_app(app)


with app.app_context():
    # Step 1: Create and add two Services
    '''service1 = Service(
        name="Plumbing",
        base_price=150.0,
        time_required="2 hours",
        descriptions="Fixing leaks, broken pipes, and installation of new fixtures."
    )
    
    service2 = Service(
        name="Electrician",
        base_price=200.0,
        time_required="3 hours",
        descriptions="Wiring, installation of electrical appliances, and repairs."
    )

    db.session.add(service1)
    db.session.add(service2)
    
    # Step 2: Create and add two Service Professionals
    professional1 = ServiceProfessional(
        email="srihari@gmail.com",
        password="srihari",
        full_name="SriHari",
        service_id=1,  # Assuming this is for Plumbing
        experience=5,
        profile_doc="profile_doc1.pdf",
        address="123 12th Avenue West Mambalam",
        pincode="600083"
    )

    professional2 = ServiceProfessional(
        email="vamsi@gmail.com",
        password="ronaldo",
        full_name="Vamsi",
        service_id=2,  # Assuming this is for Electrician
        experience=8,
        profile_doc="profile_doc2.pdf",
        address="456 Rukmani Street West Mambalam",
        pincode="600083"
    )

    db.session.add(professional1)
    db.session.add(professional2)
    
    # Step 3: Create and add two Customers
    customer1 = Customer(
        email="varshini@gmail.com",
        password="vv1805",
        full_name="Varshini Venkatesh",
        address="No. 4 MKN Road Alandur",
        pincode="600013"
    )

    customer2 = Customer(
        email="vaish@gmail.com",
        password="vaish1805",
        full_name="Vaishnavi Venkatesh",
        address="No. 10 TTK road Chennai",
        pincode="600082"
    )

    db.session.add(customer1)
    db.session.add(customer2)
    '''
    # Step 4: Create and add two Service Requests
    request1 = ServiceRequest(
        service_id=1, 
        cust_id=1,  
        professional_id=1,  
        date_of_req=datetime.now(),
        service_status="requested"
    )

    request2 = ServiceRequest(
        service_id=2, 
        cust_id=2,  
        professional_id=2, 
        date_of_req=datetime.now(),
        service_status="requested"
    )

    db.session.add(request1)
    db.session.add(request2)
    
    db.session.commit()

    print("Data inserted successfully!")
