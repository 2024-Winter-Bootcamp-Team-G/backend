from sqlalchemy.orm import Session
from app.models.board import Board
from app.schemas.board import BoardCreate


# 새로운 보드 생성
def create_board(db: Session, board: BoardCreate):
    new_board = Board(
        # user_id=board.user_id,
        board_name=board.board_name,
        image_url=board.image_url,
        category_ratio=board.category_ratio,
        keyword=board.keyword,
    )
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return new_board


# 모든 보드 조회
def get_boards(db: Session):
    return db.query(Board).all()


# 보드 상세 조회
def get_board_by_id(db: Session, board_id: int):
    return db.query(Board).filter(Board.id == board_id).first()
