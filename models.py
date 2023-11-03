"""
-----------------This Code is written by-----------------
---------------------Abhinav Singla----------------------
"""

#Code Starts Here

from app import db

#Declaring Forms Section
class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_name = db.Column(db.String(100)) #Title
    form_desc = db.Column(db.String(5000)) #Description
    creation_date = db.Column(db.DateTime) #Date

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