from flask import Flask, Blueprint, request, Response, jsonify
from flask_login import LoginManager, login_user, current_user, login_required
import hashlib
from .utils import serialize_data, deserialize_data
from .models import db, User
from functools import wraps
import time
import base64


def _authenticate():
    return Response(
        'Please login', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def _load_user(username):
    return User.query.filter_by(username=u).first()


def _load_user_from_request(request):
    auth = request.authorization
    if auth is None:
        return None
    u, p = auth.username, auth.password
    user = User.query.filter_by(username=u).first()
    if user is None:
        return None
    if isinstance(p, unicode):
        p = p.encode('utf8')
    m = hashlib.md5()
    m.update(p)
    digest = m.hexdigest()
    if digest.lower() == user.password.lower():
        login_user(user)
        return user
    return None



def create_app(config_pyfile):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile(config_pyfile)
    db.init_app(app)
    login_manager = LoginManager(app)
    login_manager.user_loader(_load_user)
    login_manager.request_loader(_load_user_from_request)
    login_manager.unauthorized_handler(_authenticate)
    blueprint = Blueprint('bp', __name__)

    @blueprint.route('/auth', methods=['GET', 'POST'])
    def auth():
        auth = request.headers.get('Authorization')
        expired, invalid, data = deserialize_data(auth.replace('Bearer ', ''))
        if expired:
            return jsonify({
                'code': 401,
                'message': 'token expired'
            })
        if invalid:
            return jsonify({
                'code': 401,
                'message': 'invalid token'
            })
        return jsonify({
                'code': 200,
                'message': 'OK',
                'data': data
            })


    @blueprint.route('/sign', methods=['GET', 'POST'])
    @login_required
    def sign():
        access_id = request.args.get('access_id')
        tonce = request.args.get('tonce')
        now = time.time() * 1000
        if access_id and tonce and now - 10000 < int(tonce) < now + 10000:
            cu = current_user.to_json()
            cu['token'] = serialize_data(cu)
            return jsonify({
                'code': 200,
                'message': 'OK',
                'data': cu
            })
        return jsonify({
                'code': 401,
                'message': 'invalid request'
            })
    app.register_blueprint(blueprint, url_prefix=app.config.get('URL_PREFIX', ''))

    with app.app_context():
        db.create_all()

    return app
