import http.client, urllib

token = "abhzzh8o6ouxk8z8c31b5n9qq5nfvw"
user = "u8i163kt3oo7yswjrvni79fab6mzxg"



def message(title, text):

  conn = http.client.HTTPSConnection("api.pushover.net:443")
  conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
      "token": token,
      "user": user,
      "title": title,
      "message": text,
    }), { "Content-type": "application/x-www-form-urlencoded" })

  conn.getresponse()



if __name__ == '__main__':
    message("title Test", "Text Test")

