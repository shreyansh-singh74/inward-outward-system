from config import JWT_SECRET, REDIS_URL
from itsdangerous import URLSafeTimedSerializer
import logging
import random
import string
import bcrypt
import json
from datetime import datetime, timezone, timedelta
import redis

serializer = URLSafeTimedSerializer(secret_key=JWT_SECRET, salt="email-configuration")

# Initialize Redis client with fallback to in-memory if Redis is unreachable
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    use_redis = True
except Exception as e:
    logging.warning(f"Redis not available, falling back to in-memory store: {e}")
    use_redis = False

otp_store = {}
user_reg_data = {}

def generate_otp(length=6):
    """Generate a numeric OTP of specified length"""
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))

def store_otp(email, otp, expiry_minutes=5):
    """Store OTP with expiration time"""
    hashed_otp = bcrypt.hashpw(otp.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    if use_redis:
        data = {
            'hashed_otp': hashed_otp,
            'attempts': 0,
            'last_sent': datetime.now(timezone.utc).isoformat()
        }
        redis_client.setex(f"otp:{email}", timedelta(minutes=expiry_minutes), json.dumps(data))
    else:
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
        otp_store[email] = {
            'hashed_otp': hashed_otp,
            'expiry': expiry_time,
            'attempts': 0,
            'last_sent': datetime.now(timezone.utc)
        }
    return True

def store_user_registration_data(email, name, department):
    """Store user registration data temporarily until OTP verification"""
    if use_redis:
        data = {
            'name': name,
            'department': department,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        redis_client.setex(f"reg:{email}", timedelta(minutes=30), json.dumps(data))
    else:
        user_reg_data[email] = {
            'name': name,
            'department': department,
            'timestamp': datetime.now(timezone.utc)
        }

def get_user_registration_data(email):
    """Retrieve stored user registration data"""
    if use_redis:
        val = redis_client.get(f"reg:{email}")
        if val:
            redis_client.delete(f"reg:{email}")
            return json.loads(val)
        return None
    else:
        if email in user_reg_data:
            data = user_reg_data[email]
            del user_reg_data[email]
            return data
        return None

def verify_otp(email, otp):
    """Verify if OTP is valid and not expired"""
    if use_redis:
        val = redis_client.get(f"otp:{email}")
        if not val:
            return False
        otp_data = json.loads(val)
        otp_data['attempts'] += 1
        if otp_data['attempts'] > 3:
            redis_client.delete(f"otp:{email}")
            return False
        
        is_valid = bcrypt.checkpw(otp.encode('utf-8'), otp_data['hashed_otp'].encode('utf-8'))
        if is_valid:
            redis_client.delete(f"otp:{email}")
        else:
            # Update attempts count back to redis
            ttl = redis_client.ttl(f"otp:{email}")
            if ttl > 0:
                redis_client.setex(f"otp:{email}", ttl, json.dumps(otp_data))
        return is_valid
    else:
        if email not in otp_store:
            return False
        otp_data = otp_store[email]
        if datetime.now(timezone.utc) > otp_data['expiry']:
            del otp_store[email]
            return False
        otp_data['attempts'] += 1
        if otp_data['attempts'] > 3:
            del otp_store[email]
            return False
        is_valid = bcrypt.checkpw(otp.encode('utf-8'), otp_data['hashed_otp'].encode('utf-8'))
        if is_valid:
            del otp_store[email]
        return is_valid

def can_send_new_otp(email):
    """Check if we can send a new OTP (rate limiting)"""
    if use_redis:
        val = redis_client.get(f"otp:{email}")
        if not val:
            return True
        otp_data = json.loads(val)
        last_sent = datetime.fromisoformat(otp_data['last_sent'])
        time_since_last = datetime.now(timezone.utc) - last_sent
        return time_since_last.total_seconds() >= 60
    else:
        if email not in otp_store:
            return True
        time_since_last = datetime.now(timezone.utc) - otp_store[email]['last_sent']
        return time_since_last.total_seconds() >= 60

def cleanup_expired_data():
    """Clean up expired data (run periodically if using memory)"""
    if use_redis:
        return
    now = datetime.now(timezone.utc)
    for email in list(otp_store.keys()):
        if now > otp_store[email]['expiry']:
            del otp_store[email]
    for email in list(user_reg_data.keys()):
        if (now - user_reg_data[email]['timestamp']).total_seconds() > 1800:
            del user_reg_data[email]

def create_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))
        return None

