from flask import Flask , render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'e807159b5a8981367c0f3228' # for session management and CSRF protection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense.db' # SQLite database configuration
db = SQLAlchemy(app) # Initialize SQLAlchemy for database interactions
migrate = Migrate(app, db) # Migration used to update database schema without losing data 

login_manager = LoginManager(app) # Initialize LoginManager for user session management to handle user authentication
login_manager.login_view = 'login_page' # Redirects to login page if user is not authenticated
login_manager.login_message_category = "warning"   # Flash message category for login required messages

bcrypt = Bcrypt(app) # Initialize Bcrypt for password hashing

from expense import routes, models