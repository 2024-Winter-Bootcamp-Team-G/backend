# backend

## 요구 사항
- Python 3.12
- Docker 및 Docker Compose
- 가상환경 설정 (로컬 환경에서 실행 시 필요)

## 디렉터리 구조

```   
backend/               # FastAPI 백엔드
├── Dockerfile
├── README.md
├── app/
│   ├── __init__.py
│   ├── config.py             # 설정 파일
│   ├── db.py                 # DB 연결
│   ├── init_db.py            # 초기 데이터베이스 설정
│   ├── main.py               # FastAPI 엔트리포인트
│   ├── models/               # DB 모델
│   ├── routes/               # API 라우팅
│   ├── schemas/              # Pydantic 스키마
│   ├── services/             # 비즈니스 로직
│   ├── tests/                # 테스트 코드
│   └── utils/                # 헬퍼 유틸리티
├── docker-compose.yaml       # Docker Compose 설정
├── requirements.txt          # Python 패키지 의존성
└── .env                      # 환경 변수
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
1. Docker Compose 실행
   ```bash
    docker-compose up --build
    ```

2. 실행 확인: 브라우저에서 "http://localhost:8000/docs" 로 API 문서 확인.

3. 종료 방법
    ```bash
    docker-compose down -v
    ```

---

## Redis 저장 구조

**Redis 저장 구조**
1. 최신 동영상 목록:
   - 키: `youtube_channel:{채널ID}`
   - 값: `["동영상ID1", "동영상ID2", ...]`

2. 동영상 세부 정보:
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