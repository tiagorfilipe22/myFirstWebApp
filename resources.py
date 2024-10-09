import random
import string
import smtplib
from email.message import EmailMessage
import http.client, urllib


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
    user = "helpdesk.project.cs50@gmail.com"
    password = "volnisyolpbrtgvl"

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
      "token": "abhzzh8o6ouxk8z8c31b5n9qq5nfvw",
      "user": "u8i163kt3oo7yswjrvni79fab6mzxg",
      "title": title,
      "message": text,
    }), { "Content-type": "application/x-www-form-urlencoded" })

  conn.getresponse()
