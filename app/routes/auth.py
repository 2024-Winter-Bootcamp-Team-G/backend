from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.config import GoogleConfig
from app.services.google_service import exchange_code_for_token, get_cached_or_request_subscriptions

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
def auth_and_get_subscriptions(request: Request):
    # 인가코드 받기
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    # 액세스 토큰 획득
    access_token = exchange_code_for_token(code)

    # 구독 목록을 가져와서 redis에 캐싱
    subscription_data = get_cached_or_request_subscriptions(access_token)

    # 프론트엔드로 리다이렉트, 주소 뒤에 data_id 반환
    data_id = subscription_data["data_id"]
    redirect_url = f"http://localhost:5173/board?data_id={data_id}"
    return RedirectResponse(redirect_url)