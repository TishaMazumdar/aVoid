from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import json
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="static")
USERS_FILE = "backend/data/users.json"


# ---------- Auth Logic ----------

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def signup_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False
    users[username] = {"password": password}
    save_users(users)
    return True

def login_user(username: str, password: str) -> bool:
    users = load_users()
    user = users.get(username)
    return user is not None and user["password"] == password

# ---------- Routes ----------

@app.get("/")
def home(request: Request):
    username = request.session.get("username")
    users = load_users()

    if not username or username not in users:
        return RedirectResponse("/login")

    user = users[username]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "name": user["name"],
        "dob": user["dob"]
    })

@app.get("/signup")
def signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    dob: str = Form(...)
):
    users = load_users()
    if email in users:
        return templates.TemplateResponse("index.html", {"request": request, "signup_error": "Email already registered"})

    users[email] = {
        "name": name,
        "password": password,
        "dob": dob
    }
    save_users(users)
    request.session["username"] = email
    return templates.TemplateResponse("index.html", {
        "request": request,
        "username": email,
        "signup_success": "Signup successful!"
    })

@app.get("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    users = load_users()
    user = users.get(email)
    if not user or user["password"] != password:
        return templates.TemplateResponse("index.html", {"request": request, "login_error": "Invalid email or password"})

    request.session["username"] = email
    return RedirectResponse("/", status_code=302)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)