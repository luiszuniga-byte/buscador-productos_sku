import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
import os
import re

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Buscador de Productos", layout="wide")

# =========================
# ESTILOS (FONDO + UI)
# =========================
st.markdown(
    """
    <style>

    /* =========================
       FONDO DEGRADADO GLOBAL
    ========================= */
    .stApp {
        background: linear-gradient(
            135deg,
            #ff9a3c 0%,
            #ffb347 40%,
            #ffe29a 100%
        );
    }

    /* =========================
       CONTENEDOR PRINCIPAL
    ========================= */
    .block-container {
        padding-bottom: 85px;
        background-color: rgba(255, 255, 255, 0.88);
        border-radius: 14px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0px 6px 18px rgba(0,0,0,0.15);
    }

    /* =========================
       FOOTER
    ========================= */
    .footer-lz {
        position: fixed;
        bottom: 10px;
        left: 10px;
        background: linear-gradient(145deg, #1b1b1b, #111111);
        color: #b5b5b5;
        padding: 7px 14px;
        border-radius: 8px;
        font-size: 12px;
        z-index: 9999999;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.65),
                    -2px -2px 5px rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.06);
        letter-spacing: 0.3px;
        font-weight: 500;
        pointer-events: none;
    }

    </style>

    <div class="footer-lz">✦ Hecho por LZ ✦</div>
    """,
    unsafe_allow_html=True
)

# =========================
# SESSION INIT
# =========================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "sku_input" not in st.session_state:
    st.session_state.sku_input = ""

# =========================
# LOGO
# =========================
try:
    logo = Image.open("logo.png")
    st.image(logo, width=110)
except:
    pass

# =========================
# TITULO
# =========================
st.markdown(
    """
    <h1 style="text-align:center;font-size:34px;margin-top:10px;margin-bottom:25px;">
    🔎 Buscador por SKU_ENCRIPTADO
    </h1>
    """,
    unsafe_allow_html=True
)

# =========================
# UTIL NORMALIZAR RUT
# =========================
def normalizar_rut(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().upper()
    texto = re.sub(r"\s+", "", texto)
    return texto

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

    df["Usuario"] = df["Usuario"].apply(normalizar_rut)
    df["Password"] = df["Password"].astype(str).str.strip()

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

        usuario = normalizar_rut(usuario)
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
ARCHIVO_PARQUET = "data.parquet"

@st.cache_data
def cargar_datos():
    if not os.path.exists(ARCHIVO_PARQUET):
        st.error("❌ No se encontró data.parquet")
        st.stop()

    df = pd.read_parquet(ARCHIVO_PARQUET)
    df.columns = df.columns.str.strip()
    return df

df = cargar_datos()

# =========================
# VALIDACIÓN
# =========================
if "SKU_ENCRIPTADO" not in df.columns:
    st.error("❌ No existe SKU_ENCRIPTADO")
    st.stop()

# =========================
# BOTONES
# =========================
colA, colB, colC = st.columns([1, 1, 6])

with colA:
    if st.button("🚪 Salir"):
        st.session_state.autenticado = False
        st.session_state.sku_input = ""
        st.rerun()

with colB:
    if st.button("🧹 Limpiar"):
        st.session_state.sku_input = ""
        st.rerun()

# =========================
# BUSCADOR
# =========================
st.divider()

st.text_input("Ingrese SKU_ENCRIPTADO", key="sku_input")

busqueda = st.session_state.sku_input

# =========================
# RESULTADOS
# =========================
if busqueda:

    resultado = df[
        df["SKU_ENCRIPTADO"].astype(str).str.upper().str.strip()
        == str(busqueda).upper().strip()
    ]

    resultado = resultado.drop_duplicates(subset=["SKU_ENCRIPTADO"])

    st.write(f"Resultados encontrados: {len(resultado)}")

    if not resultado.empty:
        st.dataframe(resultado, use_container_width=True, hide_index=True)

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
st.caption(f"Usuario conectado: {st.session_state.get('usuario','')}")
st.caption(f"Total registros cargados: {len(df)}")

# =========================
# LOG ADMIN
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
