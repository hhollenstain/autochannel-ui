import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
#from flask_login import LoginManager
# from flask_mail import Mail
from autochannel.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = 'users.login'
# login_manager.login_message_category = 'info'
# mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    Bootstrap(app)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    # login_manager.init_app(app)
    # mail.init_app(app)


    from autochannel.api.routes import mod_api
    from autochannel.site.routes import mod_site
    from autochannel.errors.routes import mod_errors
    # from flaskblog.errors.handlers import errors
    app.register_blueprint(mod_api, url_prefix='/api')
    app.register_blueprint(mod_site)
    app.register_blueprint(mod_errors)

    return app