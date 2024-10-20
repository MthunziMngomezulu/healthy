from datetime import datetime
from email.policy import default
from turtle import title
from Funding import db, login_manager
from Funding import bcrypt
from flask_login import UserMixin
from Funding import app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    surname = db.Column(db.String(length=30), nullable=False)  # Removed uniqueness for surname
    dateofbirth = db.Column(db.Date(), nullable=False)
    address = db.Column(db.String(length=13), nullable=False)  # Changed to lowercase to match form field
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    contact_details = db.Column(db.String(length=50), nullable=False, unique=True)
    # Updated 'faculty' field to 'job_role' to reflect the job-related role
    faculty = db.Column(db.String())
    password_hash = db.Column(db.String(length=60), nullable=False)
    role = db.Column(db.String(length=30), nullable=True ,default='cadidate')  # Removed uniqueness constraint for 'role'

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Item {self.name}'


class Applications(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    job_title = db.Column(db.String(length=200), nullable=False)
    healthcare_Facility = db.Column(db.String(length=200), nullable=False)
    
    # Updated 'faculty' field to 'job_role' in ApplicationForm
    #role = db.Column(db.String(50), nullable=True) # Changed from 'faculty' to 'job_role'
    
    description = db.Column(db.String(length=255), nullable=False)
    environment = db.Column(db.String(), nullable=False)
    #amount = db.Column(db.Float(), nullable=False)
    link = db.Column(db.String(length=200), nullable=False)

with app.app_context():
    db.create_all()  # Create tables

    # Create a new user
    date_of_birth = datetime.strptime("1990-05-15", '%Y-%m-%d').date()
    user = User(
        username="gomez",
        surname="mngomezulu",
        dateofbirth=date_of_birth,
        address="durban",
        email_address="mngomezulu@gomez.com",
        contact_details="00000000",
        faculty="Nurse",
        password_hash=bcrypt.generate_password_hash("passwords").decode('utf-8')
    )

    application=Applications(job_title = 'Nurse',healthcare_Facility = 'Hospital',description = 'To assist in providing Occupational therapy services to patients To assist the Occupational Therapist with therapy groups.' ,environment = 'urban',link = 'https://shorturl.at/A4sCw')
    application1=Applications(job_title = 'Nurse',healthcare_Facility = 'Hospital',description = 'To assist in providing Occupational therapy services to patients To assist the Occupational Therapist with therapy groups.' ,environment = 'urban',link = 'https://shorturl.at/A4sCw')
    application2=Applications(job_title = 'Dentist',healthcare_Facility = 'Hospital',description = 'Examine patients medical records and prepare them for treatment Check teeth, gums, and other parts of the mouth, along with X-rays and tests, to diagnose dental problems' ,environment = 'rural',link = 'https://shorturl.at/OjjLa')
    application3=Applications(job_title = 'Doctor',healthcare_Facility = 'Hospital',description='Provide medical care to patients, diagnose conditions, prescribe treatments, and oversee patient recovery.',environment = 'urban',link = 'https://shorturl.at/npt1T')
    application4=Applications(job_title = 'Pharmacist',healthcare_Facility = 'Hospital',description ='Dispense medications to patients, provide drug-related advice, and ensure the safe use of prescriptions.',environment = 'urban',link = 'https://shorturl.at/A4sCw')
    application5=Applications(job_title = 'Optometrist',healthcare_Facility = 'Hospital',description = 'Conduct eye examinations, prescribe corrective lenses, and diagnose visual impairments or eye diseases.' ,environment = 'urban',link = 'https://za.indeed.com/Optometrist-jobs?vjk=838c26724d3ca0dc&advn=9128450782417927')
    application6=Applications(job_title = 'Clinical Technologist',healthcare_Facility = 'Hospital',description = 'Operate and maintain medical equipment, assist with diagnostic procedures, and ensure accurate test results for patients.' ,environment = 'urban',link = 'https://shorturl.at/yjljs')



    # Add and commit the new user
    db.session.add(user)
    db.session.add_all([application1, application,application2,application3,application4,application5,application6])
    try:
        db.session.commit()
    except:
        db.session.rollback()

