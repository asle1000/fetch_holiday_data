import os
import json
from google.cloud.firestore import Client
import subprocess

def upload_holiday_data_to_collections(db: Client, year: int, month: int, data_map: dict):
    doc_id = str(year)
    
    doc_ref = db.collection("holidays").document(doc_id)
    
    doc = doc_ref.get()
    if doc.exists:
        current_data = doc.to_dict()
    else:
        current_data = {}
    
    month_key = f"{month:02d}"
    current_data[month_key] = {
        "rest_holidays": data_map["rest_holidays"],
        "anniversaries": data_map["anniversaries"], 
        "divisions_24": data_map["divisions_24"],
        "sundry_days": data_map["sundry_days"]
    }
    
    doc_ref.set(current_data)

# holiday-json-repo/holidays/{year}.json 저장 함수

def save_holiday_json_to_repo(year: int, data: dict, repo_path: str):
    holidays_dir = os.path.join(repo_path, 'holidays')
    os.makedirs(holidays_dir, exist_ok=True)  # 디렉토리 없으면 생성
    file_path = os.path.join(holidays_dir, f"{year}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{file_path} 저장 완료")

def git_commit_and_push(repo_path, file_path, message):
    cmds = [
        ['git', 'pull', '--rebase', 'origin', 'main'],
        ['git', 'add', file_path],
        ['git', 'commit', '-m', message],
        ['git', 'push', 'origin', 'main']
    ]
    for cmd in cmds:
        subprocess.run(cmd, cwd=repo_path, check=True)
