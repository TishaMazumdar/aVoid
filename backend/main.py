from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json

#from backend.matcher import match_user_to_rooms

app = FastAPI()

# Load room data from file
with open("data/rooms.json", "r") as f:
    ROOM_DATA = json.load(f)

@app.post("/webhook")
async def receive_webhook(request: Request):
    try:
        data = await request.json()
        print("🔔 Received webhook data:", data)

        # Just return what you received
        return JSONResponse(content={"received": data})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

'''@app.post("/webhook")
async def receive_webhook(request: Request):
    try:
        data = await request.json()

        # Parse new user profile
        new_user = {
            "name": data.get("name"),
            "dob": data.get("dob"),
            "vibe": data.get("vibe"),
            "traits": data.get("traits"),
            "preferences": data.get("room_preferences"),
        }

        # Match user to best room
        best_room, score = match_user_to_rooms(new_user, ROOM_DATA)

        result = {
            "assigned_room": best_room,
            "match_score": score,
        }

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})'''