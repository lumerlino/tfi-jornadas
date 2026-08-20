import streamlit as st
from supabase import create_client


def obtener_cliente_supabase():

    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]

    return create_client(
        supabase_url,
        supabase_key
    )