from datetime import datetime, timedelta

from api.public_holiday_api_client import (
    get_rest_holidays,
    get_anniversaries,
    get_24_divisions,
    get_sundry_days,
)
from firebase.setup import initialize_firestore
from firebase.write import upload_holiday_data_to_collections
from google.cloud.firestore import Client
import requests

def document_exists(db: Client, year: int, month: int) -> bool:
    doc_ref = db.collection("holidays").document(str(year))
    doc = doc_ref.get()
    
    if not doc.exists:
        return False
    
    data = doc.to_dict()
    month_key = f"{month:02d}"
    
    if month_key not in data:
        return False
    
    month_data = data[month_key]
    required_fields = ["rest_holidays", "anniversaries", "divisions_24", "sundry_days"]
    
    return all(field in month_data for field in required_fields)


def should_force_update(current: datetime, target: datetime) -> bool:
    return target >= current.replace(day=1)

if __name__ == "__main__":
    print("휴일 데이터 수집 시작...")
    
    db = initialize_firestore()
    print("파이어스토어 연결 완료")

    now = datetime.now()
    current_year = now.year
    
    start_year = current_year - 5
    end_year = current_year + 5
    
    print(f"데이터 수집 범위: {start_year}년 ~ {end_year}년")

    year_months = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            year_months.append((year, month))

    total_months = len(year_months)
    processed = 0
    
    print(f"총 {total_months}개월 데이터 처리 시작...")

    for year, month in year_months:
        processed += 1
        print(f"[{processed}/{total_months}] {year}년 {month:02d}월 처리 중...")
        
        is_future_or_present = should_force_update(now, datetime(year, month, 1))

        skip = False
        if not is_future_or_present:
            if document_exists(db, year, month):
                print(f"  - 이미 존재함, 건너뜀")
                skip = True

        if skip:
            continue

        data_map = {
            "rest_holidays": get_rest_holidays(year, month),
            "anniversaries": get_anniversaries(year, month),
            "divisions_24": get_24_divisions(year, month),
            "sundry_days": get_sundry_days(year, month),
        }

        upload_holiday_data_to_collections(db, year, month, data_map)
        print(f"  - 저장 완료")

    print("모든 데이터 수집 완료!")
