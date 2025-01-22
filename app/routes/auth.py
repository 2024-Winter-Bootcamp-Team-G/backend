from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import requests
from app.config import GoogleConfig

router = APIRouter(prefix="/googleauth", tags=["Authentication"])


@router.get("/login")
def login():
    scope = "https://www.googleapis.com/auth/youtube.readonly"
    response_type = "code"
    auth_url = (
        f"{GoogleConfig.GOOGLE_AUTH_URL}"
        f"?client_id={GoogleConfig.CLIENT_ID}"
        f"&redirect_uri={GoogleConfig.REDIRECT_URI}"
        f"&scope={scope}"
        f"&response_type={response_type}"
        f"&access_type=offline"
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    token_url = GoogleConfig.GOOGLE_TOKEN_URL
    payload = {
        "client_id": GoogleConfig.CLIENT_ID,
        "client_secret": GoogleConfig.CLIENT_SECRET,
        "code": code,
        "redirect_uri": GoogleConfig.REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="토큰을 가져오는 데 실패했습니다.")

    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=500, detail="Access token not found")

    # 2. HttpOnly 쿠키 설정
    frontend_url = "http://localhost:5173/board"
    response = RedirectResponse(url=frontend_url)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return response