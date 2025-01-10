# backend

## 요구 사항
- Python 3.12
- 가상환경 설정 필요

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
