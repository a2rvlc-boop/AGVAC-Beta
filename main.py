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
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; color: #9e9e9e; font-size: 11px; padding-bottom: 10px; background-color: white; width: 100%; }
    .login-footer-version { text-align: center; color: #9e9e9e; font-size: 12px; margin-top: 20px; }
    
    /* Caja corporativa Sobre AGVAC */
    .about-box { 
        background-color: #f8f9fa; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 6px solid #005b7f;
        margin-top: 20px;
        font-size: 14px;
        color: #333;
        line-height: 1.6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .logo-container-about {
        display: flex;
        justify-content: center;
        gap: 30px;
        align-items: center;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ARCHIVOS Y DATOS INICIALES ---
DB_FILE = "datos_agvac.csv"
STOCK_FILE = "stock_agvac.csv"
URL_LOGO_MRG = "https://raw.githubusercontent.com/a2rvlc-boop/AGVAC/refs/heads/main/logomrg.png"
URL_LOGO_AGVAC = "https://raw.githubusercontent.com/a2rvlc-boop/AGVAC/refs/heads/main/logo_agvac.png"

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

# --- BLOQUE CORPORATIVO "SOBRE AGVAC" ---
SOBRE_AGVAC_HTML = f"""
<div class="about-box">
    <div class="logo-container-about">
        <img src="{URL_LOGO_AGVAC}" width="70">
        <img src="{URL_LOGO_MRG}" width="70">
    </div>
    <h3 style="text-align:center; margin-top:0;">Sobre AGVAC</h3>
    <p><b>AGVAC</b> es una solución tecnológica diseñada específicamente para optimizar la gestión de inventarios de vacunas en entornos sanitarios. Nuestra misión es simplificar el flujo de trabajo del personal sanitario, automatizando la carga administrativa y minimizando el riesgo de errores de stock.</p>
    <p>Esta aplicación ha sido diseñada y desarrollada por <b>MRG Healthcare Applications</b>, un grupo multidisciplinar de trabajadores del sector de la salud e informática dedicados al diseño de nuevas herramientas digitales que den respuesta a los desafíos reales de la sanidad moderna.</p>
    <ul>
        <li><b>Registro Automatizado:</b> Trazabilidad de dosis administradas en gestión de stock.</li>
        <li><b>Gestión de Stock:</b> Alertas inteligentes basadas en umbrales críticos.</li>
        <li><b>Análisis:</b> Visualización de datos para la planificación estratégica.</li>
    </ul>
</div>
"""

# --- 3. CONTROL DE ACCESO ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

def login():
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown(f'<div style="text-align:center; margin-top:50px;"><img src="{URL_LOGO_AGVAC}" width="180"></div>', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>Acceso AGVAC</h2>", unsafe_allow_html=True)
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if usuario == "agvac" and password == "agvac":
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Error de credenciales")
        
        # Mostrar descripción profesional en el login
        st.markdown(SOBRE_AGVAC_HTML, unsafe_allow_html=True)
        st.markdown("<div class='login-footer-version'>MRGAGVAC2026.1.7.2 | Beta AGVAC</div>", unsafe_allow_html=True)

if not st.session_state.autenticado:
    login()
    st.stop()

# --- 4. INTERFAZ PRINCIPAL ---
if 'cesta' not in st.session_state: st.session_state.cesta = []

# Sidebar
if st.sidebar.button("🔒 Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

# Información corporativa en Sidebar
with st.sidebar.expander("ℹ️ Información AGVAC"):
    st.markdown(SOBRE_AGVAC_HTML, unsafe_allow_html=True)

st.sidebar.divider()
df_alertas = pd.read_csv(STOCK_FILE)
alertas = df_alertas[df_alertas['Cantidad'] <= df_alertas['Minimo']]
if not alertas.empty:
    st.sidebar.error("⚠️ STOCK CRÍTICO")
    for _, fila in alertas.iterrows():
        st.sidebar.warning(f"{fila['Vacuna']}: {int(fila['Cantidad'])} unidades")

# Cabecera principal con logos
col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_izq: st.image(URL_LOGO_MRG)
with col_centro: st.markdown("<h1 style='text-align: center; font-size: 50px;'>AGVAC</h1>", unsafe_allow_html=True)
with col_der: st.image(URL_LOGO_AGVAC)

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
                    nueva = {"Fecha": ahora.strftime("%Y-%m-%d %H:%M"), "Vacuna": item, "Semana": ahora.strftime("%U-%Y"), "Mes": ahora.strftime("%m-%Y"), "Año": ahora.strftime("%Y")}
                    df_hist = pd.concat([df_hist, pd.DataFrame([nueva])], ignore_index=True)
                    if item in df_stock['Vacuna'].values:
                        idx = df_stock.index[df_stock['Vacuna'] == item].tolist()[0]
                        df_stock.at[idx, 'Cantidad'] -= 1
                
                df_hist.to_csv(DB_FILE, index=False)
                df_stock.to_csv(STOCK_FILE, index=False)
                st.session_state.cesta = []
                st.success("¡Registrado!")
                st.rerun()
        else: st.info("No hay vacunas en la cesta")

# --- TAB 2: HISTORIAL ---
with tab_hist:
    st.subheader("📋 Gestión de Registros")
    df_ver = pd.read_csv(DB_FILE)
    if not df_ver.empty:
        df_display = df_ver.iloc[::-1].copy()
        id_eliminar = st.selectbox("Eliminar registro (devuelve dosis):", 
                                 options=df_display.index, 
                                 format_func=lambda x: f"{df_display.loc[x, 'Fecha']} | {df_display.loc[x, 'Vacuna']}")
        
        if st.button("🗑️ Eliminar y Devolver Dosis"):
            vacuna_retorno = df_ver.loc[id_eliminar, 'Vacuna']
            df_stock_ret = pd.read_csv(STOCK_FILE)
            if vacuna_retorno in df_stock_ret['Vacuna'].values:
                idx_s = df_stock_ret.index[df_stock_ret['Vacuna'] == vacuna_retorno].tolist()[0]
                df_stock_ret.at[idx_s, 'Cantidad'] += 1
                df_stock_ret.to_csv(STOCK_FILE, index=False)
            df_ver.drop(id_eliminar).to_csv(DB_FILE, index=False)
            st.success("Registro actualizado.")
            st.rerun()
        st.divider()
        st.dataframe(df_display, use_container_width=True)

# --- TAB 3: ESTADÍSTICAS ---
with tab_graf:
    df_g = pd.read_csv(DB_FILE)
    if not df_g.empty:
        c = df_g['Vacuna'].value_counts().reset_index()
        fig = px.pie(c, values='count', names='Vacuna', color='Vacuna', color_discrete_map=st.session_state.lista_vacunas, hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 4: STOCK ---
with tab_conf:
    df_st = pd.read_csv(STOCK_FILE)
    st.dataframe(df_st, use_container_width=True)
    col_st1, col_st2 = st.columns(2)
    with col_st1:
        st.write("### Ajustar Stock")
        v_a = st.selectbox("Elegir:", df_st['Vacuna'])
        n_a = st.number_input("Cantidad (+/-):", step=1)
        if st.button("Actualizar"):
            idx_a = df_st.index[df_st['Vacuna'] == v_a].tolist()[0]
            df_st.at[idx_a, 'Cantidad'] += n_a
            df_st.to_csv(STOCK_FILE, index=False); st.rerun()
    with col_st2:
        st.write("### Nueva Vacuna")
        n_v = st.text_input("Nombre:")
        n_c = st.color_picker("Color:", "#005b7f")
        if st.button("Añadir"):
            if n_v:
                nueva_v = pd.DataFrame([{"Vacuna": n_v, "Cantidad": 25, "Minimo": 5}])
                pd.concat([df_st, nueva_v], ignore_index=True).to_csv(STOCK_FILE, index=False)
                st.session_state.lista_vacunas[n_v] = n_c; st.rerun()

st.markdown(f'<div class="footer">MRGAGVAC2026.1.7.2 | Beta AGVAC</div>', unsafe_allow_html=True)
