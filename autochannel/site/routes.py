import os
import logging
import requests
from flask import Flask, Blueprint, session, request, url_for, render_template, redirect, \
 jsonify, flash, abort, Response
from flask import current_app as app
from flask_bootstrap import Bootstrap
from requests_oauthlib import OAuth2Session
from itsdangerous import JSONWebSignatureSerializer
from autochannel import db
from autochannel.models import Guild, Category
from autochannel.lib.decorators import login_required, guild_check
from autochannel.lib import discordData
from autochannel.api import api_functions
from autochannel.data import data_functions, data_forms


LOG = logging.getLogger(__name__)

mod_site = Blueprint('mod_site', __name__)

@mod_site.route('/')
def index():
    return render_template('pages/index.html')

@mod_site.route('/avatar-test')
def avatar_test():
    token = session['oauth2_token']
    user = api_functions.get_user(token)
    return avatar(user)

def avatar(user):
    if user.get('avatar'):
        return app.config['AVATAR_BASE_URL'] + user['id'] + '/' + user['avatar'] + '.jpg'
    else:
        return app.config['DEFAULT_AVATAR']

def token_updater(token):
    session['oauth2_token'] = token

@login_required
@mod_site.route('/dashboard',  strict_slashes=False)
def dashboard_index():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    if 'oauth2_token' in session:
        return redirect(url_for('mod_site.dashboard', user_id=session['api_token']['user_id']))
    
    return redirect(url_for('mod_api.login')) 

@login_required
@mod_site.route('/dashboard/add-guild')
def add_guild():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    guild_id = request.args.get('guild_id')
    categories = api_functions.get_guild_categories(guild_id)
    guild = api_functions.get_guild(guild_id)
    guild_data = discordData.parse_managed_guilds(guild)
    guild_id_add = Guild(id=guild_id)
    db.session.add(guild_id_add)
    db.session.commit()
    LOG.info(f'GUILD ID: {guild_id}')
    return "worked?"


@mod_site.route('/dashboard/<user_id>')
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

@mod_site.route('/dashboard/<user_id>/<guild_id>/form', methods=['GET', 'POST'])
@login_required
@guild_check
def dashboard_guild_form(user_id=None, guild_id=None):
    guild = Guild.query.get_or_404(guild_id)
    cat = Category.query.filter_by(guild_id=guild_id).all()
    form = data_forms.GuildForm(request.form, obj=guild)
    form.populate_obj(guild)
    LOG.info(cat)
    LOG.info(guild)
    LOG.info(form.categories)

    return render_template('pages/guild-form.html', form=form, user_id=user_id, guild_id=guild_id)

@mod_site.route('/dashboard/<user_id>/<guild_id>/db')
@login_required
@guild_check
def dashboard_guild_db(user_id=None, guild_id=None):
    guild = Guild.query.filter_by(id = guild_id).first()
    guild_data = guild.get_categories()
    return render_template('pages/guild-db.html', guild=guild_data)

@mod_site.route('/dashboard/<user_id>/<guild_id>')
@login_required
@guild_check
def dashboard_guild(user_id=None, guild_id=None):
    """[summary]
    
    Keyword Arguments:
        user_id {[type]} -- [description] (default: {None})
        guild_id {[type]} -- [description] (default: {None})
    
    Returns:
        [type] -- [description]
    """
    #channels = api_functions.get_guild_channels(guild_id)
    discord_categories = api_functions.get_guild_categories(guild_id)
    data_functions.data_update_guild_categories(categories=discord_categories, guild_id=guild_id)
    db_categories = Guild.query.get(guild_id).get_categories()
    guild = api_functions.get_guild(guild_id)
    guild_data = discordData.parse_managed_guilds(guild)
    
    if discord_categories:
        return render_template('pages/guild-categories.html', db_categories=db_categories, discord_categories=discord_categories, guild=guild_data)

    return jsonify(error='BOT Not added to this guild or no')

@mod_site.route('/ohno')
def ohno():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    #return jsonify(error="something went wrong")
    return render_template('pages/ohno.html')

@mod_site.route('/callback')
def callback():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
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
    user = api_functions.get_user(discord_token)
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

@mod_site.route('/me')
@login_required
def me():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    discord = api_functions.make_session(token=session.get('oauth2_token'))
    user = discord.get(app.config['API_BASE_URL'] + '/users/@me').json()
    guilds = discord.get(app.config['API_BASE_URL'] + '/users/@me/guilds').json()
    connections = discord.get(app.config['API_BASE_URL'] + '/users/@me/connections').json()
    return jsonify(user=user, guilds=guilds, connections=connections)

@mod_site.route('/whoami')
@login_required
def whoami():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    token = session['oauth2_token']
    return jsonify(user=api_functions.get_user(token))

@mod_site.route('/api/user')
@login_required
def user():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    token = session['oauth2_token']
    #user_info = get_user(token)
    return jsonify(user=api_functions.get_user(token))

# def user_data_builder(user):
    
#     return user_data



@mod_site.route('/managed-guilds')
@login_required
def managed_guilds():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    token = session['oauth2_token']
    user = api_functions.get_user(token)
    guilds = api_functions.get_user_guilds(token)
    user_servers = sorted(
        api_functions.get_user_managed_servers(user, guilds),
        key=lambda s: s['name'].lower()
    )
    guild_data = discordData.parse_managed_guilds(user_servers)
    return jsonify(managedGuilds=guild_data)

@mod_site.route('/login')
def login():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    # scope = request.args.get(
    #     'scope',
    #     'identify email connections guilds guilds.join')
    scope = ['identify', 'email', 'guilds', 'connections', 'guilds.join']
    discord = api_functions.make_session(scope=scope)
    authorization_url, state = discord.authorization_url(
        app.config['AUTHORIZATION_BASE_URL'],
        # access_type="offline"
    )
    session['oauth2_state'] = state
    return redirect(authorization_url) 

@mod_site.route('/logout')
def logout():
    """[summary]

    Returns:
        [type] -- [description]
    """
    session.clear()
    return redirect(url_for('mod_site.index'))

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def catch_all(path):
#     if app.debug:
#         return requests.get('http://localhost:8080/{}'.format(path)).text
#     return render_template("index.html")