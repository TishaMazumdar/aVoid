from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/")
async def omnidim_webhook(request: Request):
    try:
        payload = await request.json()
        print("🚀 Webhook received:")
        print(payload)

        # OPTIONAL: Save to file / Firebase / DB / do matching etc
        return JSONResponse(content={"message": "Received!"})

    except Exception as e:
        print(f"❌ Error parsing webhook: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})