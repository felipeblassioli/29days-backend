from app import db, twitter
from peewee import *

def lookup_status(self, **params):
	"""Returns fully-hydrated tweet objects for up to 100 tweets per
	request, as specified by comma-separated values passed to the id
	parameter.

	Docs: https://dev.twitter.com/docs/api/1.1/get/statuses/lookup

	"""
	return self.post('statuses/lookup', params=params)

import json
def lookup_tweets(ids):
	ret = []
	print ids
	try:
		print ids
		print dir(twitter)
		tweets = lookup_status(twitter,id=ids)
		#tweets = twitter.post('statuses/lookup', id=ids)
		print "lookup_tweets={}".format(len(tweets))
		for tweet in tweets:
			try:
				print 'favorite_count={} retweet_count={}'.format(tweet['favorite_count'], tweet['retweet_count'])
				ret.append({"id": tweet['id_str'], 
							"favorite_count":tweet['favorite_count'], 
							"retweet_count":tweet['retweet_count']})
			except KeyError:
				print 'error'
				print json.dumps(tweet, indent=4)
	except TwythonError as e:
		print e
		return None
	return ret

import json
class CountryCount(db.Model):
	country = CharField(default='')
	count = IntegerField(default=0)

	@staticmethod
	def increment(country):
		try:
			counter = CountryCount.get(CountryCount.country == country)
			counter.save()
		except CountryCount.DoesNotExist:
			counter = CountryCount()
			counter.country = 1
			counter.save(force_insert=True)

class User(db.Model):
	twitter_user_id = CharField(default='')
	twitter_tweet_id = CharField(default='')
	media_url = CharField(default='')
	tag_country = CharField(default='')
	tag_challenge = CharField(default='')
	body = TextField(default='')
	points = IntegerField(default=0)
	favorite_count = IntegerField(default=0)
	retweet_count = IntegerField(default=0)

	def _points(self):
		return (3*self.favorite_count + self.retweet_count)*100

	@property
	def simple(self):
		return {"url": self.media_url, "favorite_count": self.favorite_count, "retweet_count": self.retweet_count, "id":self.id}
	
	@staticmethod
	def find_by_twitter_id(twitter_id):
		try:
			usr = User.get(User.twitter_id == twitter_id)
		except User.DoesNotExist:
			usr = None
		return usr

	@staticmethod
	def find_user_id(screen_name):
		try:
			user = twitter.lookup_user(screen_name=screen_name)
			try:
				return user[0]['id_str']
			except KeyError:
				return "not found"
		except TwythonError as e:
			print e
			return 'not found'

	@staticmethod
	def save_tweet_data(user_id,tweet_id,json_data,country,challenge):
		usr = User()
		usr.twitter_user_id = user_id
		usr.twitter_tweet_id = tweet_id
		usr.media_url = json_data['media_url']
		usr.tag_country = country or ''
		usr.tag_challenge = challenge or ''
		usr.body = json.dumps(json_data)
		usr.save(force_insert=True)
		if country != None: CountryCount.increment(country)

	@staticmethod
	def update_points():
		tweet_ids = [t.twitter_tweet_id for t in User.select()]
		n = len(tweet_ids)-1
		while(n>=0):
			m = n-100 if n >= 100 else 0
			print '>>>>>>>>>>>>>>m={}n={}totSub={}'.format(m,n,len(tweet_ids[m:n]))
			ids = ','.join(tweet_ids[m:n])
			n = n - 100
			tweets = lookup_tweets(ids)
			print "totTweets={}".format(len(tweets))
			for t in tweets:
				try:
					tweet = User.get(User.twitter_tweet_id == t['id'])
					tweet.favorite_count = t['favorite_count']
					tweet.retweet_count = t['retweet_count']
					tweet.points = tweet._points()
					print tweet.twitter_user_id, tweet.favorite_count, tweet.retweet_count
					tweet.save()
				except User.DoesNotExist:
					pass

	@staticmethod
	def get_challenges(user_id, screen_name):
		ret = []
		if user_id == None:
			user_id = User.find_user_id(screen_name)

		l_challenges = []
		print 'get_challenges for usr_id={}'.format(user_id)
		for tweet in User.select().where(User.twitter_user_id == user_id).order_by(User.id.desc()):
			cha = tweet.tag_challenge
			if cha != '' and cha not in l_challenges:
				l_challenges.append(cha)
				ret.append({"challenge": cha,"url": tweet.media_url})
				#print '>>>>>>>>>>>>>>',tweet['media_url']
		return ret



class UserRanking(db.Model):
	twitter_user_id = CharField(default='')
	points = IntegerField(default=0)

	@staticmethod
	def update_points():
		pass
		# ret = []
		# User.update_points()
		# points = {}
		# for tweet in User.select():
		# 	usr_id = tweet.twitter_user_id

class UserAuth(db.Model):
	twitter_user_id = CharField(default='')
	email = CharField(default='')
	screen_name = CharField(default='')

	@staticmethod
	def add_user_credentials(screen_name,email):
		usr = UserAuth()
		usr.screen_name = screen_name
		usr.email = email
		usr.twitter_user_id = User.find_user_id(screen_name)
		usr.save(force_insert=True)

User.create_table(True)
CountryCount.create_table(True)
UserRanking.create_table(True)
UserAuth.create_table(True)