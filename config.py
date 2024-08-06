import streamlit as st

class Config:
    def __init__(self):
        self.hugging_face_api_key = st.secrets["hugging_face_api_key"]
        self.hugging_face_model_api_endpoint = st.secrets["hugging_face_model_api_endpoint"]
        self.openai_api_key = st.secrets["OPENAI_API_KEY"]
config = Config()
