import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Cargar las credenciales desde la variable de entorno
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
if firebase_credentials:
    cred_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()