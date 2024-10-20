from Funding import app, db
from flask import render_template, redirect, request, url_for, flash, session, jsonify
from Funding.models import Item, User, Applications as ApplicationFormModel
from Funding.forms import RegisterForm, LoginForm, ApplicationF, ProfileForm, ContactForm
from flask_login import login_user, logout_user, current_user, login_required
from email.message import EmailMessage
from datetime import datetime
import ssl, smtplib, requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Homepage route
@app.route('/')
def main():
    return redirect(url_for('login_page'))

# Render home page
@app.route('/home')
def home_page():
    return render_template('home_page.html')

# Render about page
@app.route('/about')
def about_page():
    return render_template('about.html')

# Display bursaries
@app.route('/bursaries')
def bursary_page():
    applications = ApplicationFormModel.query.all()
    return render_template('bursarylist.html', applications=applications)

# Register user
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                surname=form.surname.data,
                dateofbirth=form.dateofbirth.data,
                address=form.address.data,
                email_address=form.email_address.data,
                contact_details=form.contact_details.data,
                password=form.password.data  # Hashing handled by the password setter
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f'Account created successfully! You are now logged in as {user.username}', category='success')
            return redirect(url_for('home_page'))
        except Exception as e:
            db.session.rollback()
            flash(f'There was an error creating the account: {e}', category='danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", category='danger')
    return render_template('register.html', form=form)

# Login user
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('profile'))
        flash('Username and password do not match! Please try again', category='danger')
    return render_template('login.html', form=form)

# Logout user
@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for('home_page'))

# Application form submission
@app.route('/ApplicationForm', methods=['GET', 'POST'])
def application_form_page():
    form = ApplicationF()
    if form.validate_on_submit():
        try:
            application_data = ApplicationFormModel(
                name=form.name.data,
                company=form.company.data,
                role=form.role.data,
                description=form.description.data,
                enddate=form.enddate.data,
                amount=form.amount.data,
                link=form.link.data
            )
            db.session.add(application_data)
            db.session.commit()
            flash('Application submitted successfully!', category='success')
            return redirect(url_for('home_page'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error occurred in Application Form: {e}', category='danger')
    else:
        for err_msg in form.errors.values():
            flash(f'Error occurred in Application Form: {err_msg}', category='danger')
    return render_template('applicationform.html', form=form)

# Profile page and updating profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email_address = form.email_address.data
        current_user.password = form.password1.data
        current_user.dateofbirth = form.dateofbirth.data
        current_user.role = form.role.data
        current_user.faculty = form.faculty.data
        db.session.commit()
        available_bursaries_count = int(ApplicationFormModel.query.filter(ApplicationFormModel.job_title.ilike(f'%{current_user.faculty}%')).count())
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email_address.data = current_user.email_address
        form.dateofbirth.data = current_user.dateofbirth
        form.role.data = current_user.role
        form.faculty.data = current_user.faculty
        available_bursaries_count = int(ApplicationFormModel.query.filter(ApplicationFormModel.job_title.ilike(f'%{current_user.faculty}%')).count())
    return render_template('profile.html', form=form, available_bursaries_count=available_bursaries_count)

# Contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    email_sender = 'silverknight1414@gmail.com'
    email_password = 'cpxn ympm wuvf fetq'
    if form.validate_on_submit():
        try:
            subject = 'HealthNet For Job Vacancies'
            body = f"Name: {form.name.data}\nEmail: {form.email.data}\n\n{form.message.data}"
            recipient = form.email.data
            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = recipient
            em['Subject'] = subject
            em.set_content(body)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, recipient, em.as_string())
            flash('Your message has been sent!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
    return render_template('contact.html', form=form)

# Bursary details page
@app.route('/bursaries/<int:bursary_id>')
def bursary_detail(bursary_id):
    bursary = ApplicationFormModel.query.get(bursary_id)
    return render_template('bursary_detail.html', bursary=bursary)

# Delete bursary
@app.route('/delete_bursary/<int:id>', methods=['POST'])
@login_required
def delete_bursary(id):
    if current_user.username != "Admin":
        flash('You are not authorized to delete bursaries.', 'danger')
        return redirect(url_for('bursary_page'))
    bursary = ApplicationFormModel.query.get_or_404(id)
    db.session.delete(bursary)
    db.session.commit()
    flash('Bursary deleted successfully!', 'success')
    return redirect(url_for('bursary_page'))

# Job recommendation system
df = pd.read_csv('Job_vacancies.csv')
df.columns = df.columns.str.strip()
df['combined_features'] = df['Job Title'] + " " + df['Required Qualification'] + " " + df['Specification Required']
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['combined_features'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Get job recommendations based on job title
def get_recommendations(job_title):
    idx = df[df['Job Title'] == job_title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    job_indices = [i[0] for i in sim_scores[1:6]]  # Top 5 similar jobs
    return df.iloc[job_indices][['Job Title', 'Required Qualification', 'Specification Required']]

# Recommendation route
@app.route('/recommend', methods=['POST'])
def rec():
    job_title = request.form.get('job_title')
    if job_title:
        recommendations = get_recommendations(job_title)
    else:
        recommendations = None
    applications = ApplicationFormModel.query.all()
    return render_template('bursary_detail.html', job_title=job_title, applications=applications, recommendations=recommendations)
