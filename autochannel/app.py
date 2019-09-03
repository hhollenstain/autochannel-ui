import os
import logging
import coloredlogs
import requests
from flask import Flask, session, request, url_for, render_template, redirect, \
 jsonify, flash, abort, Response
from flask_bootstrap import Bootstrap
from requests_oauthlib import OAuth2Session
from itsdangerous import JSONWebSignatureSerializer
from autochannel.lib.decorators import login_required
from autochannel.lib import discordData
import autochannel.api
from autochannel.api.routes import mod_api
from autochannel.site.routes import mod
from autochannel.api import api_functions

LOG = logging.getLogger(__name__)

# """
# OAUTH2 client 
# """
# OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
# OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
# OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'

# """
# Discord specific
# """
# API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
# AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
# AVATAR_BASE_URL = "https://cdn.discordapp.com/avatars/"
# DEFAULT_AVATAR = "https://discordapp.com/assets/"\
#                 "1cbd08c76f8af6dddce02c5138971129.png"
# TOKEN_URL = API_BASE_URL + '/oauth2/token'

# AC_TOKEN = os.getenv('AC_TOKEN')

"""
Flask configs
"""
# template_dir = os.path.abspath('autochannel_frontend/dist')
# # app = Flask(__name__,
# #             static_folder = "./dist/static",
# #             template_folder = "./dist")
# app = Flask(__name__,
#             static_folder = f'{template_dir}/static',
#             template_folder = template_dir)

ac = Flask(__name__)

ac.register_blueprint(mod_api, url_prefix='/api')
#app.register_blueprint(site.routes.mod )

# @app.route('/')
# def hello():
#     return 'Hello Coder, you are up!'

# @app.route('/table.html')
# def table():
#     return render_template('layouts/default.html',
#                             content=render_template( 'pages/table.html') )

ac.debug = False
ac.config['SECRET_KEY'] = app.OAUTH2_CLIENT_SECRET
Bootstrap(ac)


if 'http://' in app.OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

@ac.route('/avatar-test')
def avatar_test():
    token = session['oauth2_token']
    user = get_user(token)
    return avatar(user)

def avatar(user):
    if user.get('avatar'):
        return app.AVATAR_BASE_URL + user['id'] + '/' + user['avatar'] + '.jpg'
    else:
        return app.DEFAULT_AVATAR

def token_updater(token):
    session['oauth2_token'] = token


# def make_session(token=None, state=None, scope=None):
#     return OAuth2Session(
#         client_id=OAUTH2_CLIENT_ID,
#         token=token,
#         state=state,
#         scope=scope,
#         redirect_uri=OAUTH2_REDIRECT_URI,
#         auto_refresh_kwargs={
#             'client_id': OAUTH2_CLIENT_ID,
#             'client_secret': OAUTH2_CLIENT_SECRET,
#         },
#         auto_refresh_url=TOKEN_URL,
#         token_updater=token_updater)

@login_required
@ac.route('/dashboard')
def index():
    #LOG.info("dashboard lOGOSDFDSFSFSF")
    if 'oauth2_token' in session:
        return redirect(url_for('.me'))
    
    return redirect(url_for('mod_api.login')) 


@ac.route('/dashboard/<user_id>')
@login_required
def dashboard(user_id):
   #return f'USER ID: {user_id}'
   #guilds = user_id
    guilds = api_functions.get_managed_guilds()
#    return render_template('layouts/default.html',
#                             content=render_template(
#                             'pages/selectserver.html', guilds=guilds,
#                             user_id=user_id))
    return render_template('pages/selectserver-boot.html', guilds=guilds, user_id=user_id)

@ac.route('/dashboard/<user_id>/<guild_id>')
@login_required
def dashboard_guild(user_id=None, guild_id=None):
    channels = api_functions.get_guild_channels(guild_id)
    categories = api_functions.get_guild_categories(guild_id)
    if channels:
        #categories = api_functions.get_guild_categories(channels)
        return jsonify(guild_id=guild_id, categories=categories)
    
    return jsonify(error='BOT Not added to this guild')

    

# @app.route('/api/login')
# def login():
#     # scope = request.args.get(
#     #     'scope',
#     #     'identify email connections guilds guilds.join')
#     scope = ['identify', 'email', 'guilds', 'connections', 'guilds.join']
#     discord = make_session(scope=scope)
#     authorization_url, state = discord.authorization_url(
#         AUTHORIZATION_BASE_URL,
#         # access_type="offline"
#     )
#     session['oauth2_state'] = state
#     return redirect(authorization_url) 

@ac.route('/ohno')
def ohno():
    return jsonify(error="something went wrong")

@ac.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    discord_token = discord.fetch_token(
        app.TOKEN_URL,
        client_secret=app.OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    if not discord_token:
        return redirect(url_for('ohno'))

    session['oauth2_token'] = discord_token

# Fetch the user
    user = get_user(discord_token)
    # if not user:
    #     return redirect(url_for('logout'))
    # Generate api_key from user_id
    serializer = JSONWebSignatureSerializer(app.config['SECRET_KEY'])
    api_key = str(serializer.dumps({'user_id': user['id']}))
    # Store api_token in client session
    api_token = {
        'api_key': api_key,
        'user_id': user['id']
    }
    session.permanent = True
    session['api_token'] = api_token
    #return redirect(url_for('.me'))
    return redirect(url_for('dashboard', user_id=session['api_token']['user_id']))

@ac.route('/me')
@login_required
def me():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(app.API_BASE_URL + '/users/@me').json()
    guilds = discord.get(app.API_BASE_URL + '/users/@me/guilds').json()
    connections = discord.get(app.API_BASE_URL + '/users/@me/connections').json()
    return jsonify(user=user, guilds=guilds, connections=connections)

@ac.route('/whoami')
@login_required
def whoami():
    token = session['oauth2_token']
    return jsonify(user=get_user(token))

@ac.route('/api/user')
@login_required
def user():
    token = session['oauth2_token']
    #user_info = get_user(token)
    return jsonify(user=get_user(token))

# def user_data_builder(user):
    
#     return user_data



@ac.route('/managed-guilds')
@login_required
def managed_guilds():
    token = session['oauth2_token']
    user = get_user(token)
    guilds = api_functions.get_user_guilds(token)
    user_servers = sorted(
        api_functions.get_user_managed_servers(user, guilds),
        key=lambda s: s['name'].lower()
    )
    guild_data = discordData.parse_managed_guilds(user_servers)
    #return jsonify(managedGuilds=user_servers)
    return jsonify(managedGuilds=guild_data)


@ac.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@ac.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('pages/404.html'), 404

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def catch_all(path):
#     if app.debug:
#         return requests.get('http://localhost:8080/{}'.format(path)).text
#     return render_template("index.html")

def get_guild_channels(server_id, voice=True, text=True):
    headers = {'Authorization': 'Bot '+app.AC_TOKEN}
    r = requests.get(API_BASE_URL+'/guilds/{}/channels'.format(server_id),
                     headers=headers)
    if r.status_code == 200:
        channels = r.json()
        if not voice:
            channels = list(filter(lambda c: c['type'] != 'voice',
                                   channels))
        if not text:
            channels = list(filter(lambda c: c['type'] != 'text', channels))
        return channels
    return None