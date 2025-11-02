from fastapi import FastAPI
import httpx

app = FastAPI()

# Заглушка для корня
@app.get("/")
async def root():
    return {"message": "Service is running. Use /docs for API documentation."}

# Callback от Poster
@app.get("/menu-on-tv")
async def poster_callback(code: str, account: str = None):
    url = "https://joinposter.com/api/auth/access_token"
    data = {
        "application_id": "4394",
        "application_secret": "eb7286874ae3e6c82d2d688711cb4950",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://menu-on-tv.onrender.com/menu-on-tv"  # должно совпадать с настройками Poster
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=data)
        token_data = r.json()

    return {
        "message": "Авторизация успешна",
        "account": account,
        "token": token_data
    }

# Заготовки для меню
@app.get("/menu/bar.json")
async def bar_menu():
    return {"items": [], "note": "Здесь будет меню бара"}

@app.get("/menu/food.json")
async def food_menu():
    return {"items": [], "note": "Здесь будет меню кухни"}
