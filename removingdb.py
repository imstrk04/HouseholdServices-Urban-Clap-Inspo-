from flask import Flask
from application.database import db
from application.models import Service, ServiceProfessional, Customer, ServiceRequest, Rating
from datetime import datetime

app = Flask(__name__)
# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'
app.app_context().push()
db.init_app(app)

with app.app_context():
    try:
        # Delete all entries in each table
        #User.query.delete()
        #Customer.query.delete()
        #ServiceProfessional.query.delete()
        #Service.query.delete()
        #ServiceRequest.query.delete()
        Rating.query.delete()
        # Commit the session to apply the changes
        db.session.commit()

        print("All values deleted successfully!")
    
    except Exception as e:
        # Rollback in case of any errors
        db.session.rollback()
        print(f"An error occurred: {e}")