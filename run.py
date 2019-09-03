import os
import logging
import coloredlogs
from waitress import serve
from autochannel.lib import utils
from autochannel import create_app

LOG = logging.getLogger(__name__)

def main():
    args = utils.parse_arguments()
    logging.basicConfig(level=logging.INFO)
    coloredlogs.install(level=0,
                        fmt="[%(asctime)s][%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                        isatty=True)
    if args.debug:
        l_level = logging.DEBUG
        app.debug = True
    else:
        l_level = logging.INFO

    logging.getLogger(__package__).setLevel(l_level)
    logging.getLogger('websockets.protocol').setLevel(l_level)
    logging.getLogger('urllib3').setLevel(l_level)
    app = create_app()

    if 'http://' in app.config['OAUTH2_REDIRECT_URI']:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
    app.run()
    #serve(app, listen='0.0.0.0:5000')

# if __name__ == "__main__":
#     main()