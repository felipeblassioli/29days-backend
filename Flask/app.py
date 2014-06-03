# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_peewee.db import Database
from flask import render_template
from twython import Twython, TwythonError
import sendgrid

countries = [u'alemanha',u'argentina',u'argélia',u'austrália',u'bélgica',u'brasil',u'bósnia',u'camarões',u'chile',u'colombia',u'costadomarfim',u'costarica',u'coreiadosul',u'croácia',u'eua',u'equador',u'espanha',u'frança',u'gana',u'grécia',u'holanda',u'honduras',u'inglaterra',u'itália',u'irã',u'japão',u'méxico',u'nigéria',u'portugal',u'rússia',u'suíça',u'uruguai']
challenges = ['hadouken','vemprarua','amornacopa','pettorcedor']

DATABASE = {
	'name': 'vintenove_2',
	'engine': 'peewee.MySQLDatabase',
	'user': 'root',
	'passwd': ''
}
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
db = Database(app)

APP_KEY = 'vko3p8bk1WE1BBu8vV5xzfHQG'
APP_SECRET = '6mKL4xPJFXT62OP1PeVVdQGFBS66lCtXHhIb81zqGWbBQhnb2L'
OAUTH_TOKEN = '228101273-d2CC5EdBwGipJlpyO3fsi5eSzmJlqc0D2BpfuqdG'
OAUTH_TOKEN_SECRET = 'aDZowFcdPIwWvWOYZ51djy8AcwHqEGDvZc6b846FhxOwc'
# Requires Authentication as of Twitter API v1.1
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

SENDGRID_USERNAME = 'felipeblassioli'
SENDGRID_PASSWORD = 'abacate123'
sg = sendgrid.SendGridClient(SENDGRID_USERNAME, SENDGRID_PASSWORD)

#twitter.lookup_status = lookup_status
@app.route('/')
def hello_world():
	return 'Hello World!'

import models
@app.route('/images/view')
def show_images():
	img_arr = [ user.media_url for user in models.User.select() ]
	return render_template('images.html', images=img_arr)

def get_name(usr_id):
	try:
		user = twitter.lookup_user(user_id=usr_id)
		try:
			return user[0]['name']
		except KeyError:
			return "none"
	except TwythonError as e:
		print e
		return 'none'

@app.route('/images/friends')
def images_friends():
	ids = request.args.get('ids',[]).split(',')
	print ids
	ret = {}
	for usr_id in ids:
		urls = []
		print 'usr_id',usr_id
		for usr in models.User.select().where(models.User.twitter_user_id == usr_id):
			urls.append(usr.media_url)
		if len(urls) > 0: ret[get_name(usr_id)] = urls
	return jsonify(ret)

@app.route('/images')
def images():
	ret = {}
	dict_countries = {}
	dict_challenges = {}
	for c in countries: dict_countries[c] = []
	for c in challenges: dict_challenges[c] = []
	for tweet in models.User.select().order_by(models.User.id.desc()):
		if tweet.tag_challenge != '' and tweet.tag_challenge != None:
			try:
				dict_challenges[tweet.tag_challenge].append(tweet.simple)
			except KeyError:
				pass
		if tweet.tag_country != '' and tweet.tag_country != None:
			try:
				dict_countries[tweet.tag_country].append(tweet.simple)
			except KeyError:
				pass
	a_countries = [{"country": c, "img": dict_countries[c]} for c in countries]
	a_challenges = [{"name": c, "img": dict_challenges[c]} for c in challenges]
	ret = {"challenges": a_challenges, "countries": a_countries}
	return jsonify(ret)

from peewee import fn
@app.route('/users/rank')
def users_rank():
	arr = []
	fsum = fn.sum(models.User.points)
	for s in models.User.select(models.User.twitter_user_id, 
								fsum.alias('points')).group_by(models.User.twitter_user_id).order_by(fsum):
		arr.append({"user_id": s.twitter_user_id, "points": s.points})
	return jsonify({"data": arr})

@app.route('/users/rank/update')
def rank_update():
	models.User.update_points()
	return 'ok'

@app.route('/challenges/congratz')
def congratulate():
	l_challenges = models.User.get_challenges(request.args.get('user_id',None), request.args.get('screen_name',None))
	html = render_template('congratz.html', images=l_challenges)	
	print html
	message = sendgrid.Mail()
	message.add_to('Felipe Blassioli <felipeblassioli@gmail.com>')
	message.set_subject('[Desafio-29days] Parabéns! Você completou todos os desafios!')
	message.set_html(html)
	#message.set_text('Body')
	message.set_from('Felipe Blassioli <felipeblassioli@gmail.com>')
	status, msg = sg.send(message)
	return 'ok'

# Isso é muuuuuuito errado, mas fui forçado
@app.route('/users/add')
def users():
	screen_name = request.args.get('screen_name','')
	email = request.args.get('email','')
	models.UserAuth.add_user_credentials(screen_name,email)
	return 'ok'

import logging
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
if __name__ == '__main__':
	app.run()
