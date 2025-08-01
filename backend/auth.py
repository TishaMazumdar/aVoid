import json
import bcrypt
import uuid
from typing import Optional

USERS_FILE = "backend/data/users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def signup_user(username: str, password: str) -> Optional[str]:
    users = load_users()
    if any(u["username"] == username for u in users):
        return None  # User exists
    password_hash = hash_password(password)
    token = str(uuid.uuid4())
    users.append({"username": username, "password_hash": password_hash, "session_token": token})
    save_users(users)
    return token

def login_user(username: str, password: str) -> Optional[str]:
    users = load_users()
    for u in users:
        if u["username"] == username and verify_password(password, u["password_hash"]):
            return u["session_token"]
    return None