import streamlit as st
import pandas as pd
from PIL import Image

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Buscador de Productos", layout="wide")

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
# USUARIOS (LOGIN)
# =========================
@st.cache_data
def cargar_usuarios():
    df = pd.read_csv(
        "base_usuarios.csv",
        dtype=str,
        encoding="utf-8",
        sep=";"   # 🔥 CLAVE
    )

    df.columns = df.columns.str.strip()
    return df

usuarios_df = cargar_usuarios()

# =========================
# LOGIN
# =========================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:

    st.subheader("🔐 Acceso al sistema")

    usuario = st.text_input("Usuario (RUT)")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        usuario = usuario.strip()

        validacion = usuarios_df[
            (usuarios_df["Usuario"] == usuario) &
            (usuarios_df["Password"] == password)
        ]

        if not validacion.empty:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
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
# BUSCADOR
# =========================
st.divider()

busqueda = st.text_input("Ingrese SKU_ENCRIPTADO")

if busqueda:

    resultado = df[df["SKU_ENCRIPTADO"].str.upper() == busqueda.upper()]
    resultado = resultado.drop_duplicates(subset=["SKU_ENCRIPTADO"])

    st.write(f"Resultados encontrados: {len(resultado)}")

    if not resultado.empty:
        st.dataframe(resultado, use_container_width=True)

        if "URL Imagen" in resultado.columns:
            st.subheader("Imágenes")

            for _, row in resultado.iterrows():
                if pd.notna(row["URL Imagen"]):
                    try:
                        st.image(row["URL Imagen"], width=120)
                    except:
                        pass
    else:
        st.warning("No se encontraron resultados")

# =========================
# INFO GENERAL
# =========================
st.caption(f"Usuario conectado: {st.session_state.get('usuario', '')}")
st.caption(f"Total registros cargados: {len(df)}")
