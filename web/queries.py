import json
from pyscript import fetch

# base_url: str = "http://[::1]:8000"
base_url: str = "http://127.0.0.1:8000"


# ----------------------------------------------------------------
async def query_ex(url: str) -> dict:
    try:
        response: dict = await fetch(url).json()
        return response
    except Exception as e:
        result: dict = {"error": str(e)}
        return result


# ----------------------------------------------------------------
async def send_data_ex(data: dict):
    try:
        response = await fetch(
            url=data["callbackUrl"],
            method="POST",
            headers={"Content-type": "application/json"},
            body=json.dumps(data),
        )
    except Exception as e:
        print(e)


# ----------------------------------------------------------------


# ----------------------------------------------------------------
