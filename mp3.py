import streamlit as st

st.title("AUthentication")

if st.button("Authenticate"):
    st.login("google")
