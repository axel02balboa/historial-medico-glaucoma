import firebase_admin
from firebase_admin import credentials, firestore
import json
import streamlit as st

# Cargar credenciales desde Streamlit Secrets
firebase_credentials = st.secrets["FIREBASE_CREDENTIALS"]

try:
    # Decodificar el JSON de las credenciales
    cred_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(cred_dict)
    
    # Inicializar Firebase si no está inicializado
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        
    # Inicializar Firestore
    db = firestore.client()
    st.write("Firebase se ha inicializado correctamente.")
except json.JSONDecodeError:
    st.error("Error al decodificar el JSON de las credenciales. Revisa el formato del JSON.")
except ValueError as e:
    st.error(f"Error al inicializar las credenciales de Firebase: {e}")
