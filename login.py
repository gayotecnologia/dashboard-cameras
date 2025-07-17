# login.py
import streamlit as st

def check_login():
    # Dicionário com usuários e senhas
    users = {
        "admin": "GayoSeg25",
        "rodrigo": "sspatem",
        "jefferson": "sspatem",
    }

    # Sessão de autenticação
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("🔐 Login")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if username in users and users[username] == password:
                st.success("✅ Login bem-sucedido!")
                st.session_state.logged_in = True
            else:
                st.error("❌ Usuário ou senha inválidos.")
        st.stop()
