import os
import logging
import requests
from flask import Flask, session, request, url_for, render_template, redirect, \
 jsonify, flash, abort, Response, Blueprint
from flask import current_app as app
from flask_bootstrap import Bootstrap
from requests_oauthlib import OAuth2Session
from itsdangerous import JSONWebSignatureSerializer
"""App imports"""
from autochannel.lib.decorators import login_required
from autochannel.lib import discordData
"""Api imports"""
from autochannel.api import api_functions
"""Data Imports"""
from autochannel.data import data_functions
from autochannel.models import Guild, Category
from autochannel import db

LOG = logging.getLogger(__name__)

mod_api = Blueprint('mod_api', __name__)

@login_required
@mod_api.route('/add-guild')
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
    LOG.debug(f'GUILD Added: {guild_id}')
    return redirect(url_for('mod_site.add_guild', guild_id=guild_id, user_id=session['api_token']['user_id'])) 

@mod_api.route('/callback')
def callback():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    if request.values.get('error'):
        return request.values['error']
    discord = api_functions.make_session(state=session.get('oauth2_state'))
    discord_token = discord.fetch_token(
        app.config['TOKEN_URL'],
        client_secret=app.config['OAUTH2_CLIENT_SECRET'],
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
    session['guilds'] = api_functions.get_managed_guilds()
    return redirect(url_for('mod_site.dashboard', user_id=session['api_token']['user_id']))
    
@mod_api.route('/update-enabled-cat',methods=['GET','POST'])
@login_required
def update_enabled_cats():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    msg=''
    channel_id = request.form.get('channel_id')
    enabled = request.form.get('enabled')
    data_functions.data_update_cat_enable(channel_id=channel_id, enabled=enabled)
    msg = 'Updated'
    return jsonify(data=msg)