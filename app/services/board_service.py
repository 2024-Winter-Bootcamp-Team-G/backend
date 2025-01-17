from sqlalchemy.orm import Session
from app.models.board import Board
from app.schemas.board import BoardCreate
from app.utils.dalle_handler import generate_image_with_dalle
from app.utils.gcs_handler import upload_image_to_gcs


# 보드 생성
async def create_board(db: Session, board_data: BoardCreate, user_id: int):
    """
    POST /board: 보드 생성 로직

    전체 로직:
    1. 선택한 채널 전송 (channel-send 엔드포인트 호출)
    2. 유튜브 API 호출 → 채널 정보와 최신 동영상 목록 Redis 저장
    3. Redis에서 데이터를 꺼내 GPT를 통해 키워드와 카테고리 생성
       - 키워드 구조:
         {
           "category1": ["keyword1", "keyword2"],
           ...
         }
       - 카테고리 비율 (category_ratio): [int, int, ...]
    4. DALL·E를 호출하여 이미지 생성 → 이미지 결과 URL을 DB에 저장
    5. 보드 생성 완료 → DB에 보드 데이터를 저장

    Args:
        db (Session): SQLAlchemy 세션
        board_data (BoardCreate): 보드 생성에 필요한 데이터
        user_id (int): 요청을 보낸 사용자의 ID

    Returns:
        dict: 생성된 보드 정보 및 성공 메시지
    """
    # 1. 선택한 채널 정보 전송
    # TODO: channel-send 엔드포인트 호출 로직 구현 필요
    # - 선택된 채널 ID를 받아서 전송
    # - 성공적으로 전송되지 않을 경우 예외 처리



    # 2. 유튜브 API 호출 및 Redis 저장
    # TODO: 유튜브 API를 호출하여 채널 정보와 최신 동영상 목록을 Redis에 저장하는 로직 구현 필요



    # 3. Redis에서 데이터 가져오기 및 GPT 키워드 생성
    # TODO: Redis에서 데이터를 가져와 GPT로 키워드와 카테고리를 생성하는 로직 구현 필요



    # 임시 데이터 (위 작업 끝난 후 제거)
    # category_ratio: [40, 30, 20, 10],
    # keywords: {
    #     "Wildlife": ["Lions", "Elephants", "Giraffes"],
    #     "Landscapes": ["Mountains", "Rivers", "Forests"],
    #     "Ocean": ["Coral Reefs", "Dolphins", "Shipwrecks"],
    #     "Sky": ["Clouds", "Rainbows", "Stars"],
    # }
    board_name = (
        board_data.board_name or "Generated Board"
    )  # 보드 이름도 gpt가 생성해주어야 하긴 한데...

    # 4. DALL·E를 통한 이미지 생성
    try:
        existing_board = db.query(Board).filter(Board.user_id == user_id).first()
        category_ratio = existing_board.category_ratio
        keywords = existing_board.keywords
        image_url = generate_image_with_dalle(category_ratio, keywords)
    except Exception as e:
        raise ValueError(f"DALL·E 이미지 생성 오류: {str(e)}")
    try:  # TODO: GCS 저장 로직 검증 필요
        gcs_image_url = upload_image_to_gcs(
            image_url, f"boards/{user_id}/{board_name}.png"
        )
    except Exception as e:
        raise ValueError(f"GCS 업로드 오류: {str(e)}")

    # 5. DB 저장
    new_board = Board(
        user_id=user_id,
        board_name=board_data.board_name,
        image_url=gcs_image_url,
        category_ratio=category_ratio,
        keywords=keywords,
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return {
        "message": "보드가 성공적으로 생성되었습니다.",
        "board": {
            "id": new_board.id,
            "board_name": new_board.board_name,
            "category_ratio": new_board.category_ratio,
            "keywords": new_board.keywords,
        },
    }


# 모든 보드 조회
def get_boards(db: Session, user_id: int):
    return db.query(Board).filter(Board.user_id == user_id).all()


# 보드 상세 조회
def get_board_by_id(db: Session, board_id: int):
    return db.query(Board).filter(Board.id == board_id).first()
