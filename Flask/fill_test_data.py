# -*- coding: utf-8 -*-
from twython import TwythonStreamer
from models import User
from app import countries, challenges
import json

APP_KEY = 'vko3p8bk1WE1BBu8vV5xzfHQG'
APP_SECRET = '6mKL4xPJFXT62OP1PeVVdQGFBS66lCtXHhIb81zqGWbBQhnb2L'
OAUTH_TOKEN = '228101273-d2CC5EdBwGipJlpyO3fsi5eSzmJlqc0D2BpfuqdG'
OAUTH_TOKEN_SECRET = 'aDZowFcdPIwWvWOYZ51djy8AcwHqEGDvZc6b846FhxOwc'

from random import randint
class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print data['text'].encode('utf-8')
        try:
            print json.dumps(data, indent=4, sort_keys=True)
            usr_id = data['user']['id_str']
            tweet_id = data['id_str']
            media_data = data['entities']['media'][0]
            challenge = challenges[randint(0,len(challenges)-1)]
            country = countries[randint(0,len(countries)-1)]
            print usr_id,tweet_id,country,challenge
            User.save_tweet_data(usr_id,tweet_id,media_data,country,challenge)
        except KeyError:
        	print 'no media :('
        # Want to disconnect after the first result?
        #self.disconnect()

    def on_error(self, status_code, data):
        print status_code, data

def watch_tags(tags='#cats'):
	print 'watch_tags',tags
	# Requires Authentication as of Twitter API v1.1
	stream = MyStreamer(APP_KEY, APP_SECRET,
						OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	stream.statuses.filter(track=tags)

watch_tags()
