import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
from mensajeros import lista_mensajeros


# zona horaria de Colombia
colombia = pytz.timezone("America/Bogota")

# Conexión a Google Sheets
def conectar_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(credentials)
    sheet = client.open("registro_despacho").sheet1
    return sheet
#Título de la aplicación
st.markdown(
    """
    <h1 style='text-align: center; color: #19277F;'>📦 Registro de despacho - Muelles y Frenos Simón Bolívar</h1>
    """,
    unsafe_allow_html=True
)
# Línea decorativa
st.markdown("<hr style='border: none; height: 4px; background-color: #fab70e;'>", unsafe_allow_html=True)

codigo = st.text_input("Ingrese el Número de guia (*)")
opcion = st.selectbox(" Asignar mensajero (*)", lista_mensajeros + ["OTRO"])

if opcion == "OTRO":
    mensajero = st.text_input(" Escribe el nombre del mensajero:")
else:
    mensajero = opcion

col0, col1, col2, col3 = st.columns([3, 3, 3, 3])

# Registrar despacho
with col1:
    if st.button("Registrar Despacho"):
        if codigo and mensajero:
            sheet = conectar_google_sheet()
            registros = sheet.get_all_records()
            
            # Validar si ya existe despacho para este código
            codigo_existente = any(str(fila["codigo"]) == codigo and fila["hora_despacho"] != "" for fila in registros)
            
            if codigo_existente:
                st.warning("⚠️ Ya se ha registrado un despacho con este código.")
            else:
                hora_despacho = datetime.now(colombia).strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([codigo, mensajero, hora_despacho, "", ""])
                st.success(f"✅ Despacho registrado exitosamente para el código {codigo} con {mensajero}.")
        else:
            st.error("❌ Por favor, ingrese el código y seleccione un mensajero.")

# Registrar entrega
with col2:
    if st.button("Registrar Entrega"):
        if codigo:
            sheet = conectar_google_sheet()
            registros = sheet.get_all_records()

            encontrado = False
            for i, fila in enumerate(registros):
                if str(fila["codigo"]) == codigo:
                    if fila["hora_entrega"] != "":
                        st.warning("⚠️ Este código ya tiene registrada una entrega.")
                    elif fila["hora_despacho"] == "":
                        st.warning("⚠️ No se ha registrado despacho previo para este código.")
                    else:
                        hora_entrega = datetime.now(colombia).strftime("%Y-%m-%d %H:%M:%S")
                        # Calcular tiempo total
                        hora_despacho_dt = datetime.strptime(fila["hora_despacho"], "%Y-%m-%d %H:%M:%S")
                        hora_entrega_dt = datetime.strptime(hora_entrega, "%Y-%m-%d %H:%M:%S")
                        tiempo_total = str(hora_entrega_dt - hora_despacho_dt)
                      
                        sheet.update(f"D{i+2}", [[hora_entrega]])
                        sheet.update(f"E{i+2}", [[tiempo_total]])
                        st.success(f"✅ Entrega registrada correctamente.")
                    encontrado = True
                    break
            if not encontrado:
                st.warning("⚠️ No se ha registrado despacho previo para este código.")
        else:
            st.error("❌ Por favor, ingrese el código.")

# Línea decorativa
st.markdown("<hr style='border: none; height: 4px; background-color: #fab70e;'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 1, 3])  
with col2:
    st.image("logo.png", width=200)

st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #19277f;">
        <p>© 2025 Muelles y Frenos Simón Bolívar. Todos los derechos reservados.</p>
    </div>
""", unsafe_allow_html=True)
