import streamlit as st
import time
import os
import subprocess

st.title("PCAP replay tool")
subtitle = "Replay PCAPs using tcpreplay"
def stream_data():
    for character in list(subtitle):
        yield character + ""
        time.sleep(0.02)
st.write_stream(stream_data)

def file_selector(folder_path='../..'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a PCAP to replay:', filenames)
    return os.path.join(folder_path, selected_filename)

st.subheader("Choose PCAP:")
filename = file_selector()

st.write("---")

st.subheader("PCAP replay speed (in pps)")
replay_speed = st.slider("How many packets would you like to replay per second?", 0.25, 200.0, 25.0)

st.write("---")

st.subheader("Command you are running: ")
command = "sudo tcpreplay -i eth1 -vv " + "-p " + str(replay_speed) + " " + filename
st.code(command, language="bash")
	
def replayTraffic():
	global traffic_replay
	traffic_replay = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
if st.button("Start PCAP replay"):
	replayTraffic(command)

if st.button("Stop PCAP replay", type="primary"):
	os.kill(out.pid, signal.SIGINT)
	if 'process' in globals():  
        	os.kill(process.pid, signal.SIGINT)  
