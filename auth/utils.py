from config import JWT_SECRET, REDIS_URL
from itsdangerous import URLSafeTimedSerializer
import logging
import secrets
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
rate_limit_store = {}

# Per-IP rate limits for auth endpoints (prevent email bombing / OTP brute force)
IP_RATE_LIMITS = {
    "otp_send": (10, 900),      # max 10 OTP sends per IP per 15 min
    "otp_verify": (20, 900),    # max 20 verify attempts per IP per 15 min
}

def client_ip(request) -> str:
    """Extract real client IP, honoring Cloudflare/nginx proxy headers.

    Order matters: CF-Connecting-IP is set by the Cloudflare edge and cannot
    be spoofed by the client. X-Forwarded-For is only trusted because nginx
    overwrites it from CF-Connecting-IP before forwarding to the app.
    """
    cf = request.headers.get("cf-connecting-ip")
    if cf:
        return cf.split(",")[0].strip()
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def is_rate_limited(key: str, ip: str) -> bool:
    """Return True if the IP exceeded the limit for the given key."""
    limit, window = IP_RATE_LIMITS[key]
    if use_redis:
        rl_key = f"rl:{key}:{ip}"
        current = redis_client.get(rl_key)
        if current is None:
            redis_client.setex(rl_key, window, 1)
            return False
        if int(current) >= limit:
            return True
        redis_client.incr(rl_key)
        return False
    now = datetime.now(timezone.utc)
    store_key = (key, ip)
    timestamps = [
        t for t in rate_limit_store.get(store_key, [])
        if now - t < timedelta(seconds=window)
    ]
    if len(timestamps) >= limit:
        rate_limit_store[store_key] = timestamps
        return True
    timestamps.append(now)
    rate_limit_store[store_key] = timestamps
    return False

def generate_otp(length=6):
    """Generate a numeric OTP of specified length using a CSPRNG"""
    digits = string.digits
    return ''.join(secrets.choice(digits) for _ in range(length))

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

