from datetime import datetime
from api.public_holiday_api_client import (
    get_rest_holidays,
    get_anniversaries,
    get_24_divisions,
    get_sundry_days,
)
from firebase.write import save_holiday_json_to_repo, git_commit_and_push
import os
import copy

TYPE_MAP = {
    "rest_holidays": "REST_HOLIDAYS",
    "anniversaries": "ANNIVERSARIES",
    "divisions_24": "DIVISIONS_24",
    "sundry_days": "SUNDRY_DAYS"
}

# 포틴데이 (매월 14일 커플 기념일)
FOURTEEN_DAYS = {
    1: "다이어리 데이",
    2: "밸런타인데이",
    3: "화이트데이",
    4: "블랙데이",
    5: "로즈데이",
    6: "키스데이",
    7: "실버데이",
    8: "그린데이",
    9: "포토데이 / 뮤직데이",
    10: "와인데이",
    11: "무비데이",
    12: "허그데이"
}

def should_force_update(current: datetime, target: datetime) -> bool:
    return target >= current.replace(day=1)

def empty_to_none(value):
    return None if value == "" else value

def extract_items(data, type_key):
    try:
        items = data.get("response", {}).get("body", {}).get("items", "")
        if items == "" or items is None:
            return []
        # items가 dict이고 'item' 키가 있으면 그걸로
        if isinstance(items, dict) and "item" in items:
            items = items["item"]
        elif isinstance(items, dict):
            return []
        # item이 단일 dict일 수도 있음
        if isinstance(items, dict):
            items = [items]
        result = []
        for item in items:
            date_name = item.get("dateName")
            is_holiday_raw = item.get("isHoliday")
            is_holiday = True if is_holiday_raw == "Y" else False
            locdate = item.get("locdate")
            if date_name and ("임시공휴일" in date_name or "대체공휴일" in date_name):
                type_val = "SUBSTITUTE_HOLIDAY"
            else:
                type_val = TYPE_MAP[type_key]
            result.append({
                "dateName": date_name,
                "isHoliday": is_holiday,
                "locdate": locdate,
                "type": type_val
            })
        return result
    except Exception as e:
        print(f"extract_items error: {e}")
        return []

def remove_empty_items(data):
    data = copy.deepcopy(data)
    try:
        items = data["response"]["body"]["items"]
        if items == "" or items is None:
            del data["response"]["body"]["items"]
    except Exception:
        pass
    return data

def add_fourteen_day(year: int, month: int) -> dict:
    """매월 14일 포틴데이를 SPECIAL 타입으로 추가"""
    if month not in FOURTEEN_DAYS:
        return None
    date_name = FOURTEEN_DAYS[month]
    locdate = int(f"{year}{month:02d}14")
    return {
        "dateName": date_name,
        "isHoliday": False,
        "locdate": locdate,
        "type": "SPECIAL"
    }

if __name__ == "__main__":
    print("휴일 데이터 수집 시작...")

    now = datetime.now()
    current_year = now.year
    start_year = current_year - 1
    end_year = current_year + 1
    print(f"데이터 수집 범위: {start_year}년 ~ {end_year}년")

    year_months = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            year_months.append((year, month))

    total_months = len(year_months)
    processed = 0
    print(f"총 {total_months}개월 데이터 처리 시작...")

    yearly_data = {}
    for year, month in year_months:
        processed += 1
        print(f"[{processed}/{total_months}] {year}년 {month:02d}월 처리 중...")
        days = []
        days += extract_items(get_rest_holidays(year, month), "rest_holidays")
        days += extract_items(get_anniversaries(year, month), "anniversaries")
        days += extract_items(get_24_divisions(year, month), "divisions_24")
        days += extract_items(get_sundry_days(year, month), "sundry_days")
        # 포틴데이 추가 (매월 14일)
        fourteen_day = add_fourteen_day(year, month)
        if fourteen_day:
            days.append(fourteen_day)
        data_map = {
            "month": f"{month:02d}",
            "days": days
        }
        if year not in yearly_data:
            yearly_data[year] = []
        yearly_data[year].append(data_map)
        print(f"  - 저장 완료")

    # holiday-json-repo/holidays/{year}.json 저장
    repo_path = os.path.join(os.path.dirname(__file__), 'holiday-json-repo')
    for year, data in yearly_data.items():
        save_holiday_json_to_repo(year, data, repo_path)
        file_path = f"holidays/{year}.json"
        message = f"Add/update {year}년 holiday 데이터"
        git_commit_and_push(repo_path, file_path, message)
        print(f"  - {year}년 holiday-json-repo 저장 및 커밋/푸시 완료")

    print("모든 데이터 수집 완료!")
