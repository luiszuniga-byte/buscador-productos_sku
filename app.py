import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
import os

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Buscador de Productos", layout="wide")

# =========================
# SESSION INIT
# =========================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "sku_input" not in st.session_state:
    st.session_state.sku_input = ""

if "busqueda" not in st.session_state:
    st.session_state.busqueda = ""

# =========================
# LOGO + TITULO
# =========================
col1, col2 = st.columns([1, 5])

with col1:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=120)
    except:
        pass

with col2:
    st.title("🔎 Buscador por SKU_ENCRIPTADO")

# =========================
# LOG
# =========================
def registrar_log(usuario):
    ip = "desconocida"

    try:
        ip = st.context.headers.get("X-Forwarded-For", "desconocida")
    except:
        pass

    log = pd.DataFrame([{
        "usuario": usuario,
        "ip": ip,
        "fecha_hora": datetime.now()
    }])

    archivo = "log_accesos.csv"

    if os.path.exists(archivo):
        log.to_csv(archivo, mode="a", header=False, index=False)
    else:
        log.to_csv(archivo, index=False)

# =========================
# USUARIOS
# =========================
@st.cache_data
def cargar_usuarios():
    df = pd.read_csv(
        "base_usuarios.csv",
        dtype=str,
        encoding="utf-8",
        sep=";"
    )

    df.columns = df.columns.str.strip()
    df["Usuario"] = df["Usuario"].str.strip()
    df["Password"] = df["Password"].str.strip()

    return df.drop_duplicates(subset=["Usuario"])

usuarios_df = cargar_usuarios()

# =========================
# LOGIN
# =========================
if not st.session_state.autenticado:

    st.subheader("🔐 Acceso al sistema")

    usuario = st.text_input("Usuario (RUT)")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        usuario = usuario.strip()
        password = password.strip()

        validacion = usuarios_df[
            (usuarios_df["Usuario"] == usuario) &
            (usuarios_df["Password"] == password)
        ]

        if not validacion.empty:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario

            registrar_log(usuario)

            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

# =========================
# DATA PRODUCTOS
# =========================
RUTA_ARCHIVO = "https://raw.githubusercontent.com/luiszuniga-byte/buscador-productos_sku/main/Template_Stock.csv"

@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        RUTA_ARCHIVO,
        dtype=str,
        encoding="latin1",
        sep=";",
        engine="python"
    )

    df.columns = df.columns.str.strip()
    return df

df = cargar_datos()

# =========================
# VALIDACIÓN
# =========================
if "SKU_ENCRIPTADO" not in df.columns:
    st.error("❌ No existe la columna SKU_ENCRIPTADO")
    st.stop()

# =========================
# BOTONES SUPERIORES
# =========================
colA, colB, colC = st.columns([1, 1, 6])

with colA:
    if st.button("🚪 Salir"):
        st.session_state.autenticado = False
        st.session_state.sku_input = ""
        st.session_state.busqueda = ""
        st.rerun()

with colB:
    if st.button("🧹 Limpiar"):
        st.session_state.sku_input = ""
        st.session_state.busqueda = ""
        st.rerun()

# =========================
# BUSCADOR (FIX REAL)
# =========================
st.divider()

st.session_state.sku_input = st.text_input(
    "Ingrese SKU_ENCRIPTADO",
    value=st.session_state.sku_input
)

# sincronización real
st.session_state.busqueda = st.session_state.sku_input

# =========================
# RESULTADOS
# =========================
if st.session_state.busqueda:

    resultado = df[df["SKU_ENCRIPTADO"].str.upper() == st.session_state.busqueda.upper()]
    resultado = resultado.drop_duplicates(subset=["SKU_ENCRIPTADO"])

    st.write(f"Resultados encontrados: {len(resultado)}")

    if not resultado.empty:
        st.dataframe(resultado, use_container_width=True)

        if "URL Imagen" in resultado.columns:
            st.subheader("Imágenes")

            for _, row in resultado.iterrows():
                if pd.notna(row["URL Imagen"]):
                    st.image(row["URL Imagen"], width=120)
    else:
        st.warning("No se encontraron resultados")

# =========================
# INFO
# =========================
st.caption(f"Usuario conectado: {st.session_state.get('usuario', '')}")
st.caption(f"Total registros cargados: {len(df)}")

# =========================
# LOG SOLO ADMIN (OCULTO)
# =========================
if st.session_state.get("usuario") == "14160711-1":

    st.divider()
    st.subheader("📊 Log de Accesos")

    if os.path.exists("log_accesos.csv"):
        log_df = pd.read_csv("log_accesos.csv")

        st.dataframe(log_df, use_container_width=True)

        with open("log_accesos.csv", "rb") as f:
            st.download_button(
                "📥 Descargar Log",
                f,
                file_name="log_accesos.csv"
            )
    else:
        st.info("No hay registros aún")
