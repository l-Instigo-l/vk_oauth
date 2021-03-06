import requests
import json
import datetime

from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = "12super secret key21"
app.permanent_session_lifetime = datetime.timedelta(days=31)
app.config['OAUTH_CREDENTIALS'] = {
	'vk': {
		'id': 'app_id',
		'secret': 'app_secret_key'
	}
}

@app.route('/')
def index():
	if 'login' in session:
		if session.get('login') is False:
			return render_template('index.html')
		
		elif session.get('login') is True:
			return result()
	else:
		return render_template('index.html')

@app.route('/auth', methods=["POST"])
def auth():
	url = 'https://oauth.vk.com/authorize?client_id=' + app.config['OAUTH_CREDENTIALS']['vk']['id'] + '&display=page&redirect_uri=http://localhost:5000/result&scope=friends,offline&response_type=code&v=5.95'
	return redirect(url)

@app.route('/result', methods=["GET", "POST"])
def result():
	session['login'] = True
	if request.args.get('code'):
		session['code'] = request.args.get('code')
		url = 'https://oauth.vk.com/access_token?client_id=' + app.config['OAUTH_CREDENTIALS']['vk']['id'] + '&client_secret=' + app.config['OAUTH_CREDENTIALS']['vk']['secret'] + '&redirect_uri=http://localhost:5000/result&code=' + session['code']
		json_data = requests.get(url)
		session['token-response'] = json_data.json()
		return redirect('/result')

	elif 'error' in request.args:
		return str(request.args)

	else:
		if 'access_token' in session.get('token-response'):
		
			url2 = 'https://api.vk.com/method/friends.get?count=5&fields=nickname,photo_100&order=random&access_token=' + session['token-response']['access_token'] + '&v=5.95'
			friends = requests.get(url2).json()
			session['friends'] = friends

			name_url = 'https://api.vk.com/method/users.get?fields=photo_100&access_token=' + session['token-response']['access_token'] + '&v=5.95'
			name = requests.get(name_url).json()
			session['name'] = name
			session['login'] = True
			return render_template('auth_success.html', friends=session['friends']['response']['items'], name=session['name']['response'][0])
		
		elif session.get('token-response') is None:
			return str(session['token-response'])

@app.route('/logout', methods=["POST", "GET"])
def logout():
	session['login'] = False
	return render_template('index.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
