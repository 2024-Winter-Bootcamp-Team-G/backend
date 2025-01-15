from bcrypt import hashpw, gensalt, checkpw
from app.utils.time import time_zone
from app.utils.redis_handler import RedisHandler


def format_date(date_str):
    """날짜 포맷 변환 함수"""
    pass


# 비밀번호 해싱
def hash_password(password: str) -> str:
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
