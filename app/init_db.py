from app.db import engine, Base


# 데이터베이스 테이블 생성
def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()