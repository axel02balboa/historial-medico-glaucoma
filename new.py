import streamlit as st
from PIL import Image
import io
import numpy as np
from fpdf import FPDF
from tensorflow.keras.models import load_model
from firebase import db  # Importar la configuración de Firebase

# Cargar el modelo entrenado
try:
    model = load_model('glaucoma_model.h5')
except Exception as e:
    st.error("Error al cargar el modelo. Asegúrate de que el archivo 'glaucoma_model.h5' existe y es válido.")
    st.stop()

# Función para verificar acceso de usuario y contraseña
def verificar_acceso(usuario, contraseña):
    USUARIOS_VALIDOS = {
        "personal1": "personalcontra",
        "especialista1": "especialistacontra"
    }
    return USUARIOS_VALIDOS.get(usuario) == contraseña

# Función para convertir una imagen PIL a bytes
def convertir_imagen_a_bytes(imagen):
    img_byte_arr = io.BytesIO()
    imagen.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

# Insertar o actualizar la información de un paciente en Firebase
def guardar_datos_paciente(nombre, edad, sexo, direccion, dni, telefono, sintomas_previos, foto_ojo_derecho, foto_ojo_izquierdo, reporte):
    doc_ref = db.collection("pacientes").document(nombre)
    data = {
        "nombre": nombre,
        "edad": edad,
        "sexo": sexo,
        "direccion": direccion,
        "dni": dni,
        "telefono": telefono,
        "sintomas_previos": sintomas_previos,
        "reporte": reporte
    }
    if foto_ojo_derecho:
        image_pil = Image.open(foto_ojo_derecho)
        data["foto_ojo_derecho"] = convertir_imagen_a_bytes(image_pil)
        data["prediccion_ojo_derecho"] = float(predict_glaucoma(image_pil))  # Convertir a float
    if foto_ojo_izquierdo:
        image_pil = Image.open(foto_ojo_izquierdo)
        data["foto_ojo_izquierdo"] = convertir_imagen_a_bytes(image_pil)
        data["prediccion_ojo_izquierdo"] = float(predict_glaucoma(image_pil))  # Convertir a float
    doc_ref.set(data)
    st.success(f"Datos de {nombre} guardados correctamente en Firebase.")

# Función para predecir si la imagen tiene glaucoma
def predict_glaucoma(img):
    img = img.resize((150, 150))  # Redimensionar a 150x150
    img_array = np.array(img) / 255.0  # Normalizar la imagen
    img_array = np.expand_dims(img_array, axis=0)  # Agregar dimensión para batch
    prediction = model.predict(img_array)
    return prediction[0][0]  # Retornar la probabilidad

# Cargar los datos de los pacientes desde Firebase
def cargar_datos_pacientes():
    pacientes_ref = db.collection("pacientes")
    docs = pacientes_ref.stream()
    pacientes = []
    for doc in docs:
        paciente = doc.to_dict()
        if paciente.get("foto_ojo_derecho"):
            paciente["foto_ojo_derecho"] = Image.open(io.BytesIO(paciente["foto_ojo_derecho"]))
        if paciente.get("foto_ojo_izquierdo"):
            paciente["foto_ojo_izquierdo"] = Image.open(io.BytesIO(paciente["foto_ojo_izquierdo"]))
        pacientes.append(paciente)
    return pacientes

# Eliminar un paciente de Firebase
def eliminar_paciente(nombre):
    db.collection("pacientes").document(nombre).delete()
    st.success(f"Paciente {nombre} eliminado correctamente.")

# Función para generar PDF del reporte del paciente
def generar_pdf(nombre, edad, sexo, direccion, dni, telefono, sintomas, reporte, imagen_derecho, imagen_izquierdo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Reporte Médico del Paciente", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Datos del Paciente", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Nombre: {nombre}", ln=True)
    pdf.cell(0, 10, f"Edad: {edad}", ln=True)
    pdf.cell(0, 10, f"Sexo: {sexo}", ln=True)
    pdf.cell(0, 10, f"Dirección: {direccion}", ln=True)
    pdf.cell(0, 10, f"DNI: {dni}", ln=True)
    pdf.cell(0, 10, f"Teléfono: {telefono}", ln=True)
    pdf.ln(10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "Síntomas Previos", border=1, ln=True, fill=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=sintomas, border=1)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Reporte Médico", border=1, ln=True, fill=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=reporte, border=1)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Imágenes de los Ojos", ln=True, fill=True)
    pdf.ln(5)

    if imagen_derecho:
        img_path = "ojo_derecho_temp.png"
        imagen_derecho.save(img_path)
        pdf.cell(0, 10, "Imagen Ojo Derecho:", ln=True)
        pdf.image(img_path, x=10, y=None, w=90)

    if imagen_izquierdo:
        img_path = "ojo_izquierdo_temp.png"
        imagen_izquierdo.save(img_path)
        pdf.cell(0, 10, "Imagen Ojo Izquierdo:", ln=True)
        pdf.image(img_path, x=110, y=None, w=90)

    pdf.ln(20)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Especialista: ________", ln=True, align="L")
    pdf.cell(0, 10, "Firma: ________", ln=True, align="L")

    pdf_output = f"Reporte_{nombre}.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Estilo de la página con fondo y botones mejorados
st.markdown("""
    <style>
    .main {
        background-color: #e6f7ff;
        font-family: 'Arial', sans-serif;
    }
    h1 {
        color: #4B8BBE;
        text-align: center;
    }
    h2 {
        color: #2E8B57;
    }
    h3 {
        color: #4682B4;
    }
    .stButton>button {
        background-color: #b1e3b3;
        color: white;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextInput>div>input {
        padding: 10px;
        font-size: 14px;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    .stFormSubmitButton>button {
        background-color: #b1e3b3;
        color: white;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Estado de sesión
if "acceso_concedido" not in st.session_state:
    st.session_state.acceso_concedido = False
    st.session_state.tipo_usuario = None
    st.session_state.paciente_seleccionado = None

# Formulario de inicio de sesión
if not st.session_state.acceso_concedido:
    st.markdown("<h1>Iniciar Sesión</h1>", unsafe_allow_html=True)
    with st.form("form_login"):
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        submit_login = st.form_submit_button("Ingresar")

    if submit_login:
        if verificar_acceso(usuario, contraseña):
            st.success("Acceso concedido.")
            st.session_state.acceso_concedido = True
            st.session_state.tipo_usuario = usuario
            st.experimental_set_query_params(refresh=True)
        else:
            st.error("Usuario o contraseña incorrectos.")
else:
    st.markdown(f"<h1>Historial Médico</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2>Bienvenido {st.session_state.tipo_usuario}</h2>", unsafe_allow_html=True)

    pacientes_db = cargar_datos_pacientes()
    st.markdown("<h3>Pacientes:</h3>", unsafe_allow_html=True)
    if not pacientes_db:
        st.warning("No hay pacientes cargados.")
    else:
        for i, paciente in enumerate(pacientes_db):
            nombre = paciente.get("nombre", "")
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(f"Paciente {i+1} ({nombre})", key=f"btn_paciente_{nombre}"):
                    st.session_state.paciente_seleccionado = paciente
            with col2:
                if st.button("Eliminar", key=f"eliminar_{nombre}"):
                    eliminar_paciente(nombre)
                    st.experimental_set_query_params(refresh=True)

    with st.expander("Agregar nuevo paciente"):
        st.markdown("<h3>Ingrese los datos del nuevo paciente:</h3>", unsafe_allow_html=True)
        with st.form("form_agregar_paciente"):
            nuevo_nombre = st.text_input("Nombre y Apellidos")
            nueva_edad = st.text_input("Edad")
            nuevo_sexo = st.selectbox("Sexo", options=["Masculino", "Femenino"])
            nueva_direccion = st.text_input("Dirección")
            nuevo_dni = st.text_input("DNI")
            nuevo_telefono = st.text_input("Teléfono")
            nuevo_sintomas = st.text_area("Síntomas previos")
            foto_ojo_derecho = st.file_uploader("Foto ojo derecho", type=["png", "jpg", "jpeg"], key="ojo_derecho")
            foto_ojo_izquierdo = st.file_uploader("Foto ojo izquierdo", type=["png", "jpg", "jpeg"], key="ojo_izquierdo")
            submit_nuevo_paciente = st.form_submit_button("Agregar Paciente")

            if submit_nuevo_paciente:
                if not (nuevo_nombre and nueva_edad and nuevo_sexo and nueva_direccion and nuevo_dni and nuevo_telefono):
                    st.error("Todos los campos son obligatorios.")
                else:
                    guardar_datos_paciente(nuevo_nombre, nueva_edad, nuevo_sexo, nueva_direccion, nuevo_dni, nuevo_telefono, nuevo_sintomas, foto_ojo_derecho, foto_ojo_izquierdo, None)
                    st.success("Paciente agregado correctamente.")
                    st.experimental_set_query_params(refresh=True)

            # Predicción en el momento de subir la imagen del ojo derecho
            if foto_ojo_derecho:
                img_derecho = Image.open(foto_ojo_derecho)
                st.image(img_derecho, caption="Imagen ojo derecho cargada", use_column_width=True)
                probabilidad_derecho = predict_glaucoma(img_derecho)
                if probabilidad_derecho >= 0.5:
                    st.success(f"La probabilidad de no tener glaucoma en el ojo derecho es del {probabilidad_derecho * 100:.2f}%.")
                else:
                    st.warning(f"La probabilidad de tener glaucoma en el ojo derecho es del {(1 - probabilidad_derecho) * 100:.2f}%.")

            # Predicción en el momento de subir la imagen del ojo izquierdo
            if foto_ojo_izquierdo:
                img_izquierdo = Image.open(foto_ojo_izquierdo)
                st.image(img_izquierdo, caption="Imagen ojo izquierdo cargada", use_column_width=True)
                probabilidad_izquierdo = predict_glaucoma(img_izquierdo)
                if probabilidad_izquierdo >= 0.5:
                    st.success(f"La probabilidad de no tener glaucoma en el ojo izquierdo es del {probabilidad_izquierdo * 100:.2f}%.")
                else:
                    st.warning(f"La probabilidad de tener glaucoma en el ojo izquierdo es del {(1 - probabilidad_izquierdo) * 100:.2f}%.")

    if st.session_state.paciente_seleccionado:
        paciente = st.session_state.paciente_seleccionado
        nombre = paciente.get('nombre', '')
        edad = paciente.get('edad', '')
        sexo = paciente.get('sexo', '')
        direccion = paciente.get('direccion', '')
        dni = paciente.get('dni', '')
        telefono = paciente.get('telefono', '')
        sintomas_previos = paciente.get('sintomas_previos', '')
        foto_derecho = paciente.get('foto_ojo_derecho', None)
        foto_izquierdo = paciente.get('foto_ojo_izquierdo', None)
        reporte = paciente.get('reporte', '')
        prediccion_derecho = paciente.get("prediccion_ojo_derecho", None)
        prediccion_izquierdo = paciente.get("prediccion_ojo_izquierdo", None)

        st.markdown(f"<h3>Paciente: {nombre}</h3>", unsafe_allow_html=True)
        
        # Mostrar resultados de predicciones como alertas visuales en el historial
        if prediccion_derecho is not None:
            st.write("**Resultado del ojo derecho:**")
            if prediccion_derecho >= 0.5:
                st.success(f"Alta probabilidad de NO tener glaucoma en el ojo derecho: {prediccion_derecho * 100:.2f}%")
            else:
                st.warning(f"Alta probabilidad de tener glaucoma en el ojo derecho: {(1 - prediccion_derecho) * 100:.2f}%")
        
        if prediccion_izquierdo is not None:
            st.write("**Resultado del ojo izquierdo:**")
            if prediccion_izquierdo >= 0.5:
                st.success(f"Alta probabilidad de NO tener glaucoma en el ojo izquierdo: {prediccion_izquierdo * 100:.2f}%")
            else:
                st.warning(f"Alta probabilidad de tener glaucoma en el ojo izquierdo: {(1 - prediccion_izquierdo) * 100:.2f}%")

        seleccion = st.radio("Selecciona una opción", ("Historial Médico", "Reporte"))

        if seleccion == "Historial Médico":
            with st.form("form_historial"):
                nombre = st.text_input("Nombre y Apellidos", value=nombre)
                edad = st.text_input("Edad", value=edad)
                sexo = st.selectbox("Sexo", options=["Masculino", "Femenino"], index=0 if sexo == "Masculino" else 1)
                direccion = st.text_input("Dirección", value=direccion)
                dni = st.text_input("DNI", value=dni)
                telefono = st.text_input("Teléfono", value=telefono)
                sintomas_previos = st.text_area("Síntomas previos", value=sintomas_previos)

                foto_ojo_derecho = st.file_uploader("Foto ojo derecho", type=["png", "jpg", "jpeg"])
                foto_ojo_izquierdo = st.file_uploader("Foto ojo izquierdo", type=["png", "jpg", "jpeg"])

                if foto_derecho:
                    st.image(foto_derecho, caption="Foto ojo derecho", use_column_width=True)
                if foto_izquierdo:
                    st.image(foto_izquierdo, caption="Foto ojo izquierdo", use_column_width=True)

                submit_historial = st.form_submit_button("Guardar Historial")

            if submit_historial:
                guardar_datos_paciente(nombre, edad, sexo, direccion, dni, telefono, sintomas_previos, foto_ojo_derecho, foto_ojo_izquierdo, reporte)
                st.success("Historial médico guardado correctamente.")
                st.experimental_set_query_params(refresh=True)

        elif seleccion == "Reporte":
            st.markdown("<h3>Reporte del paciente</h3>", unsafe_allow_html=True)
            with st.form("form_reporte"):
                reporte = st.text_area("Escribe el reporte aquí:", value=reporte, height=200)
                submit_reporte = st.form_submit_button("Guardar Reporte")

            if submit_reporte:
                guardar_datos_paciente(nombre, edad, sexo, direccion, dni, telefono, sintomas_previos, foto_derecho, foto_ojo_izquierdo, reporte)
                st.success("Reporte guardado correctamente.")
                st.experimental_set_query_params(refresh=True)

            if st.button("Generar PDF"):
                pdf_file = generar_pdf(nombre, edad, sexo, direccion, dni, telefono, sintomas_previos, reporte, foto_derecho, foto_ojo_izquierdo)
                with open(pdf_file, "rb") as pdf:
                    st.download_button("Descargar PDF", pdf, file_name=f"Reporte_{nombre}.pdf")

    if st.button("Cerrar sesión"):
        st.session_state.acceso_concedido = False
        st.experimental_set_query_params(refresh=True)
