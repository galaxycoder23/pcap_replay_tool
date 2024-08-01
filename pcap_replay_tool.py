import streamlit as st
import time
import os

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
#st.write('You selected `%s`' % filename)

st.write("---")

st.subheader("PCAP replay speed (in pps)")
replay_speed = st.slider("How many packets would you like to replay per second?", 0.25, 200.0, 25.0)

st.write("---")

st.subheader("Command you are running: ")
command = "sudo tcpreplay -i eth1 -vv " + "-p " + str(replay_speed) + " " + filename
st.code(command, language="bash")

if st.button("Start PCAP replay"):
	command = "sudo tcpreplay -i eth1 " + "-p " + str(replay_speed) + " " + filename
	stream = os.popen(command)
	out = stream.read()
	st.write(out)

if st.button("Stop PCAP replay", type="primary"):
	stream2 = os.popen(signal.SIGINT)
	out2 = stream2.read()
	st.write(out2)
