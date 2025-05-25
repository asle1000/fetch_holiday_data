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
def document_exists(db: Client, collection_name: str, doc_id: str) -> bool:
    doc = db.collection(collection_name).document(doc_id).get()
    return doc.exists


def should_force_update(current: datetime, target: datetime) -> bool:
    return target >= current.replace(day=1)

if __name__ == "__main__":

    db = initialize_firestore()

    now = datetime.now().replace(day=1)
    start = now - timedelta(days=365 * 2)
    end = now + timedelta(days=365)

    year_months = []
    cursor = start
    while cursor <= end:
        year_months.append((cursor.year, cursor.month))
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)

    for year, month in year_months:
        doc_id = f"{year}-{month:02d}"
        is_future_or_present = should_force_update(now, datetime(year, month, 1))

        skip = False
        if not is_future_or_present:
            collections = ["rest_holidays", "anniversaries", "divisions_24", "sundry_days"]
            if all(document_exists(db, col, doc_id) for col in collections):
                print(f" Firestore에 이미 존재: {doc_id}, 업데이트 생략")
                skip = True

        if skip:
            continue

        print(f"업데이트 시작: {doc_id}")

        data_map = {
            "rest_holidays": get_rest_holidays(year, month),
            "anniversaries": get_anniversaries(year, month),
            "divisions_24": get_24_divisions(year, month),
            "sundry_days": get_sundry_days(year, month),
        }

        upload_holiday_data_to_collections(db, year, month, data_map)
