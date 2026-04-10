import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AGVAC", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .stButton>button { background-color: #005b7f; color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    .stButton>button:hover { background-color: #00425c; color: white; }
    h1, h2, h3 { color: #004561; font-family: 'Arial', sans-serif; }
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; color: #9e9e9e; font-size: 11px; padding-bottom: 10px; }
    .login-footer-version { position: fixed; bottom: 20px; left: 0; width: 100%; text-align: center; color: #9e9e9e; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ARCHIVOS Y DATOS INICIALES ---
DB_FILE = "datos_agvac.csv"
STOCK_FILE = "stock_agvac.csv"

# Mínimos críticos por defecto
MINIMOS_DEFAULT = {
    "Herpes Zoster": 20, "Neumococo20": 20, "ProQuad": 2, "VariVax": 2,
    "Priorix": 2, "Mpox": 2, "GRIPE": 2, "VPH": 10, "HepB": 10,
    "HepB Hemo": 5, "HepA": 10, "HepA+B": 5, "Meningitis ACW135Y": 10,
    "Meningitis B": 5, "Tetanos-Difteria": 20, "Boostrix": 5,
    "Hexa": 5, "Vivotif": 15, "Fiebre Tifoidea": 10, "Fiebre Amarilla": 10, "COVID": 2
}

if 'lista_vacunas' not in st.session_state:
    st.session_state.lista_vacunas = {
        "Herpes Zoster": "#FF8C00", "Neumococo20": "#00008B", "ProQuad": "#808080",
        "VariVax": "#FF0000", "Priorix": "#A9A9A9", "Mpox": "#FFFF00",
        "GRIPE": "#ADD8E6", "VPH": "#AEC6CF", "HepB": "#9ACD32",
        "HepB Hemo": "#808000", "HepA": "#000080", "HepA+B": "#90EE90",
        "Meningitis ACW135Y": "#D3D3D3", "Meningitis B": "#800000",
        "Tetanos-Difteria": "#FF4500", "Boostrix": "#800080", "Hexa": "#7DF9FF",
        "Vivotif": "#77DD77", "Fiebre Tifoidea": "#00FF7F", "Fiebre Amarilla": "#CCFF00",
        "COVID": "#E6E6FA"
    }

# Asegurar existencia de archivos
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["Fecha", "Vacuna", "Semana", "Mes", "Año"]).to_csv(DB_FILE, index=False)

if not os.path.exists(STOCK_FILE):
    df_stock_init = pd.DataFrame([
        {"Vacuna": v, "Cantidad": 25, "Minimo": MINIMOS_DEFAULT.get(v, 5)} 
        for v in st.session_state.lista_vacunas.keys()
    ])
    df_stock_init.to_csv(STOCK_FILE, index=False)

# --- 3. CONTROL DE ACCESO ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

def login():
    URL_LOGO_LOGIN = "https://raw.githubusercontent.com/a2rvlc-boop/AGVAC/refs/heads/main/logo_agvac.png"
    st.markdown(f'<div style="text-align:center; margin-top:50px;"><img src="{URL_LOGO_LOGIN}" width="180"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>Acceso AGVAC</h2>", unsafe_allow_html=True)
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if usuario == "agvac" and password == "agvac":
            st.session_state.autenticado = True
            st.rerun()
        else: st.error("Error de credenciales")
    st.markdown("<div class='login-footer-version'>MRGAGVAC2026.1.7.1 | Beta AGVAC</div>", unsafe_allow_html=True)

if not st.session_state.autenticado:
    login()
    st.stop()

# --- 4. INTERFAZ PRINCIPAL ---
if 'cesta' not in st.session_state: st.session_state.cesta = []

# Sidebar con alertas de Stock
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

st.sidebar.divider()
df_alertas = pd.read_csv(STOCK_FILE)
alertas = df_alertas[df_alertas['Cantidad'] <= df_alertas['Minimo']]
if not alertas.empty:
    st.sidebar.error("⚠️ STOCK CRÍTICO")
    for _, fila in alertas.iterrows():
        st.sidebar.warning(f"{fila['Vacuna']}: {int(fila['Cantidad'])} unidades")

# Cabecera
col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_izq: st.image("https://raw.githubusercontent.com/a2rvlc-boop/AGVAC/refs/heads/main/logomrg.png")
with col_centro: st.markdown("<h1 style='text-align: center; font-size: 50px;'>AGVAC</h1>", unsafe_allow_html=True)
with col_der: st.image("https://raw.githubusercontent.com/a2rvlc-boop/AGVAC/refs/heads/main/logo_agvac.png")

tab_reg, tab_hist, tab_graf, tab_conf = st.tabs(["📝 Registro", "📋 Historial", "📊 Estadísticas", "⚙️ Stock y Catálogo"])

# --- TAB 1: REGISTRO ---
with tab_reg:
    col_s, col_c = st.columns(2)
    with col_s:
        st.subheader("🔍 Seleccionar Vacuna")
        seleccion = st.selectbox("Vacuna:", [""] + list(st.session_state.lista_vacunas.keys()))
        if st.button("➕ Añadir a la lista"):
            if seleccion:
                st.session_state.cesta.append(seleccion)
                st.rerun()
    with col_c:
        st.subheader("📦 Cesta de hoy")
        if st.session_state.cesta:
            for i, item in enumerate(st.session_state.cesta):
                st.write(f"{i+1}. {item}")
            if st.button("✅ GUARDAR Y DESCONTAR STOCK"):
                df_hist = pd.read_csv(DB_FILE)
                df_stock = pd.read_csv(STOCK_FILE)
                ahora = datetime.now()
                for item in st.session_state.cesta:
                    # Guardar Historial
                    nueva = {"Fecha": ahora.strftime("%Y-%m-%d %H:%M"), "Vacuna": item, "Semana": ahora.strftime("%U-%Y"), "Mes": ahora.strftime("%m-%Y"), "Año": ahora.strftime("%Y")}
                    df_hist = pd.concat([df_hist, pd.DataFrame([nueva])], ignore_index=True)
                    # Descontar Stock
                    if item in df_stock['Vacuna'].values:
                        idx = df_stock.index[df_stock['Vacuna'] == item].tolist()[0]
                        df_stock.at[idx, 'Cantidad'] -= 1
                
                df_hist.to_csv(DB_FILE, index=False)
                df_stock.to_csv(STOCK_FILE, index=False)
                st.session_state.cesta = []
                st.success("¡Registrado y Stock descontado!")
                st.rerun()
        else: st.info("No hay vacunas en la cesta")

# --- TAB 2: HISTORIAL (ELIMINACIÓN + DEVOLUCIÓN STOCK) ---
with tab_hist:
    st.subheader("📋 Gestión de Registros")
    df_ver = pd.read_csv(DB_FILE)
    if not df_ver.empty:
        df_display = df_ver.iloc[::-1].copy()
        id_eliminar = st.selectbox("Seleccionar registro para eliminar (devuelve 1 dosis al stock):", 
                                 options=df_display.index, 
                                 format_func=lambda x: f"{df_display.loc[x, 'Fecha']} | {df_display.loc[x, 'Vacuna']}")
        
        if st.button("🗑️ Eliminar Registro y Devolver Dosis"):
            # 1. Identificar vacuna
            vacuna_retorno = df_ver.loc[id_eliminar, 'Vacuna']
            # 2. Sumar al stock
            df_stock_ret = pd.read_csv(STOCK_FILE)
            if vacuna_retorno in df_stock_ret['Vacuna'].values:
                idx_s = df_stock_ret.index[df_stock_ret['Vacuna'] == vacuna_retorno].tolist()[0]
                df_stock_ret.at[idx_s, 'Cantidad'] += 1
                df_stock_ret.to_csv(STOCK_FILE, index=False) # Guardado físico
            
            # 3. Borrar del historial
            df_final = df_ver.drop(id_eliminar)
            df_final.to_csv(DB_FILE, index=False) # Guardado físico
            st.success(f"Dosis de {vacuna_retorno} devuelta al inventario.")
            st.rerun()
            
        st.divider()
        st.dataframe(df_display, use_container_width=True)
    else: st.info("El historial está vacío.")

# --- TAB 3: ESTADÍSTICAS ---
with tab_graf:
    st.subheader("📊 Resumen de Actividad")
    df_g = pd.read_csv(DB_FILE)
    if not df_g.empty:
        c = df_g['Vacuna'].value_counts().reset_index()
        fig = px.pie(c, values='count', names='Vacuna', color='Vacuna', 
                    color_discrete_map=st.session_state.lista_vacunas, hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Sin datos suficientes.")

# --- TAB 4: GESTIÓN DE STOCK Y CATÁLOGO ---
with tab_conf:
    st.subheader("📦 Inventario en Tiempo Real")
    df_st = pd.read_csv(STOCK_FILE)
    st.dataframe(df_st, use_container_width=True)
    
    col_st1, col_st2 = st.columns(2)
    with col_st1:
        st.write("### ➕ / ➖ Ajustar Cantidades")
        v_a = st.selectbox("Elegir Vacuna:", df_st['Vacuna'])
        n_a = st.number_input("Cantidad a modificar (ej: 10 para añadir, -10 para quitar):", step=1)
        if st.button("Actualizar Inventario"):
            idx_a = df_st.index[df_st['Vacuna'] == v_a].tolist()[0]
            df_st.at[idx_a, 'Cantidad'] += n_a
            df_st.to_csv(STOCK_FILE, index=False)
            st.rerun()
            
    with col_st2:
        st.write("### 🆕 Nueva Vacuna")
        n_v = st.text_input("Nombre de la vacuna:")
        n_c = st.color_picker("Color para gráficas:", "#005b7f")
        n_m = st.number_input("Mínimo para alerta:", value=5)
        if st.button("Registrar Vacuna Nueva"):
            if n_v:
                nueva_v = pd.DataFrame([{"Vacuna": n_v, "Cantidad": 25, "Minimo": n_m}])
                df_st = pd.concat([df_st, nueva_v], ignore_index=True)
                df_st.to_csv(STOCK_FILE, index=False)
                st.session_state.lista_vacunas[n_v] = n_c
                st.success(f"{n_v} añadida con éxito.")
                st.rerun()
                
    st.divider()
    st.write("### 🗑️ Eliminar Vacuna del Sistema")
    v_borrar = st.selectbox("Vacuna a borrar por completo:", list(st.session_state.lista_vacunas.keys()))
    if st.button("ELIMINAR DEFINITIVAMENTE"):
        df_st = df_st[df_st['Vacuna'] != v_borrar]
        df_st.to_csv(STOCK_FILE, index=False)
        if v_borrar in st.session_state.lista_vacunas:
            del st.session_state.lista_vacunas[v_borrar]
        st.rerun()

st.markdown('<div class="footer">MRGAGVAC2026.1.7.1 | Beta AGVAC</div>', unsafe_allow_html=True)
