import random
import string
import smtplib
from email.message import EmailMessage
import http.client, urllib
from dotenv import load_dotenv
import os

# load the .env file
load_dotenv()

# access the env variables
db_email_user = os.getenv('DB_EMAIL_USER')
db_email_password = os.getenv('DB_EMAIL_PASSWORD')
db_push_token = os.getenv('DB_PUSH_TOKEN')
db_push_user = os.getenv('DB_PUSH_USER')

# function to get random password
def get_random_string():
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(8))
    return(password)



# function to get first letter uppercase
def getFirstUpper(string):
    string = string[0].upper() + string[1:]
    return string

# function send email
def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user = db_email_user
    password = db_email_password

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

# function to send pushover notifications
def message(title, text):

  conn = http.client.HTTPSConnection("api.pushover.net:443")
  conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
      "token": db_push_token,
      "user": db_push_user,
      "title": title,
      "message": text,
    }), { "Content-type": "application/x-www-form-urlencoded" })

  conn.getresponse()
