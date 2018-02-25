from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from base64 import b64encode, b64decode
from flask import current_app
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


def _get_serializer():
    ctx = stack.top
    if ctx is not None:
        if not hasattr(ctx, 'safeserializer'):
            ctx.safeserializer = URLSafeTimedSerializer(
                current_app.secret_key
            )
    return ctx.safeserializer


def deserialize_data(token, max_age=24*3600):
    serializer = _get_serializer()
    data = None
    expired, invalid = False, False
    try:
        data = serializer.loads(b64decode(token))
    except SignatureExpired:
        expired = True
    except:
        invalid = True
    return expired, invalid, data


def serialize_data(data):
    serializer = _get_serializer()
    return b64encode(serializer.dumps(data))
