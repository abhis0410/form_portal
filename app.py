"""
-----------------This Code is written by-----------------
---------------------Abhinav Singla----------------------
"""

#Code Starts Here


#Importing Libraries
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from plugin_loader import load_plugins
from models import Form, Question, Response, Answer

# Initializing App

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forms.db'  # Use SQLite for simplicity. Replace with a real database in production.
db = SQLAlchemy(app)

# Loading Plugins
loaded_plugins = load_plugins()

#Functions Start here

def after_submission_plugins(form, response):

    result1 = loaded_plugins['google_sheets'].export_response(form, response)
    print(result1)

    result2 = loaded_plugins['sms_notification'].send_sms_notification(form, response)
    print(result2)


    
def is_logged_in():
    return 'username' in session


users = {'admin': 'admin'} # assuming user data is available in database

@app.route('/')
def login():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for('dashboard'))
    
    return 'Login failed. Please check your credentials.'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('dashboard.html')

###-------------------FORM DATA-----------------------------###


#-------------------Generate Form-----------------------------#

@app.route('/generate-form', methods=['GET', 'POST'])
def generate_form():
    if not is_logged_in():
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        new_form = Form(form_name=title , form_desc = description)
        db.session.add(new_form)
        db.session.commit()

        questions = request.form.getlist('question[]')
        answer_types = request.form.getlist('answer-type[]')

        for question, answer_type in zip(questions, answer_types):
            new_question = Question(form_id=new_form.id, 
                                    question_text=question, 
                                    question_type=answer_type)
            db.session.add(new_question)

        db.session.commit()

        return "Form created and saved to the database."

    return render_template('form.html')


#-------------------View Form-----------------------------

@app.route('/view_forms')
def view_forms():
    if not is_logged_in():
        return redirect(url_for('login'))

    forms = Form.query.all()
    print(forms)
    return render_template('view_forms.html', forms=forms)


#-------------------View Responses-----------------------------

def get_response_text(response, question):
    answer = Answer.query.filter_by(response_id=response.id, question_id=question.id).first()
    if answer:
        return answer.answer_text
    else:
        return "No answer"


@app.route('/view_responses/<int:form_id>')
def view_responses(form_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    form = Form.query.get(form_id)

    if form is None:
        return "Form not found."

    responses = Response.query.filter_by(form_id=form.id).all()
    questions = Question.query.filter_by(form_id=form.id).all()

    return render_template('view_responses.html', form=form, responses=responses, questions=questions, get_response_text = get_response_text)


#-------------------Delete Form-----------------------------
@app.route('/delete-form/<int:form_id>', methods=['POST'])
def delete_form(form_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    form = Form.query.get(form_id)

    if form is None:
        return "Form not found."

    db.session.delete(form)
    db.session.commit()
    
    return redirect(url_for('view_forms'))



# -------------------Fill Form -----------------------------#
@app.route('/fill-forms/<int:form_id>', methods=['GET', 'POST'])
def fill_form(form_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    Session = sessionmaker(bind=db.engine)
    session = Session()

    form = session.query(Form).get(form_id)

    if form is None:
        session.close()
        return "Form not found."

    questions = session.query(Question).filter_by(form_id=form.id).all()

    if request.method == 'POST':
        response = Response(form_id=form.id) 
        session.add(response)
        session.commit()

        for question in questions:
            answer_text = request.form.get(f"response_{question.id}")
            selected_option = request.form.get(f"selected_option_{question.id}")
            new_answer = Answer(response_id=response.id, question_id=question.id, answer_text=answer_text, selected_option=selected_option)
            session.add(new_answer)

        session.commit()
        session.close()

        # after_submission_plugins(form, response)
        # commented because of login details entered due to personal reasons

        return "Form submitted successfully."

    session.close()

    return render_template('fill_form.html', form=form, questions=questions)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)