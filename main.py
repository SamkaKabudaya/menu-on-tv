from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.get("/menu-on-tv")
async def poster_callback(code: str, account: str = None):
    url = "https://joinposter.com/api/auth/access_token"
    data = {
        "application_id": "4394",
        "application_secret": "eb7286874ae3e6c82d2d688711cb4950",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://mysite.onrender.com/menu-on-tv"  # см. ниже
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=data)
        token_data = r.json()
    return {"message": "Авторизация успешна", "token": token_data}