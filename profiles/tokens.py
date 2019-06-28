from django.conf import settings
from django.contrib.auth.models import User
from itsdangerous import BadSignature, URLSafeSerializer


def make_confirmation_token(user, code):
    serializer = URLSafeSerializer(settings.SECRET_KEY)
    token = serializer.dumps([user.id, code])
    return token


def confirm_singup_token(token):
    """
    If token is not valid or user reuse it - returns None
    else - returns user (associated with token) with code attribute
    """
    serializer = URLSafeSerializer(settings.SECRET_KEY)
    try:
        data = serializer.loads(token)
    except BadSignature:
        return None
    user_id, code = data

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    if user.is_active or user.last_login is not None:
        # to prevent token reusing
        return None
    
    return user, code
