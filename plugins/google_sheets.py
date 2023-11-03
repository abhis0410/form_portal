"""
-----------------This Code is written by-----------------
---------------------Abhinav Singla----------------------
"""

#Code Starts Here

#Importing Libraries

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import SpreadsheetNotFound
from models import Answer 

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
