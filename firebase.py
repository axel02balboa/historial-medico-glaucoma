import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Cargar las credenciales desde los secrets de Streamlit
firebase_credentials = st.secrets["general"]["FIREBASE_CREDENTIALS"]

# Imprimir una parte de las credenciales para verificar su carga
try:
    cred_dict = json.loads(firebase_credentials)
    st.write("Las credenciales se cargaron correctamente.")
except json.JSONDecodeError as e:
    st.error("Error al decodificar el JSON de las credenciales.")
    st.stop()

# Inicializar la app de Firebase si aún no se ha hecho
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

# Crea el cliente de Firestore
db = firestore.client()

