from tempfile import NamedTemporaryFile
import streamlit as st

uploaded_file = st.file_uploader("File upload", type='pcap')
with NamedTemporaryFile(dir='.', suffix='.csv') as f:
    f.write(uploaded_file.getbuffer())
    print(f.name)
