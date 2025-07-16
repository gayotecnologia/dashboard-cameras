import streamlit as st

def check_login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")

    if username == "romilson" and password == "1234":
        return True
    else:
        if username or password:
            st.sidebar.error("Usuário ou senha inválidos")
        return False
