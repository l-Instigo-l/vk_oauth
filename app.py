import requests
import json
import datetime

from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = "super secret key"
app.permanent_session_lifetime = datetime.timedelta(days=31)
app.config['OAUTH_CREDENTIALS'] = {
	'vk': {
		'id': 'app_id',
		'secret': 'secret_key'
	}
}

@app.route('/')
def index():
	if 'login_status' in session:
		print(session.get('login_status'))
		print(session.get('name'))
		if session.get('login_status') is False:
			return render_template('index.html')
		
		else:
			print(session.get('login_status'))
			print(session.get('name'))
			return result()
	else:
		print(session.get('login_status'))
		print(session.get('name'))
		return render_template('index.html')

@app.route("/auth", methods=["POST"])
def auth():
	url = 'https://oauth.vk.com/authorize?client_id=' + app.config['OAUTH_CREDENTIALS']['vk']['id'] + '&display=page&redirect_uri=http://localhost:5000/result&scope=friends&response_type=code&v=5.95'
	return redirect(url)

@app.route('/result', methods=["GET", "POST"])
def result():
	if request.args.get('code'):
		session['code'] = request.args.get('code')
		url = 'https://oauth.vk.com/access_token?client_id=' + app.config['OAUTH_CREDENTIALS']['vk']['id'] + '&client_secret=' + app.config['OAUTH_CREDENTIALS']['vk']['secret'] + '&redirect_uri=http://localhost:5000/result&code=' + session['code']
		json_data = requests.get(url)
		session['token_response'] = json_data.json()
		return redirect('/result')
	elif 'error' in request.args:
		return request.args
	else:
		if 'access_token' in session.get('token_response'):
			url2 = 'https://api.vk.com/method/friends.get?count=5&fields=nickname,photo_100&order=random&access_token=' + session['token_response']['access_token'] + '&v=5.95'
			session['friends'] = requests.get(url2).json()

			name_url = 'https://api.vk.com/method/users.get?fields=photo_100&access_token=' + session['token_response']['access_token'] + '&v=5.95'
			session['name'] = requests.get(name_url).json()

			session['login_status'] = True
			

			return render_template('auth_success.html', friends=session['friends']['response']['items'], name=session['name']['response'][0])
		else:
			return str(session['token_response'])

@app.route("/logout", methods=["POST"])
def logout():
	session['login_status'] = False
	print(session.get('friends'))
	print(session.get('token_response'))
	
	return index()

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
