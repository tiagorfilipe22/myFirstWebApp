import smtplib
from email.message import EmailMessage

def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    #msg['bcc'] = to
    

    #user = "vyrustr@gmail.com"
    # msg['from'] = "USER TEST"
    #password = "jgisyiamoreggqlr"

    user = "helpdesk.project.cs50@gmail.com"
    # msg['from'] = "USER TEST"
    password = "volnisyolpbrtgvl"


    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

push = "5vc4x9iduu@pomail.net"

emails = ["vyrustr@gmail.com", "5vc4x9iduu@pomail.net", "tiagorfilipe22@hotmail.com"]

if __name__ == '__main__':
    email_alert("Subject Test", "body Test", emails)