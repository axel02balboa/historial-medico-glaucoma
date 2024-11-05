import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Carga las credenciales desde los secrets de Streamlit
firebase_credentials = st.secrets["general"]["FIREBASE_CREDENTIALS"]

# Decodifica las credenciales
cred_dict = json.loads(firebase_credentials)
cred = credentials.Certificate(cred_dict)

# Inicializa la app de Firebase si aún no se ha hecho
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Crea el cliente de Firestore
db = firestore.client()

