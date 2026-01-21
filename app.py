import streamlit as st
import google.generativeai as genai
from supabase import create_client
import os

# 1. Configurare Pagina Mobil
st.set_page_config(page_title="Axternum Mobile", page_icon="🛡️")

# 2. Conectare la Servicii (Secrete)
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        return create_client(url, key)
    except Exception as e:
        st.error(f"Eroare de configurare: {e}")
        return None

supabase = init_connection()
model = genai.GenerativeModel('models/gemini-2.5-flash-lite-preview-09-2025')

# 3. Interfața de Logare / Înregistrare
if 'user' not in st.session_state:
    st.title("🛡️ Axternum Universum")
    tab_log, tab_reg = st.tabs(["Conectare", "Înregistrare"])

    with tab_reg:
        new_user = st.text_input("Alege Nume Erou:", key="reg_user")
        new_pass = st.text_input("Parolă Nouă:", type="password", key="reg_pass")
        if st.button("Creează Cont"):
            if new_user and new_pass:
                # Verificăm dacă userul există deja
                check = supabase.table('players').select("*").eq('username', new_user).execute()
                if not check.data:
                    stats = {"username": new_user, "password": new_pass, "level": 1, "shards": 100, "inventory": [], "hp": 100}
                    supabase.table('players').insert(stats).execute()
                    st.success("Cont creat cu succes! Mergi la tab-ul Conectare.")
                else:
                    st.error("Acest nume este deja ocupat!")
            else:
                st.warning("Te rugăm să completezi toate câmpurile.")

    with tab_log:
        user = st.text_input("Nume Erou:", key="log_user")
        password = st.text_input("Parolă:", type="password", key="log_pass")
        if st.button("Intră în Univers"):
            res = supabase.table('players').select("*").eq('username', user).eq('password', password).execute()
            if res.data:
                st.session_state.user = res.data[0]
                st.rerun()
            else:
                st.error("Nume sau parolă incorectă!")

# 4. JOCUL ACTIV
else:
    u = st.session_state.user
    st.sidebar.title(f"👤 {u['username']}")
    st.sidebar.metric("Shards", u['shards'])
    st.sidebar.progress(u['hp'] / 100, text=f"HP: {u['hp']}%")

    # PANOU ADMIN (Doar pentru tine)
    if u['username'] == "AXTERNUM":
        with st.sidebar.expander("🛠️ Panou Admin"):
            st.write("Control Global:")
            if st.button("Vindecă-mă (100 HP)"):
                supabase.table('players').update({"hp": 100}).eq('username', u['username']).execute()
                st.rerun()

    tab1, tab2, tab3 = st.tabs(["⚔️ Aventură", "🛒 Magazin", "📜 Clasament"])

    with tab1:
        st.subheader("Misiune curentă")
        if st.button("Cere Misiune de la AI"):
            with st.spinner("Se stabilește legătura narativă..."):
                prompt = f"Ești un AI sci-fi. Salută-l pe {u['username']} și dă-i o misiune scurtă de 2 rânduri."
                response = model.generate_content(prompt)
                st.info(response.text)

    with tab2:
        st.write("Obiecte disponibile:")
        if st.button("Cumpără Scut (50 Shards)"):
            if u['shards'] >= 50:
                new_shards = u['shards'] - 50
                u['inventory'].append("Scut")
                supabase.table('players').update({"shards": new_shards, "inventory": u['inventory']}).eq('username', u['username']).execute()
                st.session_state.user['shards'] = new_shards
                st.success("Ai cumpărat un Scut!")
                st.rerun()

    with tab3:
        st.subheader("Top Exploratori")
        res = supabase.table('players').select("username, shards, level").order('shards', desc=True).limit(10).execute()
        st.table(res.data)

    if st.button("Ieșire din Joc"):
        del st.session_state.user
        st.rerun()