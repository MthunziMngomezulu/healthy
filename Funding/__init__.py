from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
#from flask_mail import Mail, Message



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
app.config['SECRET_KEY']='e02fb8dc6d8a4b29cd4ad808'

"""
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Set SMTP server
app.config['MAIL_PORT'] = 587  # Set SMTP port
app.config['MAIL_USE_TLS'] = True  # Set TLS to False
app.config['MAIL_USE_SSL'] = False  # Set SSL to False
app.config['MAIL_USERNAME'] = 'silverwing1414@gmail.com'  # Set username to None (no authentication)
app.config['MAIL_PASSWORD'] = '22079922'  # Set password to None (no authentication)
app.config['MAIL_DEFAULT_SENDER'] = 'silverknight1414@gmail.com'

mail = Mail(app)
"""

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager= LoginManager(app)
csrf = CSRFProtect(app)

from Funding import routes