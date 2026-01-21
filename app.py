import streamlit as st
import google.generativeai as genai
from supabase import create_client
import os
import random

# Configurare Pagina Mobil
st.set_page_config(page_title="Axternum Mobile", page_icon="⚔️")

# Inițializare conexiuni (Secrete)
try:
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    genai.configure(api_key=os.environ.get('GEMINI_KEY'))
    supabase = create_client(url, key)
    model = genai.GenerativeModel('models/gemini-2.5-flash-lite-preview-09-2025')
except:
    st.error("Eroare de configurare nucleu.")

# Interfața de Logare / Creare Cont
if 'user' not in st.session_state:
    st.title("🛡️ Axternum Mobile")
    nume = st.text_input("Numele Eroului:")
    if st.button("Conectare"):
        res = supabase.table('players').select("*").eq('username', nume).execute()
        if not res.data:
            stats = {"username": nume, "level": 1, "shards": 100, "inventory": [], "hp": 100}
            supabase.table('players').insert(stats).execute()
        else:
            stats = res.data[0]
        st.session_state.user = stats
        st.rerun()
else:
    # JOCUL ACTIV
    u = st.session_state.user
    st.sidebar.title(f"👤 {u['username']}")
    st.sidebar.metric("Nivel", u['level'])
    st.sidebar.metric("Shards", u['shards'])
    st.sidebar.progress(u['hp'], text=f"HP: {u['hp']}%")

    tab1, tab2, tab3 = st.tabs(["⚔️ Luptă", "🛒 Magazin", "📜 Clasament"])

    with tab1:
        if st.button("Caută Inamic"):
            prompt = "Generează un monstru sci-fi scurt."
            inamic = model.generate_content(prompt).text
            st.info(f"A apărut: {inamic}")
            # Aici adăugăm butoanele de ATAC (logică similară cu motor.py)

    with tab2:
        st.write("Obiecte disponibile:")
        if st.button("Cumpără Sabie Plasmă (100 Shards)"):
            if u['shards'] >= 100:
                u['shards'] -= 100
                u['inventory'].append("Sabie Plasmă")
                supabase.table('players').update({"shards": u['shards'], "inventory": u['inventory']}).eq('username', u['username']).execute()
                st.success("Achiziție reușită!")
    
    with tab3:
        res = supabase.table('players').select("username, shards").order('shards', desc=True).limit(5).execute()
        st.table(res.data)

    if st.button("Deconectare"):
        del st.session_state.user
        st.rerun()