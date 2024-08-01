import streamlit as st
import os

def file_selector(folder_path='../..'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)

filename = file_selector()
#st.write('You selected `%s`' % filename)

st.subheader("PCAP replay speed (in pps)")
replay_speed = st.slider("What speed would you like to replay the pcap at?", 0.25, 200, 25)

