"""
로그를 보려면 다음과 같이 실행
# pytest -s test_dalle.py
"""

import logging
import pytest
import time
from app.utils.dalle_handler import generate_image_with_dalle

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


@pytest.fixture
def dummy_data():
    return {
        "category_ratio": [40, 30, 20, 10],
        "keywords": {
            "Wildlife": ["Lions", "Elephants", "Giraffes"],
            "Landscapes": ["Mountains", "Rivers", "Forests"],
            "Ocean": ["Coral Reefs", "Dolphins", "Shipwrecks"],
            "Sky": ["Clouds", "Rainbows", "Stars"],
        },
    }


def test_generate_image_with_dalle_real(dummy_data):
    """
    실제 DALL·E API 호출 테스트
    """
    category_ratio = dummy_data["category_ratio"]
    keywords = dummy_data["keywords"]

    # 실제 OpenAI API 호출
    image_url = generate_image_with_dalle(category_ratio, keywords)

    # URL 출력
    assert image_url.startswith("http")
    logging.info(f"Generated image URL: {image_url}")
