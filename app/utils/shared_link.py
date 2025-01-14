from app.utils.redis_handler import redis_client

def create_shared_link(board_id: int) -> str:
    shared_link = f"https://example.com/shared-board/{board_id}"
    redis_client.setex(f"shared_link:{board_id}", 3600, shared_link)
    return shared_link
