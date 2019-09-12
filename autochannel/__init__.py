import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
"""AC imports"""
from autochannel.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
compress = Compress()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    compress.init_app(app)

    from autochannel.api.routes import mod_api
    from autochannel.site.routes import mod_site
    from autochannel.errors.routes import mod_errors

    app.register_blueprint(mod_api, url_prefix='/api')
    app.register_blueprint(mod_site)
    app.register_blueprint(mod_errors)

    return app