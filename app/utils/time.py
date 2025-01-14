import pytz


def time_zone():
    kst = pytz.timezone("Asia/Seoul")  # 시간대 한국으로 설정
    return kst
