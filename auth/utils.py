from config import JWT_SECRET
from itsdangerous import URLSafeTimedSerializer
import logging

serializer = URLSafeTimedSerializer(secret_key=JWT_SECRET, salt="email-configuration")


def create_url_safe_token(data: dict):

    token = serializer.dumps(data)

    return token


def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)

        return token_data

    except Exception as e:
        logging.error(str(e))
