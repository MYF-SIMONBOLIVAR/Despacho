import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
from mensajeros import lista_mensajeros
import json
from io import StringIO

# zona horaria de Colombia
colombia = pytz.timezone("America/Bogota")

# Conexión a Google Sheets
def conectar_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    google_credentials = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(google_credentials, scope)
    client = gspread.authorize(credentials)
    sheet = client.open("registro_despacho").sheet1
    return sheet
# Título
st.markdown(
    """
    <h1 style='text-align: center; color: #19277F;'>📦 Registro de despacho - Muelles y Frenos Simón Bolívar</h1>
    """,
    unsafe_allow_html=True
)
st.markdown("<hr style='border: none; height: 4px; background-color: #fab70e;'>", unsafe_allow_html=True)

# Entradas de datos
codigo = st.text_input("Ingrese el Número de guia (*)")
opcion = st.selectbox(" Asignar mensajero (*)", lista_mensajeros + ["OTRO"])
if opcion == "OTRO":
    mensajero = st.text_input(" Escribe el nombre del mensajero:")
else:
    mensajero = opcion

# Estado de alerta
alerta = None

# Botones
col0, col1, col2, col3 = st.columns([3, 3, 3, 3])

# Registrar Despacho
with col1:
    registrar_despacho = st.button("Registrar Despacho")

# Registrar Entrega
with col2:
    registrar_entrega = st.button("Registrar Entrega")

# Lógica del despacho
if registrar_despacho:
    if codigo and mensajero:
        sheet = conectar_google_sheet()
        registros = sheet.get_all_records()
        codigo_existente = any(str(fila["codigo"]) == codigo and fila["hora_despacho"] != "" for fila in registros)
        if codigo_existente:
            alerta = st.warning("⚠️ Ya se ha registrado un despacho con este código.")
        else:
            hora_despacho = datetime.now(colombia).strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([codigo, mensajero, hora_despacho, "", ""])
            alerta = st.success(f"✅ Despacho registrado exitosamente para el código {codigo} con {mensajero}.")
    else:
        alerta = st.error("❌ Por favor, ingrese el código y seleccione un mensajero.")

# Lógica de entrega
if registrar_entrega:
    if codigo:
        sheet = conectar_google_sheet()
        registros = sheet.get_all_records()
        encontrado = False
        for i, fila in enumerate(registros):
            if str(fila["codigo"]) == codigo:
                if fila["hora_entrega"] != "":
                    alerta = st.warning("⚠️ Este código ya tiene registrada una entrega.")
                elif fila["hora_despacho"] == "":
                    alerta = st.warning("⚠️ No se ha registrado despacho previo para este código.")
                else:
                    hora_entrega = datetime.now(colombia).strftime("%Y-%m-%d %H:%M:%S")
                    hora_despacho_dt = datetime.strptime(fila["hora_despacho"], "%Y-%m-%d %H:%M:%S")
                    hora_entrega_dt = datetime.strptime(hora_entrega, "%Y-%m-%d %H:%M:%S")
                    tiempo_total = str(hora_entrega_dt - hora_despacho_dt)
                    sheet.update(f"D{i+2}", [[hora_entrega]])
                    sheet.update(f"E{i+2}", [[tiempo_total]])
                    alerta = st.success("✅ Entrega registrada correctamente.")
                encontrado = True
                break
        if not encontrado:
            alerta = st.warning("⚠️ No se ha registrado despacho previo para este código.")
    else:
        alerta = st.error("❌ Por favor, ingrese el código.")

# Mostrar alerta fuera del layout
if alerta:
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# Línea final decorativa
st.markdown("<hr style='border: none; height: 4px; background-color: #fab70e;'>", unsafe_allow_html=True)

# Logo y pie de página
col1, col2, col3 = st.columns([3, 1, 3])  
with col2:
    st.image("logo.png", width=200)

st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #19277f;">
        <p>© 2025 Muelles y Frenos Simón Bolívar. Todos los derechos reservados.</p>
    </div>
""", unsafe_allow_html=True)
