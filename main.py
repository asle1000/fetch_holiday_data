from datetime import datetime
from api.public_holiday_api_client import (
    get_rest_holidays,
    get_anniversaries,
    get_24_divisions,
    get_sundry_days,
)
from firebase.write import save_holiday_json_to_repo, git_commit_and_push
import os

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
        data_map = {
            "rest_holidays": get_rest_holidays(year, month),
            "anniversaries": get_anniversaries(year, month),
            "divisions_24": get_24_divisions(year, month),
            "sundry_days": get_sundry_days(year, month),
        }
        if year not in yearly_data:
            yearly_data[year] = {}
        yearly_data[year][f"{month:02d}"] = data_map
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
