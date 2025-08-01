from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
import re
from fastapi import Body
from matcher import assign_best_room

from firebase.firebase_utils import (
    create_user_if_not_exists,
    get_user,
    update_traits,
    save_user
)

load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=JSONResponse)
def home(request: Request):
    email = request.session.get("email")
    if not email:
        return RedirectResponse("/login")

    user = get_user(email)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "email": email,
        "user": user
    })

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/google-login")
def google_login(request: Request, email: str = Form(...), name: str = Form(...)):
    # No need for manual email validation
    create_user_if_not_exists(email=email, name=name)
    request.session["email"] = email
    return RedirectResponse("/", status_code=302)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")

@app.post("/update_preferences")
def update_preferences(request: Request, type: str = Form(...), floor: str = Form(...), has_window: str = Form(...)):
    email = request.session.get("email")
    if not email:
        return RedirectResponse("/login")

    user = get_user(email)
    user["room_preferences"] = {
        "type": type,
        "floor": floor,
        "has_window": has_window
    }

    save_user(email, user)
    return RedirectResponse("/", status_code=302)

@app.post("/update_dob")
def update_dob(request: Request, dob: str = Form(...)):
    email = request.session.get("email")
    if not email:
        return RedirectResponse("/login")

    user = get_user(email)
    user["dob"] = dob
    save_user(email, user)
    return RedirectResponse("/", status_code=302)

@app.post("/webhook")
async def receive_webhook(data: dict = Body(...)):
    email = data.get("email")
    name = data.get("name")
    dob = data.get("dob")
    traits = data.get("traits")

    if not email or not traits:
        return JSONResponse({"error": "Missing email or traits"}, status_code=400)

    create_user_if_not_exists(email=email, name=name)
    
    user = get_user(email)
    user["dob"] = dob
    user["traits"] = traits
    save_user(email, user)

    return JSONResponse({"message": "Data received and stored."})

@app.post("/assign_room")
def assign_room(request: Request):
    email = request.session.get("email")
    if not email:
        return RedirectResponse("/login")

    user = get_user(email)
    room_id, score = assign_best_room(user)

    user["assigned_room"] = room_id
    user["match_score"] = f"{score:.2f}%"
    save_user(email, user)

    return RedirectResponse("/", status_code=302)

@app.get("/admin")
def admin_debug(request: Request):
    from firebase.firebase_utils import get_all_users
    users = get_all_users()
    return JSONResponse(users)
