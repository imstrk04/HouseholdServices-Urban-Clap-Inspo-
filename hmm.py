from flask_migrate import Migrate
from application.database import db
from app import app

migrate = Migrate(app, db)