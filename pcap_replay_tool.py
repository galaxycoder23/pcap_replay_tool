# Imports
import streamlit as st # For the app infrastucture itself
import time # Used for the typewriter effect
from datetime import date # To name merged PCAP
import paramiko # SSH from Python app
from scp import SCPClient # SCP
import threading # For multi-threading
import os # For use in deleting files

st.set_page_config(
   page_title="PCAP replay tool,
   page_icon="✨",
   layout="wide",
   initial_sidebar_state="expanded",
)

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

file_upload = None
filename = None
remote_path = None
multiple_files = False

file_uploads = st.file_uploader("Upload files", type=(["pcap"]), accept_multiple_files=True, on_change(display_command))
if file_uploads:
	if len(file_uploads) == 1:
		multiple_files = False
		filename = file_upload.name
	else:
		multiple_files = True
		for uploaded_file in file_uploads:
			filename = "mergedpcap_" + now.strftime("%Y/%m/%Yd_%H:%M:%S") + ".pcap"
	remote_path = "~/Documents/packet_captures/" + filename
			


# Adjust replay speed
st.write("---")
st.subheader("PCAP replay speed (in pps)")
replay_speed = st.slider("How many packets would you like to replay per second?", 0.0, 500.0, 100.0)
st.write("---")


# Display tcpreplay command to user
def display_command():
	if file_uploads:
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
		if multiple_files = False:
			with open(filename, 'wb') as f: 
				for uploaded_file in file_uploads:
					f.write(uploaded_file.getvalue()) # For uploaded file as bytes
		else:
			with open(filename, 'wb') as f: 
				f.write(file_uploads.getvalue()) # For uploaded file as bytes
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

if st.button("Start PCAP replay"):
	replay_traffic(ssh)


# Stop replay of traffic
def stop_traffic(ssh):
	ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
	if "traffic_replay" in globals():
		ssh.exec_command(f"sudo kill {traffic_replay.get_id()}")
	if os.path.exists(filename):
		os.remove(filename)
	ssh.close()

if st.button("Stop PCAP replay", type="primary"):
	stop_traffic(ssh)
