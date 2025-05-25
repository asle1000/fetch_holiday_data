import firebase_admin
from firebase_admin import credentials, firestore

FIREBASE_CREDENTIAL_PATH = "credentials/firebase-adminsdk.json"

def initialize_firestore() -> firestore.Client:
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CREDENTIAL_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()