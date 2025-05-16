from config import JWT_SECRET
from itsdangerous import URLSafeTimedSerializer
import logging
import random
import string
import bcrypt
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.models import User, VerificationToken

serializer = URLSafeTimedSerializer(secret_key=JWT_SECRET, salt="email-configuration")

# In-memory OTP storage with expiry times (in a production app, use Redis instead)
otp_store = {}

# In-memory temporary user data storage
user_reg_data = {}

def generate_otp(length=6):
    """Generate a numeric OTP of specified length"""
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))

def store_otp(email, otp, expiry_minutes=5):
    """Store OTP with expiration time"""
    # Hash the OTP before storing
    hashed_otp = bcrypt.hashpw(otp.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
    
    # Store in our in-memory dictionary
    otp_store[email] = {
        'hashed_otp': hashed_otp,
        'expiry': expiry_time,
        'attempts': 0,
        'last_sent': datetime.now()
    }
    return True

def store_user_registration_data(email, name, department):
    """Store user registration data temporarily until OTP verification"""
    user_reg_data[email] = {
        'name': name,
        'department': department,
        'timestamp': datetime.now()
    }

def get_user_registration_data(email):
    """Retrieve stored user registration data"""
    if email in user_reg_data:
        data = user_reg_data[email]
        # Delete after retrieval to clean up
        del user_reg_data[email]
        return data
    return None

def verify_otp(email, otp):
    """Verify if OTP is valid and not expired"""
    if email not in otp_store:
        return False
    
    otp_data = otp_store[email]
    
    # Check if OTP is expired
    if datetime.now() > otp_data['expiry']:
        del otp_store[email]  # Clean up expired OTP
        return False
    
    # Increment attempts counter
    otp_data['attempts'] += 1
    
    # Check if max attempts reached (3 attempts)
    if otp_data['attempts'] > 3:
        del otp_store[email]
        return False
    
    # Verify OTP
    is_valid = bcrypt.checkpw(otp.encode('utf-8'), otp_data['hashed_otp'].encode('utf-8'))
    
    # If valid, remove from store (one-time use)
    if is_valid:
        del otp_store[email]
    
    return is_valid

def can_send_new_otp(email):
    """Check if we can send a new OTP (rate limiting)"""
    if email not in otp_store:
        return True
    
    # Allow new OTP once per minute
    time_since_last = datetime.now() - otp_store[email]['last_sent']
    return time_since_last.total_seconds() >= 60

def cleanup_expired_data():
    """Clean up expired data (run periodically)"""
    now = datetime.now()
    
    # Clean up expired OTPs
    for email in list(otp_store.keys()):
        if now > otp_store[email]['expiry']:
            del otp_store[email]
    
    # Clean up expired user registration data (after 30 minutes)
    for email in list(user_reg_data.keys()):
        if (now - user_reg_data[email]['timestamp']).total_seconds() > 1800:  # 30 minutes
            del user_reg_data[email]

def create_url_safe_token(data: dict):
    """Legacy function, kept for compatibility"""
    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token: str):
    """Legacy function, kept for compatibility"""
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))
        return None
