import logging

from flask import Blueprint, jsonify, render_template, request

LOG = logging.getLogger(__name__)

mod_errors = Blueprint('mod_errors', __name__)


@mod_errors.route('/404')
def ac_404():
    return render_template('pages/404.html'), 404


@mod_errors.route('/<path:path>')
def catch_all(path):
    return render_template('pages/404.html'), 404


@mod_errors.errorhandler(404)
@mod_errors.errorhandler(405)
def handle_http_error(ex):
    """Return JSON for /api/* paths; HTML 404 page elsewhere."""
    if request.path.startswith('/api/'):
        code = getattr(ex, 'code', None) or 404
        return jsonify(error=str(ex)), code
    return render_template('pages/404.html'), 404
