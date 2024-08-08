# Imports
import streamlit as st # For the app infrastucture itself
import time # Used for the typewriter effect
from datetime import datetime # To name merged PCAP
import paramiko # SSH from Python app
from scp import SCPClient # SCP
import threading # For multi-threading
import os # For use in deleting files

st.set_page_config(
   page_title="Network traffic replay application",
   page_icon="✨"
)

st.title("Network traffic replay application")

# Subtitle and typewriter formatting
subtitle = "Replay packet captures using tcpreplay"
def stream_data():
	for character in list(subtitle):
		yield character + ""
		time.sleep(0.01)
st.write_stream(stream_data)


# Allow user to upload PCAP files
st.subheader("Upload packet captures:")

file_upload = None
filename = None
remote_path = None

# Function to display tcpreplay command to user (called further down the page)
def display_command():
	if file_uploads:
		st.subheader("Command that will be run: ")
		global replay_command 
		replay_command = "sudo -S tcpreplay -i eth1 -vv " + "-p " + str(replay_speed) + " " + remote_path
		st.code(replay_command, language="bash")

	
		
file_uploads = st.file_uploader("Upload files", type=(["pcap"]), accept_multiple_files=True, on_change=display_command)
if file_uploads:
	if len(file_uploads) == 1:
		filename = file_uploads[0].name
		with open(filename, "wb") as f: 
			for uploaded_file in file_uploads:
				f.write(uploaded_file.getvalue()) # For uploaded file as bytes
				st.download_button("Download PCAP", uploaded_file.getvalue(), file_name=filename, mime="application/vnd.tcpdump.pcap")
	else:
		for uploaded_file in file_uploads:
			filename = "mergedpcap_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".pcap"
		with open(filename, "wb") as f: 
			for uploaded_file in file_uploads:
				f.write(uploaded_file.getvalue()) # For uploaded file as bytes
		with open(filename, "rb") as merged_file:
			st.download_button("Download merged PCAP", merged_file, file_name=filename, mime="application/vnd.tcpdump.pcap")
	remote_path = "~/Documents/packet_captures/" + filename

	

# Adjust replay speed
st.write("---")
st.subheader("Packet replay speed (in pps)")
replay_speed = st.slider("How many packets would you like to replay per second?", 0.0, 500.0, 100.0)
st.write("---")

display_command()
	
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
		if os.path.exists(filename):
			os.remove(filename)
		ssh.close()

if st.button("Start traffic replay"):
	replay_traffic(ssh)


# Stop replay of traffic
def stop_traffic(ssh):
	ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
	if "traffic_replay" in globals():
		ssh.exec_command(f"sudo kill {traffic_replay.get_id()}")
	if os.path.exists(filename):
		os.remove(filename)
	ssh.close()

if st.button("Stop traffic replay", type="primary"):
	stop_traffic(ssh)
