import streamlit as st
import time
import os
import subprocess
import paramiko
from scp import SCPClient

st.title("PCAP replay tool")
subtitle = "Replay PCAPs using tcpreplay"

def stream_data():
	for character in list(subtitle):
		yield character + ""
		time.sleep(0.02)
st.write_stream(stream_data)

st.subheader("Upload PCAP:")
file = st.file_uploader("Upload a file", type=(["pcap"]))
if file is not None:
	filename = file.name

st.write("---")

st.subheader("PCAP replay speed (in pps)")
replay_speed = st.slider("How many packets would you like to replay per second?", 0.25, 200.0, 25.0)

st.write("---")

st.subheader("Command you are running: ")
remote_path = "/packet_captures/" + filename
replay_command = "sudo tcpreplay -i eth1 -vv " + "-p " + str(replay_speed) + " " + remote_path
st.code(replay_command, language="bash")

def replayTraffic(ssh):
	global traffic_replay
	stdin, stdout, stderr = ssh.exec_command(replay_command)
	traffic_replay = stdout.channel
	
def stopTraffic(ssh):
	if "traffic_replay" in globals():  
        	ssh.exec_command(f"sudo kill {traffic_replay.get_id()}")

# SSH credentials
ssh_host = st.secrets["ip-address"]
ssh_port = 22  
ssh_user = st.secrets["username"]
ssh_password = st.secrets["password"]  

ssh = paramiko.SSHClient()  
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # what does this do
ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)

with SCPClient(ssh.get_transport()) as scp:
	scp.put(file, remote_path)
		
if st.button("Start PCAP replay"):
	replayTraffic(ssh)

if st.button("Stop PCAP replay", type="primary"):
	stopTraffic(ssh)

ssh.close()
