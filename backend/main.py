from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import json
import os
from dotenv import load_dotenv
import hashlib
import re
from datetime import datetime

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="static")
USERS_FILE = "backend/data/users.json"


# ---------- Auth Logic ----------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def signup_user(email: str, password: str) -> bool:
    users = load_users()
    if email in users:
        return False
    hashed = hash_password(password)
    users[email] = {"password": hashed}
    save_users(users)
    return True

def login_user(email: str, password: str) -> bool:
    users = load_users()
    user = users.get(email)
    if not user:
        return False
    return user["password"] == hash_password(password)

# ---------- Current Users ----------

CURRENT_USERS_FILE = "backend/data/current_users.json"

def load_current_users():
    if not os.path.exists(CURRENT_USERS_FILE):
        return []
    with open(CURRENT_USERS_FILE, "r") as f:
        return json.load(f)

def save_current_users(users):
    with open(CURRENT_USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# ---------- Routes ----------

@app.get("/")
def home(request: Request):
    email = request.session.get("email")
    users = load_users()

    if not email or email not in users:
        return RedirectResponse("/login", status_code=302)

    user = users[email]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "name": user["name"],
        "dob": user["dob"],
        "email": email
    })

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/signup")
def signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    dob: str = Form(...)
):
    users = load_users()

    # Basic regex: must end in @<something>.com
    if not re.match(r"[^@]+@[^@]+\.[cC][oO][mM]$", email):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "signup_error": "Enter a valid email ending with .com"
        })

    if email in users:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "signup_error": "Email already registered"
        })

    users[email] = {
        "name": name,
        "password": hash_password(password),
        "dob": dob,
        "vibe": "",
        "traits": {},
        "room_preferences": {},
        "assigned_room": None
    }

    save_users(users)
    request.session["email"] = email

    # Add to current_users.json
    current_users = load_current_users()
    if email not in current_users:
        current_users.append(email)
        save_current_users(current_users)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "email": email,
        "signup_success": "Signup successful!"
    })

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    users = load_users()
    user = users.get(email)

    if not user or user["password"] != hash_password(password):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "login_error": "Invalid email or password"
        })

    request.session["email"] = email

    current_users = load_current_users()
    if email not in current_users:
        current_users.append(email)
        save_current_users(current_users)

    return RedirectResponse("/", status_code=302)

@app.get("/logout")
def logout(request: Request):
    email = request.session.get("email")
    current_users = load_current_users()
    if email in current_users:
        current_users.remove(email)
        save_current_users(current_users)
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

@app.get("/receive_traits")
def get_traits(request: Request):
    current_users = load_current_users()
    if not current_users:
        return JSONResponse({"status": "no user currently logged in"}, status_code=400)

    email = current_users[0]
    users = load_users()
    if email not in users:
        return JSONResponse({"status": "user not found"}, status_code=404)

    traits = users[email].get("traits", {})
    return JSONResponse({"traits": traits})

def load_questions():
    with open("backend/data/questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def map_trait_value(trait, answer, questions):
    answer = answer.lower()
    for q in questions:
        if q["trait"] == trait:
            for group, keywords in q["keywords"].items():
                for keyword in keywords:
                    if keyword in answer:
                        return group
    return answer  # fallback to raw answer if no match

def get_active_email():
    current_users = load_current_users()
    return current_users[0] if current_users else None

@app.post("/receive_traits")
async def receive_traits(request: Request):
    data = await request.json()
    print("Webhook received:", data)

    extracted = data.get("call_report", {}).get("extracted_variables", {})
    if isinstance(extracted, list):
        extracted = {item["key"]: item["value"] for item in extracted if "key" in item and "value" in item}

    # ✅ Get email from current_users.json instead of session
    email = get_active_email()
    if not email:
        return JSONResponse({"status": "no user currently logged in"}, status_code=400)

    users = load_users()
    if email not in users:
        return JSONResponse({"status": "user not found"}, status_code=404)

    # ✅ Save the traits
    questions = load_questions()
    users[email].setdefault("traits", {})
    for trait, answer in extracted.items():
        users[email]["traits"][trait] = map_trait_value(trait, str(answer), questions)

    save_users(users)

    return JSONResponse({"status": "traits saved successfully"})