import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Firebase app
cred = credentials.Certificate(os.getenv("FIREBASE_SERVICE_ACCOUNT_CREDENTIALS"))
firebase_admin.initialize_app(cred)
db = firestore.client()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(email: str):
    doc = db.collection("users").document(email).get()
    return doc.to_dict() if doc.exists else None

def save_user(email: str, data: dict):
    db.collection("users").document(email).set(data)

def create_user(email: str, name: str, password: str, dob: str):
    user = get_user(email)
    if user:
        return False
    data = {
        "name": name,
        "password": hash_password(password),
        "dob": dob,
        "vibe": "",
        "traits": {},
        "room_preferences": {},
        "assigned_room": None
    }
    save_user(email, data)
    return True

def check_login(email: str, password: str) -> bool:
    user = get_user(email)
    return user and user["password"] == hash_password(password)

def update_traits(email: str, traits: dict):
    user = get_user(email)
    if not user:
        return False
    user["traits"] = traits
    save_user(email, user)
    return True

def upload_rooms_to_firestore():
    with open("rooms.json", "r") as f:  # Or paste the data inline
        rooms = json.load(f)
    
    for room in rooms:
        doc_ref = db.collection("rooms").document(room["room_id"])
        doc_ref.set(room)