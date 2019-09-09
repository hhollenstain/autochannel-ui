"""
init - version info
"""
import logging
from flask import abort, redirect, request, session 
from functools import wraps
"""AC Imports"""
from autochannel import db
from autochannel.site import site_functions
from autochannel.models import Guild, Category
from autochannel.data import data_functions
from autochannel.api import api_functions

LOG = logging.getLogger(__name__)

def is_authenticated():
  """[summary]
  
  Returns:
      [type] -- [description]
  """
  return session.get('oauth2_token')

def login_required(view):
  """[summary]
  
  Arguments:
      view {[type]} -- [description]
  
  Returns:
      [type] -- [description]
  """
  @wraps(view)
  def view_wrapper(*args, **kwargs):
    if is_authenticated():
      return view(*args, **kwargs)
    else:
      return redirect('/api/login')
  return view_wrapper


def guild_owner_check(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      """Checks if the guild is added by simply checking the guild ID in the database backend
      
      Arguments:
          f {fucntion} -- the wrapped function to test if guild is added
      
      Returns:
          either the function or redirect to add bot to the discord server
      """

      guild_id = kwargs.get('guild_id')
      discord_guilds = api_functions.get_managed_guilds()
      session_guilds = [discord_guilds[k]['id'] for k in (discord_guilds.keys())]
      if str(guild_id) not in session_guilds:
        LOG.info('NOT YOUR GUILD')
        LOG.info(session['guilds'])
        LOG.info(session_guilds)
      else:
        LOG.info('found your guild')
        LOG.info(session_guilds)

      # if not guild_exists:
      #   invite_url = site_functions.get_invite_link(guild_id)
      #   return redirect(invite_url)

      return f(*args, **kwargs)
    return wrapper

def guild_check(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      """Checks if the guild is added by simply checking the guild ID in the database backend
      
      Arguments:
          f {fucntion} -- the wrapped function to test if guild is added
      
      Returns:
          either the function or redirect to add bot to the discord server
      """

      guild_id = kwargs.get('guild_id')
     # guild_exists = db.session.query(Guild).get(guild_id)
      guild_exists = data_functions.get_guild_from_db(guild_id)

      if not guild_exists:
        invite_url = site_functions.get_invite_link(guild_id)
        return redirect(invite_url)

      return f(*args, **kwargs)
    return wrapper