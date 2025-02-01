# 🛠️ backend

이 프로젝트는 YouTube 데이터와 OpenAI API를 활용하여 카테고리와 키워드를 생성하고, 이를 바탕으로 사용자 맞춤형 콘텐츠를 생성하는 FastAPI 기반 애플리케이션입니다.

## 📁 Project Directory Structure

```   
backend/                     # FastAPI 백엔드
├── Dockerfile               # Docker 이미지를 빌드하기 위한 파일
├── README.md                # 프로젝트 설명 및 가이드 문서
├── app                      # FastAPI 애플리케이션 소스 코드
│   ├── config.py            # 애플리케이션 환경설정
│   ├── db.py                # 데이터베이스 연결 설정
│   ├── main.py              # FastAPI 애플리케이션의 엔트리 포인트
│   ├── models               # SQLAlchemy 모델 정의
│   ├── routes               # API 라우팅 정의
│   ├── schemas              # Pydantic 데이터 스키마 정의
│   ├── services             # 주요 비즈니스 로직
│   ├── tests                # 테스트 코드
│   └── utils                # 공통 유틸리티 함수
├── docker-compose.yaml      # Docker Compose 설정 파일
├── gcp-key.json             # Google Cloud Platform 서비스 계정 키
├── requirements.txt         # Python 패키지 종속성
└── venv                     # Python 가상환경 디렉터리
```

## ✨ 주요 기능

1. **📺 YouTube 데이터 기반 키워드 생성**
   - Redis를 이용하여 캐싱된 YouTube 데이터를 OpenAI API를 통해 카테고리와 키워드로 변환합니다.

2. **🎨 DALL·E 이미지 생성**
   - 생성된 카테고리와 키워드를 기반으로 이미지를 생성합니다.

3. **⚙️ Redis와 Celery를 활용한 비동기 작업 처리**
   - Redis와 Celery를 활용하여 키워드와 이미지를 비동기로 생성합니다.

4. **🔐 사용자 관리 및 인증**
   - JWT(JSON Web Token)를 통해 인증 및 사용자 세션을 관리합니다.

5. **☁️ Google Cloud Storage 업로드**
   - 생성된 이미지를 GCP Storage에 업로드하고 URL을 저장합니다.

## 필수 파일
1. .env
   ```
   APP_NAME='My FastAPI App'

   # PostgreSQL
   DATABASE_URL=
   POSTGRES_DB=
   POSTGRES_USER=
   POSTGRES_PASSWORD=
   
   # Redis
   REDIS_HOST=
   REDIS_PORT=
   
   # RabbitMQ
   RABBITMQ_DEFAULT_USER=
   RABBITMQ_DEFAULT_PASS=
   RABBITMQ_HOST=
   RABBITMQ_PORT=
   
   # Celery
   CELERY_BROKER_URL=
   CELERY_RESULT_BACKEND=
   CELERY_BROKER_CONNECTION_MAX_RETRIES=5
   
   # OpenAI
   OPENAI_API_KEY=
   
   # GCP
   GCP_BUCKET_NAME=
   GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
   
   # JWT
   SECRET_KEY=
   ALGORITHM=
   ACCESS_TOKEN_EXPIRE_MINUTES=120
   REFRESH_TOKEN_EXPIRE_MINUTES=120
   
   # YouTube Data API
   CLIENT_ID=
   CLIENT_SECRET=
   REDIRECT_URI=
   API_KEY=
   ```
   
2. gcp-key.json
GCP 서비스를 사용하기 위한 서비스 계정 키 파일입니다. Google Cloud Console에서 발급받은 JSON 파일을 프로젝트 루트 디렉터리에 gcp-key.json 이름으로 저장해야 합니다.

## 🚀 설정 방법

### 1️⃣ 로컬 환경에서 실행

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

### 2️⃣ Docker로 실행

1. Docker Compose 실행
```bash
docker-compose up --build
```

2. 실행 확인
   - 브라우저에서 “http://localhost:8000/docs” 로 API 문서 확인.

3. 종료 방법
```bash
docker-compose down -v
```

## 📦 Redis 저장 구조

### 1️⃣ 최신 동영상 목록:
   - 키: `youtube_channel:{채널ID}`
   - 값: `["동영상ID1", "동영상ID2", ...]`

### 2️⃣ 동영상 세부 정보
   - 키: `youtube_video:{동영상ID}`
   - 값:
     ```json
     {
       "tags": ["태그1", "태그2"],
       "categoryId": "카테고리ID",
       "localizedTitle": "제목",
       "localizedDescription": "설명"
     }
     ```
### 3️⃣ 특정 보드 관련 동영상
   - 키: `board_videos:{board_id}` 
   - 값: `["동영상ID1", "동영상ID2", ...]`

## 🧪 테스트 실행
1.	테스트 실행
```bash
pytest
```

2.	코드 커버리지 확인
```bash
pytest --cov=app
```



