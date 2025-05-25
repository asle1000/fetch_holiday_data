import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
import certifi

load_dotenv()

BASE_URL = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService"
SERVICE_KEY = os.getenv("SERVICE_KEY")

def fetch_holiday_data(endpoint: str, year: int, month: int) -> dict:
    params = {
        "solYear": year,
        "solMonth": f"{month:02d}",
        "ServiceKey": SERVICE_KEY,
        "_type": "json",
        "numOfRows": 100
    }
    url = f"{BASE_URL}/{endpoint}?{urlencode(params)}"
    response = requests.get(url, verify=certifi.where())
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"JSON 파싱 실패: {url}")
        print(f"응답 내용: {response.text[:200]}")
        return {"error": "Invalid JSON", "body": response.text}
    except requests.exceptions.RequestException as e:
        print(f"요청 실패: {url}")
        print(f"에러: {e}")
        return {"error": str(e)}

def get_rest_holidays(year: int, month: int) -> dict:
    return fetch_holiday_data("getRestDeInfo", year, month)

def get_anniversaries(year: int, month: int) -> dict:
    return fetch_holiday_data("getAnniversaryInfo", year, month)

def get_24_divisions(year: int, month: int) -> dict:
    return fetch_holiday_data("get24DivisionsInfo", year, month)

def get_sundry_days(year: int, month: int) -> dict:
    return fetch_holiday_data("getSundryDayInfo", year, month)