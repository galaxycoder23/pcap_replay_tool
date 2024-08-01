import streamlit as st
import os

def file_selector(folder_path='../..'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a PCAP to upload:', filenames)
    return os.path.join(folder_path, selected_filename)

filename = file_selector()
#st.write('You selected `%s`' % filename)

st.subheader("PCAP replay speed (in pps)")
replay_speed = st.slider("How many packets would you like to replay per second?", 0.25, 200.0, 25.0)

command = "sudo tcpreplay -i eth1 " + "-p " + replay_speed + " " + filename

