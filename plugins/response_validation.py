import smtplib
from email.mime.text import MIMEText


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

