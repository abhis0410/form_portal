
# Atlan-Backend-Challenge
## Data Collection Platform Integration Solution

This project is a comprehensive solution for integrating a data collection platform with various post-submission business logic actions.  
This README provides an overview of the design, architecture, and implementation of this solution.


## Problem Statements

The core problem revolves around adding post-submission business logic to the data collection process. Clients require various actions to be triggered based on the collected data. Some real-life examples include:

1) How to store form data such as questions, responses?

2) Searching for slangs in local languages based on responses to different questions. 
3) Validating responses against predefined business rules and notifying data collectors when discrepancies are found.
4) Exporting all data to Google Sheets for further analysis.
5) Sending SMS notifications to participants with details from the collected responses.  
  

The challenge is to create a unified and extensible system that can seamlessly integrate new use cases without extensive backend modifications.


## Description of Solutions

To create kind of plug and play system, I have used Plugin architecture in Flask Framework of Python.

All the plugins could be processed once the form is submitted. 


## Question 1

Data is being stored in database via SQL. Questions and Responses are being linked to form with the use of foriegn key.

````
# models.py 
Form
├─ id: Integer (Primary Key)
├─ form_name: String(100)
├─ form_desc: String(5000)
├─ creation_date: DateTime

````

````
Question
├─ id: Integer (Primary Key)
├─ form_id: Integer (Foreign Key to Form.id)
├─ question_text: String(255)
├─ question_type: String(50)


````

````
Response
├─ id: Integer (Primary Key)
├─ form_id: Integer (Foreign Key to Form.id)
├─ submission_date: DateTime
````

````
Answer
├─ id: Integer (Primary Key)
├─ response_id: Integer (Foreign Key to Response.id)
├─ question_id: Integer (Foreign Key to Question.id)
├─ answer_text: String(255)
├─ selected_option: String(50)
├─ answer_date: DateTime
````
## Question 2

Implementing Slang-Case usage via Database Integration:

- Store city-slang mappings in DataBase
- When a response is submitted, extract the answer to the multiple-choice question (MCQ) about cities and use it as a key to look up the local language slang in the dictionary.
- This approach is simple and requires minimal computational resources. However, it may not handle dynamic or frequently changing slangs effectively.

````
# slang_search.py

def find_local_slang(city):
    slang_map_filename = 'example.csv' 
    slang_map = {}
    try:
        with open(slang_map_filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 2:
                    c, slang = row
                    slang_map[c] = slang
    except FileNotFoundError:
        pass

    return slang_map.get(city, "Slang not found")

````
## Question 3

Implementing Response Validation with Standard If else conditions


````
# response_validation.py

def validate_response(response):
    error_messages = []

    if response.monthly_savings > response.monthly_income:
        error_messages.append("Monthly savings cannot be more than monthly income.")

    # more flag checks can be added 
    return error_messages

def send_response_back_to_data_collector(response, error_messages):

    sender_email = ''
    recipient_email = response.data_collector_email 
    smtp_server = ""
    smtp_port = 587
    smtp_username = ""
    smtp_password = ""

    subject = "Response Validation Error"
    message = "\n".join(error_messages)
    msg = MIMEText(message)
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
    
    server.close()


def process_response(form, response):
    error_messages = validate_response(response)

    if error_messages:
        send_response_back_to_data_collector(response, error_messages)

````
## Question 4

Data could be processed to google sheets via using Google Drive API & Services

````
# google_sheets.py

def export_response(form, response):
    try:
        credentials_path = 'credentials.json'

        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        gc = gspread.authorize(credentials)

        spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1yBsWYQm-GgmIMHC5cQf8wB5ZmkZiEZsq4sdo-_ZNCBY/edit'

        sh = gc.open_by_url(spreadsheet_url)

        worksheet = sh.get_worksheet(0)

        response_data = [response.submission_date]
        for question in form.questions:
            response_data.append(get_response_text(response, question))

        worksheet.append_table([response_data])
        return "Response exported to Google Sheets."


    except SpreadsheetNotFound as ex:
        # Handle the exception here (e.g., log an error or return a user-friendly message)
        error_message = f"Google Sheets document not found: {ex}"
        return error_message
    

def get_response_text(response, question):
    # Query the database to get the response text for the given response and question
    answer = Answer.query.filter_by(response_id=response.id, question_id=question.id).first()

    if answer:
        return answer.answer_text
    else:
        return "No answer"

````

````
crediantial.json contains api & services credentials
````
## Question 5

SMS Notifications can be implemented by using twilio library

````
def send_sms_notification(form, response):
    twilio_account_sid = ''
    twilio_auth_token = ''
    twilio_phone_number = ''

    client = Client(twilio_account_sid, twilio_auth_token)

    customer_phone_number = response.customer_phone  # Update this with your data structure

    sms_message = f"Thank you for participating in our exercise! Your details: Name: {response.customer_name}, Email: {response.customer_email}, Address: {response.customer_address}"

    message = client.messages.create(
        body=sms_message,
        from_=twilio_phone_number,
        to=customer_phone_number
    )

    return f"SMS sent with message SID: {message.sid}"
````
## Project Dependencies

Here are the dependencies required for this project:

1. [Twilio](https://www.twilio.com/docs/quickstart/python/sms#overview): Twilio is used for sending and receiving SMS messages in your application.
2. [CSV](https://docs.python.org/3/library/csv.html): The CSV module is used for reading and writing CSV files.
3. [gspread](https://gspread.readthedocs.io/en/latest/): Gspread is a Python library for accessing Google Sheets using the Google Sheets API.
4. [oauth2client](https://github.com/googleapis/oauth2client): This library is used for handling OAuth2 authentication for Google services.
5. [gspread.exceptions](https://gspread.readthedocs.io/en/latest/): This is a part of the gspread library and is used for handling exceptions related to Google Sheets.
6. [models](https://www.sqlalchemy.org/): It seems like the "models" module is a custom module for your application.
7. [smtplib](https://docs.python.org/3/library/smtplib.html): The smtplib module is used for sending emails.
8. [email.mime.text](https://docs.python.org/3/library/email.mime.text.html): This is used to create MIMEText objects for constructing email messages.
9. [importlib](https://docs.python.org/3/library/importlib.html): The importlib module provides tools for working with dynamically imported modules.
10. [os](https://docs.python.org/3/library/os.html): The os module provides a way of using operating system-dependent functionality.
11. [Flask](https://flask.palletsprojects.com/en/2.1.x/): Flask is a web framework for building web applications in Python.
12. [SQLAlchemy](https://www.sqlalchemy.org/): SQLAlchemy is used for working with databases in your Flask application.
13. [sqlalchemy.orm](https://www.sqlalchemy.org/): The sqlalchemy.orm module is a part of SQLAlchemy and is used for ORM-related functionality.

Please make sure to install these dependencies before running your project. You can use a tool like pip to install Python packages.

```bash
pip install twilio gspread oauth2client flask sqlalchemy
```
## Thanks

