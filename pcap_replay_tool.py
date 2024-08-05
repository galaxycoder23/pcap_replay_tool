# Imports
import streamlit as st # For the app infrastucture itself
import time # Used for the typewriter effect
import paramiko # SSH from Python app
from scp import SCPClient # SCP
import threading # For multi-threading

st.title("PCAP replay tool")

# Subtitle and typewriter formatting
subtitle = "Replay PCAPs using tcpreplay"
def stream_data():
	for character in list(subtitle):
		yield character + ""
		time.sleep(0.02)
st.write_stream(stream_data)


# Allow user to upload PCAP file
st.subheader("Upload PCAP:")
filename = None
remote_path = None

file_upload = st.file_uploader("Upload a file", type=(["pcap"]))
if file_upload:
	with open(filename, 'wb') as f: 
		f.write(file_upload)
	remote_path = "~/packet_captures/" + filename


# Adjust replay speed
st.write("---")
st.subheader("PCAP replay speed (in pps)")
replay_speed = st.slider("How many packets would you like to replay per second?", 0.0, 2000.0, 500.0)
st.write("---")


# Display tcpreplay command to user
st.subheader("Command you are running: ")
replay_command = "sudo -S tcpreplay -i eth1 -vv " + "-p " + str(replay_speed) + " " + remote_path
st.code(replay_command, language="bash")

	
# SSH credentials
ssh_host = st.secrets["ip-address"]
ssh_port = 22  
ssh_user = st.secrets["username"]
ssh_password = st.secrets["password"]  

# SSH setup
ssh = paramiko.SSHClient()  
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically adds the hostname and new host key to the local HostKeys object, and saves it

def print_stream(stream, identifier):  
	for line in iter(stream.readline, ''):  
	if line:
		print(f"{identifier}: {line.strip()}")
	else:  
    break

# SCP to transfer PCAP
def upload_file_to_remote(local_file, remote_directory):
	with SCPClient(ssh.get_transport()) as scp:
		scp.put(local_file, remote_directory)

# Replay traffic
def replay_traffic(ssh):
	try:
		ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
		upload_file_to_remote(filename, remote_path)
		global traffic_replay
		stdin, stdout, stderr = ssh.exec_command(replay_command)
		stdin.write(st.secrets["password"]+"\n")
		stdin.flush()
                
		# Create threads to read stdout and stderr  
		stdout_thread = threading.Thread(target=print_stream, args=(stdout, "STDOUT"))
		stderr_thread = threading.Thread(target=print_stream, args=(stderr, "STDERR"))  
          
		# Start the threads  
		stdout_thread.start()
		stderr_thread.start()
		
		# Wait for the threads to complete
		stdout_thread.join()
		stderr_thread.join()
		
		traffic_replay = stdout.channel
	finally:
		ssh.close()

if st.button("Start PCAP replay"):
	replay_traffic(ssh)


# Stop replay of traffic
def stop_traffic(ssh):
	ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
	if "traffic_replay" in globals():
		ssh.exec_command(f"sudo kill {traffic_replay.get_id()}")
	ssh.close()

if st.button("Stop PCAP replay", type="primary"):
	stop_traffic(ssh)
