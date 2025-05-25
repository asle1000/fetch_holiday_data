from google.cloud.firestore import Client

def upload_holiday_data_to_collections(db: Client, year: int, month: int, data_map: dict):
    doc_id = f"{year}-{month:02d}"

    for collection_name, data in data_map.items():
        doc_ref = db.collection(collection_name).document(doc_id)
        doc_ref.set(data)
        print(f"Firestore 저장 완료: {collection_name}/{doc_id}")
