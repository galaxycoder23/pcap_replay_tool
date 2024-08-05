# Imports
import streamlit as st # For the app infrastucture itself
import time # Used for the typewriter effect
import paramiko # SSH from Python app
from scp import SCPClient # SCP


st.title("PCAP replay tool")

subtitle = "Replay PCAPs using tcpreplay"
def stream_data():
	for character in list(subtitle):
		yield character + ""
		time.sleep(0.02)
st.write_stream(stream_data)


# Upload PCAP file
st.subheader("Upload PCAP:")
filename = None
remote_path = None

file = st.file_uploader("Upload a file", type=(["pcap"]))
if file:
	filename = file.name
	remote_path = "~/packet_captures/" + filename


# Adjust replay speed
st.write("---")
st.subheader("PCAP replay speed (in pps)")
replay_speed = st.slider("How many packets would you like to replay per second?", 0.25, 200.0, 25.0)
st.write("---")


# Display tcpreplay command to user
st.subheader("Command you are running: ")
st.write(remote_path)
replay_command = "sudo tcpreplay -i eth1 -vv " + "-p " + str(replay_speed) + " " + remote_path
st.code(replay_command, language="bash")

	
# SSH credentials
ssh_host = st.secrets["ip-address"]
ssh_port = 22  
ssh_user = st.secrets["username"]
ssh_password = st.secrets["password"]  

# SSH setup
ssh = paramiko.SSHClient()  
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically adds the hostname and new host key to the local HostKeys object, and saves it
ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)

# SCP to transfer PCAP
with SCPClient(ssh.get_transport()) as scp:
	full_local_path = st.secrets["filepath"] + filename
	scp.put(full_local_path, remote_path)
	# Example Windows filepath: "C:/Users/<username>/Downloads/<filepath>"


# Replay traffic
def replay_traffic(ssh):
	global traffic_replay
	stdin, stdout, stderr = ssh.exec_command(replay_command)
	traffic_replay = stdout.channel
if st.button("Start PCAP replay"):
	replay_traffic(ssh)

# Stop replay of traffic
def stop_traffic(ssh):
	if "traffic_replay" in globals():  
		ssh.exec_command(f"sudo kill {traffic_replay.get_id()}")
if st.button("Stop PCAP replay", type="primary"):
	stop_traffic(ssh)


ssh.close() # Closes SSH connection
