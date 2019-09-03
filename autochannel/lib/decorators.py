"""
init - version info
"""
import logging
from flask import abort, redirect, request, session 
from functools import wraps
from autochannel import db
from autochannel.site import site_functions
from autochannel.models import Guild, Category

LOG = logging.getLogger(__name__)

def is_authenticated():
  #LOG.info(f'SESSION INFO: {session.get("oauth2_token")}')
  return session.get('oauth2_token')

def login_required(view):
  @wraps(view)
  def view_wrapper(*args, **kwargs):
    if is_authenticated():
      return view(*args, **kwargs)
    else:
      return redirect('/api/login')
  return view_wrapper

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
      #guild_exists = Guild.query.filter_by(id = guild_id).first()

      guild_exists = db.session.query(Guild).get(guild_id)
      if not guild_exists:
        invite_url = site_functions.get_invite_link(guild_id)
        return redirect(invite_url)

      return f(*args, **kwargs)
    return wrapper