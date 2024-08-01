import streamlit as st
import os

st.title("PCAP replay tool")
st.write_stream("Replay PCAPs")

def file_selector(folder_path='../..'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a PCAP to replay:', filenames)
    return os.path.join(folder_path, selected_filename)

st.subheader("Choose PCAP:")
filename = file_selector()
#st.write('You selected `%s`' % filename)

st.subheader("PCAP replay speed (in pps)")
replay_speed = st.slider("How many packets would you like to replay per second?", 0.25, 200.0, 25.0)

# Optional code ----------------------------------------------------
st.subheader("Command you are running: ")
command = "sudo tcpreplay -i eth1 " + "-p " + str(replay_speed) + " " + filename
st.code(command, language="bash")

# ------------------------------------------------------------------


if st.button("Start PCAP replay"):
	command = "sudo tcpreplay -i eth1 " + "-p " + str(replay_speed) + " " + filename
	stream = os.popen(command)
	out = stream.read()
	st.write(out)

if st.button("Stop PCAP replay", type="primary"):
	command = "exit"
	stream = os.popen(command)
	out = stream.read()
	st.write(out)
