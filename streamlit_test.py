import streamlit as st
    
f = st.file_uploader("Upload a file", type=(["pcap"]))
if f is not None:
	path_in = f.name
	print(path_in)
else:
  path_in = None
