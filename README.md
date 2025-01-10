# backend

## 요구 사항
- Python 3.12
- Docker 및 Docker Compose (선택 사항)
- 가상환경 설정 (로컬 환경에서 실행 시 필요)

## 디렉터리 구조
   ```
   backend/               # FastAPI 백엔드
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
   ├── pyproject.toml     # Poetry 설정 파일
   ├── requirements.txt   # Python 패키지 의존성
   ├── Dockerfile         # 백엔드 도커 설정 
   └── .env               # 환경 변수
   ```

## Dockerfile
- **Base Image**: python:3.12-slim → 가볍고 Python 3.12 환경 제공.
- **작업 디렉토리**: /app → 애플리케이션 코드가 복사되는 디렉터리.
- **의존성 설치**: pip install -r requirements.txt → 애플리케이션에 필요한 Python 패키지 설치.
- **FastAPI 실행**: uvicorn → FastAPI 애플리케이션 실행 (hot-reload 포함).
   
```
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## 설정 방법

### 1. 로컬 환경에서 실행
1. 가상환경 생성 및 활성화
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    venv\Scripts\activate     # Windows
    ```

2. 의존성 설치
    ```bash
    pip install -r requirements.txt
    ```

3. 서버 실행
    ```bash
    uvicorn app.main:app --reload
    ```

### 2. Docker로 실행
1. Docker 이미지 빌드
   ```bash
   docker build -t fastapi-backend .
   ```

2. Docker 컨테이너 실행
   ```bash
   docker run -d --name backend-container -p 8000:8000 fastapi-backend
   ```

3. 실행 확인: 브라우저에서 http://localhost:8000/docs로 API 문서를 확인.

4. 종료 방법
   - 실행 중인 컨테이너 중지
      ```bash
     docker stop backend-container
     ```
   - 컨테이너 삭제
     ```bash
      docker rm backend-container
      ```
---
