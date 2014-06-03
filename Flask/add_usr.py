import requests
#payload = {"screen_name": 'felipeblassioli', 'email': 'felipeblassioli@gmail.com'}
payload = {"screen_name": '7farah7', 'email': 'kamilacamilo1@gmail.com'}
requests.get('http://29days.myeyes.com.br/users/add', params=payload)