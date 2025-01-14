import requests


def youtube_api_request(endpoint: str, access_token: str, params: dict) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"https://www.googleapis.com/youtube/v3/{endpoint}",
        headers=headers,
        params=params,
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Failed to fetch data from {endpoint}.",
            "details": response.json(),
        }
