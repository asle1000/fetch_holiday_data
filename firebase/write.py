from google.cloud.firestore import Client

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
