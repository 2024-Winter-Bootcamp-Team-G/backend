# backend

## 요구 사항
- Python 3.12
- 가상환경 설정 필요

## 디렉터리 구조
   ```
   backend/              # FastAPI 백엔드
   ├── app/
   │   ├── __init__.py
   │   ├── main.py        # FastAPI 진입점
   │   ├── config.py      # 설정 파일
   │   ├── db.py          # 데이터베이스 연결
   │   ├── routes/        # API 라우트
   │   │   ├── __init__.py
   │   │   └── user.py
   │   ├── schemas/       # 데이터 검증 및 직렬화
   │   │   ├── __init__.py
   │   │   └── user.py
   │   ├── services/      # 비즈니스 로직
   │   │   ├── __init__.py
   │   │   └── user_service.py
   │   ├── tests/         # 백엔드 테스트
   │   └── utils/         # 공통 유틸리티
   ├── requirements.txt   # Python 패키지 의존성
   ├── Dockerfile         # 백엔드 도커 설정 
   └── .env               # 환경 변수
   ```

## 설정 방법
1. 리포지토리 클론:
    ```bash
    git clone <리포지토리 URL>
    cd backend
    ```

2. Python 3.12 확인 및 설치:
    ```bash
    python3 --version
    ```

3. 가상환경 생성 및 활성화:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    venv\Scripts\activate     # Windows
    ```

4. 의존성 설치:
    ```bash
    pip install -r requirements.txt
    ```

5. 환경 변수 설정:
    ```bash
    cp .env.example .env
    ```

6. 서버 실행:
    ```bash
    uvicorn app.main:app --reload
    ```

---
