from datetime import datetime, timedelta

from api.public_holiday_api_client import (
    get_rest_holidays,
    get_anniversaries,
    get_24_divisions,
    get_sundry_days,
)
# from firebase.setup import initialize_firestore
# from firebase.write import upload_holiday_data_to_collections
# from google.cloud.firestore import Client
from firebase.write import save_holiday_json_to_repo, git_commit_and_push
import os

# Firestore 관련 함수 제거
# def document_exists(db: Client, year: int, month: int) -> bool:
#     ...
# def should_force_update(current: datetime, target: datetime) -> bool:
#     ...
def should_force_update(current: datetime, target: datetime) -> bool:
    return target >= current.replace(day=1)

if __name__ == "__main__":
    print("휴일 데이터 수집 시작...")

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

    yearly_data = {}
    for year, month in year_months:
        processed += 1
        print(f"[{processed}/{total_months}] {year}년 {month:02d}월 처리 중...")

        is_future_or_present = should_force_update(now, datetime(year, month, 1))
        data_map = {
            "rest_holidays": get_rest_holidays(year, month),
            "anniversaries": get_anniversaries(year, month),
            "divisions_24": get_24_divisions(year, month),
            "sundry_days": get_sundry_days(year, month),
        }
        if year not in yearly_data:
            yearly_data[year] = {"months": {}}
        yearly_data[year]["months"][f"{month:02d}"] = data_map
        print(f"  - 데이터 수집 완료")

    # holiday-json-repo 경로
    repo_path = os.path.join(os.path.dirname(__file__), 'holiday-json-repo')
    for year, data in yearly_data.items():
        save_holiday_json_to_repo(year, data, repo_path)
        file_path = f"holidays/{year}.json"
        message = f"Add/update {year}년 holiday 데이터"
        git_commit_and_push(repo_path, file_path, message)
        print(f"  - {year}년 데이터 저장 및 커밋/푸시 완료")

    print("모든 데이터 수집 및 저장 완료!")
