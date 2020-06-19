from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
import requests
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

class Country_City(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	country = db.Column(db.String(100), nullable=False)
	vity = db.Column(db.String(100), nullable=False)
	date = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Article %r>' % self.id

@app.route('/')
def index():

	if request.method == 'POST':
		country = request.form['country']
		city = request.form['city']

		c_c = Country_City(country=country, city=city)

		try:
			db.session.add(c_c)
			db.session.commit()
			return redirect(f'/<{c_c.country}>/<{c_c.city}>')
		except:
			return "Произошла ошибка"
	else:
		return render_template("home.html")

@app.route('/<country>/<city>')
def hello(city, country, temp=None, wind_sp=None, water=None, ob=None):
	url = f'https://api.weatherbit.io/v2.0/current?'
	coun_cit = Country_City.query.order_by(Country_City.date.desc()).all()
	response = requests.get(url, headers={'Accept': 'application/json'}, params={
	'city': city,
	'country': country,
	'key': '9c0161dc9dde495aa435108927f3b57a'
	})

	s = response.json()

	temp = f"Температура: {s['data'][0]['temp']} градусов"
	wind_sp = f"Скорость ветра: {s['data'][0]['wind_spd']} м/с"
	#temp_app f"Ощущается как: {s['data'][0]['app_temp']} градусов"
	water = f"Влажность: {s['data'][0]['rh']}" + "%"
	ob = s['data'][0]['clouds']
	if ob >= 75:
		ob = "Облачно"
	elif ob <= 60 and ob > 45:
		ob = "Пасмартно"
	else:
		ob = 'Солнечно'

	return render_template('hello.html', city=city, country=country, temp=temp, wind_sp=wind_sp, 
		water=water, ob=ob, coun_cit=coun_cit)