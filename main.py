from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
import time
import os

app = FastAPI()

USED_CODES = {}
CODE_TTL_SEC = 300  # 5 минут

def is_code_used(code: str) -> bool:
    now = time.time()
    for c, ts in list(USED_CODES.items()):
        if now - ts > CODE_TTL_SEC:
            USED_CODES.pop(c, None)
    return code in USED_CODES

def mark_code_used(code: str):
    USED_CODES[code] = time.time()

@app.get("/")
async def root():
    return {"message": "Service is running. Use /docs for API documentation."}

@app.get("/menu-on-tv")
async def poster_callback(
    code: str = Query(..., description="Authorization code от Poster"),
    account: str = Query(None, description="Аккаунт Poster")
):
    if is_code_used(code):
        return RedirectResponse(url="/fail?reason=used")

    url = "https://joinposter.com/api/auth/access_token"
    data = {
        "application_id": "4394",
        "application_secret": "eb7286874ae3e6c82d2d688711cb4950",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://menu-on-tv.onrender.com/menu-on-tv",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, data=data)
        token_data = r.json()

    mark_code_used(code)

    if isinstance(token_data, dict) and token_data.get("access_token"):
        # Логируем токен (виден в Render → Logs)
        print("Получен токен:", token_data)

        # Можно сохранить токен в переменные окружения
        os.environ["POSTER_TOKEN"] = token_data["access_token"]

        return RedirectResponse(url="/success")
    else:
        print("Ошибка авторизации Poster:", token_data)
        return RedirectResponse(url="/fail?reason=poster_error")

@app.get("/success", response_class=HTMLResponse)
async def success_page():
    return """
    <html>
      <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2>✅ Авторизация успешна</h2>
        <p>Токен сохранён на сервере. Можно закрыть это окно.</p>
      </body>
    </html>
    """

@app.get("/fail", response_class=HTMLResponse)
async def fail_page(reason: str = "unknown"):
    return f"""
    <html>
      <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2>❌ Авторизация не удалась</h2>
        <p>Причина: {reason}</p>
        <p>Попробуйте пройти авторизацию ещё раз.</p>
      </body>
    </html>
    """

@app.get("/menu/bar.json")
async def bar_menu():
    return {"items": [], "note": "Здесь будет меню бара"}

@app.get("/menu/food.json")
async def food_menu():
    return {"items": [], "note": "Здесь будет меню кухни"}
