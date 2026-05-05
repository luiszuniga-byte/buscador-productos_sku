import streamlit as st
import pandas as pd

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Buscador de Productos", layout="wide")
st.title("🔎 Buscador por SKU_ENCRIPTADO")

# =========================
# RUTA ARCHIVO
# =========================
RUTA_ARCHIVO = r"C:\Users\luisz\TRABAJO\SOLICITUDES\18.PROYECTO_PARTSFLOW\CREAMOS_BUSCADOR\buscador-productos\Template_Stock.csv"

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        RUTA_ARCHIVO,
        dtype=str,
        encoding="latin1",   # importante si el archivo viene de Excel/Windows
        sep=";",             # ajusta si tu CSV usa coma ","
        engine="python"
    )

    # limpieza de nombres de columnas
    df.columns = df.columns.str.strip()

    return df

df = cargar_datos()

# =========================
# VALIDACIÓN
# =========================
if "SKU_ENCRIPTADO" not in df.columns:
    st.error("❌ No existe la columna SKU_ENCRIPTADO en el archivo")
    st.stop()

# =========================
# BUSCADOR
# =========================
busqueda = st.text_input("Ingrese SKU_ENCRIPTADO")

if busqueda:
    resultado = df[df["SKU_ENCRIPTADO"].str.contains(busqueda, case=False, na=False)]

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
st.caption(f"Total registros cargados: {len(df)}")