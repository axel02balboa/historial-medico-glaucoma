import json
import firebase_admin
from firebase_admin import credentials, firestore

# Carga las credenciales de Streamlit secrets
firebase_credentials = st.secrets["general"]["FIREBASE_CREDENTIALS"]

# Decodifica las credenciales
cred_dict = json.loads(firebase_credentials)
cred = credentials.Certificate(cred_dict)

# Inicializa la app de Firebase
firebase_admin.initialize_app(cred)
db = firestore.client()
