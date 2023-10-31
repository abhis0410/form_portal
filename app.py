"""
-----------------This Code is written by-----------------
---------------------Abhinav Singla----------------------
"""

#Code Starts Here


#Importing Libs
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

# Initializing App

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forms.db'  # Use SQLite for simplicity. Replace with a real database in production.
db = SQLAlchemy(app)

#Declaring Forms Section
class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_name = db.Column(db.String(100))
    form_desc = db.Column(db.String(5000))
    creation_date = db.Column(db.DateTime)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'))
    question_text = db.Column(db.String(255))
    question_type = db.Column(db.String(50))

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'))
    submission_date = db.Column(db.DateTime)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    answer_text = db.Column(db.String(255))
    selected_option = db.Column(db.String(50))
    answer_date = db.Column(db.DateTime)


#Functions Start here

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

        return "Form submitted successfully."

    session.close()

    return render_template('fill_form.html', form=form, questions=questions)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)